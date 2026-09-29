#!/usr/bin/env python3
"""
Guard against committing a half-written artifact from a live producer.

Why this exists: at commit e278a344 a producer's raw-result.json was committed
while it was still being written. It was empty, `check_merge_hygiene.py`
correctly rejected it as unparseable, and CI went red on
PR #504 -- a failure caused entirely by the durability-commit pattern, not by
any research defect.

The session Stop hook requires a clean tree, and producers write continuously,
so "just don't commit mid-write files" is not available. What IS available is to
check parseability first and defer only the files that are not yet valid.

    python3 wip_parse_guard.py            # report unparseable changed/untracked files
    python3 wip_parse_guard.py --exclude  # additionally defer them via .git/info/exclude

Deferral is LOCAL ONLY (.git/info/exclude): nothing is committed, no repository
configuration changes, and the entry is removed once the file parses.

The managed entries live inside a MARKED BLOCK and this script touches nothing
outside it. That is not decoration: the first version of this script rewrote the
whole exclude file and silently deleted a hand-written entry that was holding
back a 108 MB artifact, which then got committed and the push was rejected by
GH001. A tool that cleans up other people's lines is a tool that loses them.
"""
import argparse
import json
import os
import subprocess
import sys

import yaml

REPO = subprocess.check_output(
    ['git', 'rev-parse', '--show-toplevel']).decode().strip()
EXCLUDE = os.path.join(REPO, '.git', 'info', 'exclude')


def candidate_files():
    out = subprocess.check_output(
        ['git', 'status', '--porcelain', '--untracked-files=all'],
        cwd=REPO).decode().splitlines()
    return [line[3:] for line in out if line[3:].endswith(('.json', '.yaml', '.yml'))]


def parses(path):
    full = os.path.join(REPO, path)
    if not os.path.exists(full) or os.path.getsize(full) == 0:
        return False, 'empty or missing'
    try:
        with open(full) as fh:
            json.load(fh) if path.endswith('.json') else yaml.safe_load(fh)
        return True, ''
    except Exception as exc:
        return False, str(exc)[:80]


BEGIN = '# >>> wip_parse_guard managed block >>>'
END = '# <<< wip_parse_guard managed block <<<'


def read_exclude():
    if not os.path.exists(EXCLUDE):
        return []
    return open(EXCLUDE).read().splitlines()


def split_managed(lines):
    """Return (before, managed, after). Only `managed` is ever rewritten."""
    if BEGIN in lines and END in lines:
        i, j = lines.index(BEGIN), lines.index(END)
        return lines[:i], lines[i + 1:j], lines[j + 1:]
    return lines, [], []


def write_exclude(before, managed, after):
    body = list(before)
    if managed:
        body += [BEGIN] + managed + [END]
    body += after
    with open(EXCLUDE, 'w') as fh:
        fh.write('\n'.join(body).rstrip('\n') + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--exclude', action='store_true',
                    help='defer unparseable files via .git/info/exclude (local only)')
    args = ap.parse_args()

    bad = []
    for path in candidate_files():
        ok, why = parses(path)
        if not ok:
            bad.append((path, why))
    still_bad = {p for p, _ in bad}

    if args.exclude:
        before, managed, after = split_managed(read_exclude())
        # Only ever drop entries THIS script added, and only once they parse.
        managed = [ln for ln in managed if ln in still_bad]
        for path in sorted(still_bad):
            if path not in managed:
                managed.append(path)
        write_exclude(before, managed, after)

    if bad:
        print('UNPARSEABLE (not safe to commit yet):')
        for path, why in bad:
            print('  - %s: %s' % (path, why))
        if args.exclude:
            print('deferred locally in the managed block; they return once they parse')
    else:
        print('all changed/untracked JSON and YAML parse; safe to commit')
    return 0


if __name__ == '__main__':
    sys.exit(main())
