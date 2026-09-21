#!/usr/bin/env python3
"""
FROZEN CONSTANTS ARE READ, NEVER WRITTEN.

EXP-ECQ-0e0cbb `constants_are_read_never_written` forbids any frontier or
benchmark value appearing as a literal in the protocol, in code, or in a
comparison.  So this module contains NO numeric literal for either value.

Both quantities are obtained twice and cross-checked:

  * the LIVE value, read at run time from the frozen file
      - r >= 12 cell        : frontier_20260823.json, threshold 12,
                              min_naive_height.value
      - class benchmark     : icarm_database_20260823.json, curve id 1,
                              naive_height
  * the AUDIT value, PARSED OUT OF ledger/hypotheses/H-ECQ-0ed5c8.yaml
    (`target_cell_predeclared.audit_value_do_not_hard_code` and
    `intermediate_benchmark.audit_value_do_not_hard_code`).

`assert_frozen_constants()` ABORTS THE RUN if the two disagree.  Because the
audit value is parsed from the hypothesis record rather than typed here, no
transcription and no rounding is possible in this file: the rounding defect
validator F7 caught in BATCH-541940 cannot recur through this path.
"""
import hashlib
import json
import os

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    *([os.pardir] * 8)))
FRONTIER = os.path.join(ROOT, 'coordination/goals/GOAL-ECQ-002/baseline/'
                              'frontier_20260823.json')
SNAPSHOT = os.path.join(ROOT, 'coordination/goals/GOAL-ECQ-002/baseline/'
                              'icarm_database_20260823.json')
HYPOTHESIS = os.path.join(ROOT, 'ledger/hypotheses/H-ECQ-0ed5c8.yaml')

CELL_RANK_THRESHOLD = 12
BENCHMARK_BOARD_ID = 1


class FrozenConstantMismatch(RuntimeError):
    """Raised when a read value differs from the record's audit value."""


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def _hypothesis():
    with open(HYPOTHESIS) as fh:
        return yaml.safe_load(fh)['hypothesis']


def read_cell():
    """The frozen r >= 12 naive-height cell, read at run time."""
    with open(FRONTIER) as fh:
        fr = json.load(fh)
    e = fr['frontier_by_rank_threshold'][str(CELL_RANK_THRESHOLD)]
    return {
        'path': os.path.relpath(FRONTIER, ROOT),
        'sha256_read_at_run_time': sha256(FRONTIER),
        'rank_threshold': CELL_RANK_THRESHOLD,
        'min_naive_height': e['min_naive_height']['value'],
        'curve_id': e['min_naive_height']['curve_id'],
        'submitter': e['min_naive_height']['submitter'],
        'n_curves_at_or_above': e['n_curves_at_or_above'],
    }


def read_benchmark():
    """The construction-class benchmark (board entry id 1), read at run time."""
    with open(SNAPSHOT) as fh:
        db = json.load(fh)
    rows = [c for c in db['curves'] if c['id'] == BENCHMARK_BOARD_ID]
    if len(rows) != 1:
        raise FrozenConstantMismatch(
            'expected exactly one board entry with id %d, found %d'
            % (BENCHMARK_BOARD_ID, len(rows)))
    c = rows[0]
    return {
        'path': os.path.relpath(SNAPSHOT, ROOT),
        'sha256_read_at_run_time': sha256(SNAPSHOT),
        'board_id': c['id'],
        'curve_key': c['curve_key'],
        'ainvs': c['ainvs'],
        'rank_lower_bound': c['rank_lower_bound'],
        'naive_height': c['naive_height'],
    }


def assert_frozen_constants():
    """Read both constants and ABORT if either differs from its audit value.

    Returns the assertion record for the run manifest.  Raises
    FrozenConstantMismatch otherwise -- the run must not continue.
    """
    h = _hypothesis()
    audit_cell = h['target_cell_predeclared']['audit_value_do_not_hard_code']
    audit_bench = h['intermediate_benchmark']['audit_value_do_not_hard_code']
    audit_sha = h['target_cell_predeclared']['frozen_snapshot_sha256']

    cell = read_cell()
    bench = read_benchmark()
    with open(SNAPSHOT) as fh:
        snap_sha_field = json.load(fh)
    snap_sha = sha256(SNAPSHOT)

    checks = [
        ('cell_min_naive_height', cell['min_naive_height'], audit_cell),
        ('benchmark_naive_height', bench['naive_height'], audit_bench),
        ('frozen_snapshot_sha256', snap_sha, audit_sha),
    ]
    failures = [{'what': w, 'read': r, 'audit': a}
                for w, r, a in checks if r != a]
    rec = {
        'assertion': 'read value == audit value in ledger/hypotheses/'
                     'H-ECQ-0ed5c8.yaml; ABORT ON MISMATCH',
        'audit_values_parsed_from': os.path.relpath(HYPOTHESIS, ROOT),
        'audit_values_are_not_literals_in_this_code': True,
        'checks_performed': [w for w, _, _ in checks],
        'n_checks': len(checks),
        'exercised': True,
        'all_match': not failures,
        'failures': failures,
        'cell': cell,
        'benchmark': bench,
        'snapshot_curve_count': len(snap_sha_field['curves']),
    }
    if failures:
        raise FrozenConstantMismatch(json.dumps(failures))
    return rec


def board_index():
    """The frozen snapshot indexed BOTH ways: by curve_key and by a-invariants.

    Both keys, because BATCH-541940 reported board curve id 108 as its own.
    """
    with open(SNAPSHOT) as fh:
        db = json.load(fh)
    by_key, by_ainvs = {}, {}
    for c in db['curves']:
        by_key[str(c['curve_key'])] = c
        by_ainvs[tuple(int(a) for a in c['ainvs'])] = c
    return by_key, by_ainvs


if __name__ == '__main__':
    print(json.dumps(assert_frozen_constants(), indent=1))
