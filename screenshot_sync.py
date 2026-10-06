#!/usr/bin/env python3
"""Capture a screenshot of your own screen and sync it to this GitHub repo.

This is a personal tool: run it yourself on a computer you own, whenever you
want to share your current screen with your other computer. It takes one
screenshot, saves it under ./screenshots, and (unless you pass --no-push)
commits and pushes it to the repo. On your other machine, run `git pull`
to receive the new screenshots.

Usage:
    python screenshot_sync.py              # take one screenshot and push it
    python screenshot_sync.py --no-push    # just save locally, don't push
    python screenshot_sync.py --pull       # fetch screenshots from the repo

Setup:
    pip install mss
"""

import argparse
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
SHOTS_DIR = REPO_DIR / "screenshots"


def git(*args):
    """Run a git command inside the repo. Returns (ok, stdout)."""
    result = subprocess.run(
        ["git", *args], cwd=REPO_DIR, capture_output=True, text=True
    )
    if result.returncode != 0:
        sys.stderr.write(f"git {' '.join(args)} failed:\n{result.stderr.strip()}\n")
    return result.returncode == 0, result.stdout.strip()


def take_screenshot():
    """Grab the current screen and save it to ./screenshots. Returns the path."""
    try:
        import mss
        import mss.tools
    except ImportError:
        sys.exit("Missing dependency. Install it with:  pip install mss")

    SHOTS_DIR.mkdir(exist_ok=True)
    host = socket.gethostname()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = SHOTS_DIR / f"{host}_{stamp}.png"

    with mss.mss() as sct:
        # Monitor 0 is the full virtual screen (all displays combined).
        screenshot = sct.grab(sct.monitors[0])
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(out_path))

    print(f"Saved {out_path}")
    return out_path


def push(path):
    """Commit the new screenshot and push it to the repo's remote."""
    rel = path.relative_to(REPO_DIR)
    ok, _ = git("add", str(rel))
    if not ok:
        return
    ok, _ = git("commit", "-m", f"Add screenshot {rel.name}")
    if not ok:
        return
    branch_ok, branch = git("rev-parse", "--abbrev-ref", "HEAD")
    branch = branch if branch_ok and branch else "HEAD"
    if git("push", "origin", branch)[0]:
        print(f"Pushed to origin/{branch}")


def pull():
    """Fetch the latest screenshots from the remote onto the current branch."""
    branch_ok, branch = git("rev-parse", "--abbrev-ref", "HEAD")
    branch = branch if branch_ok and branch else "HEAD"
    if git("pull", "origin", branch)[0]:
        print(f"Pulled latest screenshots into {SHOTS_DIR}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-push", action="store_true", help="save locally only, do not push"
    )
    parser.add_argument(
        "--pull", action="store_true", help="fetch screenshots from the repo and exit"
    )
    args = parser.parse_args()

    if args.pull:
        pull()
        return

    path = take_screenshot()
    if not args.no_push:
        push(path)


if __name__ == "__main__":
    main()
