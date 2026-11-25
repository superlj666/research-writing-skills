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

SOURCE = "https://github.com/superlj666/research-writing-skills.git"
SKILLS = ("3w2h", "thesis-logic")


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


def synchronize(args, state_dir):
    ledger = state_dir / "state.json"
    if ledger.exists():
        records = json.loads(ledger.read_text())
        if records["source"] != args.source:
            raise ValueError("The saved state belongs to another source repository.")
    else:
        records = {"source": args.source, "installed": {}}

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
            if installed.get(skill) != new_sha:
                installed[skill] = new_sha
                replace_file(ledger, (json.dumps(records, indent=2) + "\n").encode())
        unresolved |= status != "up to date" and status != "updated"
        print(f"{skill}: {status}")
    return 2 if unresolved else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without updating any file.")
    parser.add_argument("--codex-home", type=Path,
                        default=Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex"))
    parser.add_argument("--source", default=SOURCE, help=argparse.SUPPRESS)
    args = parser.parse_args()
    state_dir = args.codex_home / "research-writing-skills"
    if args.check:
        return synchronize(args, state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    with (state_dir / "sync.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return synchronize(args, state_dir)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        detail = error.stderr.decode(errors="replace").strip() if isinstance(
            error, subprocess.CalledProcessError) else str(error)
        print(f"Skill sync failed: {detail}", file=sys.stderr)
        sys.exit(1)
