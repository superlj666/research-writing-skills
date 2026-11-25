#!/usr/bin/env python3
"""Sync the two repository skills without overwriting local edits."""

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

SOURCE = "https://github.com/superlj666/research-writing-skills.git"
SKILLS = ("3w2h", "thesis-logic")
CHECK_INTERVAL_SECONDS = 48 * 60 * 60


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.run(
        ["git", *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "/usr/bin/false"},
        timeout=120,
    ).stdout


def load_upstream(source):
    with tempfile.TemporaryDirectory(prefix="research-skills-fetch-") as directory:
        git("init", "--bare", "--quiet", directory)
        git("-C", directory, "fetch", "--quiet", "--no-tags", "--depth=1",
            source, "refs/heads/main")
        revision = git("-C", directory, "rev-parse", "FETCH_HEAD").decode().strip()
        files = {
            skill: git("-C", directory, "show", f"{revision}:skills/{skill}/SKILL.md")
            for skill in SKILLS
        }
    return revision, files


def replace_file(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".sync-", delete=False) as stream:
        temp = Path(stream.name)
        try:
            stream.write(data)
            stream.close()
            temp.chmod(0o644)
            temp.replace(path)
        finally:
            if temp.exists():
                temp.unlink()


def classify(path, upstream_sha, last_sha):
    if path.is_symlink() or path.parent.is_symlink():
        return "local override"
    if not path.exists():
        return "missing"
    current_sha = sha256(path.read_bytes())
    if current_sha == upstream_sha:
        return "up to date"
    if current_sha == last_sha:
        return "update available"
    return "local override"


def load_state(ledger, source):
    if not ledger.exists():
        return {"source": source, "installed": {}}
    records = json.loads(ledger.read_text())
    if records["source"] != source:
        raise ValueError("The saved state belongs to another source repository.")
    return records


def recently_checked(records):
    age = time.time() - records.get("last_checked_at", 0)
    return 0 <= age <= CHECK_INTERVAL_SECONDS


def skip_recent_check(args, ledger):
    if args.if_stale and recently_checked(load_state(ledger, args.source)):
        print("Skipped: GitHub was checked within the last 48 hours.")
        return True
    return False


def synchronize(args, ledger):
    records = load_state(ledger, args.source)
    revision, upstream = load_upstream(args.source)
    print(f"GitHub main {revision}")
    unresolved = False
    for skill, data in upstream.items():
        path = args.codex_home / "skills" / skill / "SKILL.md"
        new_sha = sha256(data)
        installed = records["installed"]
        status = classify(path, new_sha, installed.get(skill))
        if status == "update available" and not args.check:
            replace_file(path, data)
            status = "updated"
        if status in ("up to date", "updated") and not args.check:
            installed[skill] = new_sha
        unresolved |= status != "up to date" and status != "updated"
        print(f"{skill}: {status}")
    records["last_checked_at"] = time.time()
    replace_file(ledger, (json.dumps(records, indent=2) + "\n").encode())
    return 2 if unresolved else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without updating skill files.")
    parser.add_argument("--if-stale", action="store_true",
                        help="Skip GitHub if successfully checked in the last 48 hours.")
    parser.add_argument("--codex-home", type=Path,
                        default=Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex"))
    parser.add_argument("--source", default=SOURCE, help=argparse.SUPPRESS)
    args = parser.parse_args()
    state_dir = args.codex_home / "research-writing-skills"
    ledger = state_dir / "state.json"
    if skip_recent_check(args, ledger):
        return 0
    state_dir.mkdir(parents=True, exist_ok=True)
    with (state_dir / "sync.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if skip_recent_check(args, ledger):
            return 0
        return synchronize(args, ledger)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        detail = error.stderr.decode(errors="replace").strip() if isinstance(
            error, subprocess.CalledProcessError) else str(error)
        print(f"Skill sync failed: {detail}", file=sys.stderr)
        sys.exit(1)
