#!/usr/bin/env python3
"""Create GIT_INFO.json with git metadata for submission tracking."""

import json
import subprocess
import sys


def git_cmd(args: list[str]) -> str:
    """Run a git command and return output, or empty string on failure."""
    try:
        return subprocess.check_output(
            ['git'] + args,
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ''


def main():
    """Generate GIT_INFO.json in the current directory."""
    info = {
        'commit': git_cmd(['rev-parse', 'HEAD']),
        'commit_short': git_cmd(['rev-parse', '--short', 'HEAD']),
        'message': git_cmd(['log', '-1', '--pretty=%B']).split('\n')[0],
        'branch': git_cmd(['rev-parse', '--abbrev-ref', 'HEAD']),
        'tag': git_cmd(['describe', '--tags', '--exact-match']),
        'remote_url': git_cmd(['remote', 'get-url', 'origin']),
        'author': git_cmd(['log', '-1', '--pretty=%an']),
        'author_email': git_cmd(['log', '-1', '--pretty=%ae']),
        'commit_timestamp': git_cmd(['log', '-1', '--pretty=%aI'])
    }

    with open('GIT_INFO.json', 'w') as f:
        json.dump(info, f, indent=2)

    print("GIT_INFO.json created:")
    print(json.dumps(info, indent=2))


if __name__ == '__main__':
    main()

