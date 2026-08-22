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


def read_exclude():
    if not os.path.exists(EXCLUDE):
        return []
    return open(EXCLUDE).read().splitlines()


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

    # Drop stale deferrals: anything that now parses should come back.
    lines = read_exclude()
    still_bad = {p for p, _ in bad}
    kept = [ln for ln in lines
            if not (ln.startswith('coordination/') and ln.endswith(('.json', '.yaml', '.yml'))
                    and ln not in still_bad)]
    if args.exclude:
        for path, _ in bad:
            if path not in kept:
                kept.append(path)
        if kept != lines:
            with open(EXCLUDE, 'w') as fh:
                fh.write('\n'.join(kept) + '\n')

    if bad:
        print('UNPARSEABLE (not safe to commit yet):')
        for path, why in bad:
            print('  - %s: %s' % (path, why))
        if args.exclude:
            print('deferred locally via .git/info/exclude; they return once they parse')
    else:
        print('all changed/untracked JSON and YAML parse; safe to commit')
    return 0


if __name__ == '__main__':
    sys.exit(main())
