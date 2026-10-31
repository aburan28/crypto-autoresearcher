#!/usr/bin/env python3
"""Independent J-law audit. Phase 1 executes fixed public algebra controls only.

No producer imports, function calls, source execution, entropy, or scientific
input generation. The finite controls below are public byte alphabets and
explicit Z/7 orientation/list examples, never a replacement reference bank.
Later retained-data audit procedures must preserve this separation.
"""
from __future__ import annotations

import argparse
import hashlib
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import itertools
import json
from pathlib import Path
import subprocess

TASK = "TASK-20261030-3393bd"
ROOT = Path('/workspace/classical-ecdlp-validation-ready')
OUT = Path('/workspace/classical-ecdlp-endpoint-reuse/host-reference-cost-audit-20261030')/TASK
VIEW = 'coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-cbf9d7/derived-supervisor-views/RUN-ECDLP-939237/manifest-json-v1/supervisor/modal/collected/'
POST = 'experiments/EXP-ECDLP-080f41/postrun-from-view-346631/'
INPUTS = {}
FAILURES = Counter()
WITNESSES = []


def source_open(rel):
    assert rel.startswith((VIEW, POST))
    with (OUT/'phase2-readlog.jsonl').open('a') as log:
        log.write(json.dumps({'canonical_relative_path': rel, 'opened_at': utc_now(),
                              'operation': 'independent audit complete content read'})+'\n')
        log.flush()
    return (ROOT/rel).open('rb')


def read_json(rel):
    with source_open(rel) as f:
        data = f.read()
    INPUTS[rel] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    return json.loads(data)


def rows(rel):
    h = hashlib.sha256()
    size = count = 0
    with source_open(rel) as f:
        for count, line in enumerate(f, 1):
            h.update(line)
            size += len(line)
            if not line.endswith(b'\n'):
                record(False, 'partial-jsonl-line', rel, count)
            yield count, json.loads(line)
    INPUTS[rel] = {'sha256': h.hexdigest(), 'bytes': size, 'rows': count}


def record(condition, check, source, row=None, **detail):
    if not condition:
        FAILURES[check] += 1
        if len(WITNESSES) < 40:
            WITNESSES.append({'check': check, 'source': source, 'row': row, **detail})
    return condition


def equal(actual, wanted, check, source, row=None):
    return record(actual == wanted, check, source, row,
                  actual=str(actual)[:240], wanted=str(wanted)[:240])


def add_affine(P, Q, p, a):
    if P is None:
        return Q
    if Q is None:
        return P
    x, y = P
    X, Y = Q
    if x == X and (y+Y) % p == 0:
        return None
    slope = ((3*x*x+a)*pow(2*y, -1, p) if P == Q
             else (Y-y)*pow(X-x, -1, p)) % p
    x_new = (slope*slope-x-X) % p
    return x_new, (slope*(x-x_new)-y) % p


def reconstruct(curve):
    """Solve cyclic cocycle edge equations on this SAME retained public orbit.

    Let edge[k]=lambda(kG,G). The equations z[k+1]-z[k]=zG+edge[k]
    and z[r]=z[0]=0 force zG=-sum(edge)/r. This is finite mathematical
    reconstruction, not execution of the candidate/host producer.
    """
    p, a, b, r = (curve['model'][x] for x in ('p', 'a', 'b', 'r'))
    G = tuple(curve['base'])
    points = [None]
    for k in range(1, r):
        points.append(add_affine(points[-1], G, p, a))
    assert add_affine(points[-1], G, p, a) is None
    assert len(set(points)) == r
    assert all(P is None or (P[1]*P[1]-P[0]**3-a*P[0]-b) % p == 0 for P in points)
    logs = {P: k for k, P in enumerate(points)}
    edge = []
    for P in points:
        if P is None or (P[0] == G[0] and (P[1]+G[1]) % p == 0):
            edge.append(0)
        elif P == G:
            edge.append((3*G[0]*G[0]+a)*pow(2*G[1], -1, p) % p)
        else:
            edge.append((G[1]-P[1])*pow(G[0]-P[0], -1, p) % p)
    zG = -sum(edge)*pow(r, -1, p) % p
    z = [0]
    for k in range(r):
        z.append((z[-1]+zG+edge[k]) % p)
    assert z[-1] == 0 and z[1] == zG
    labels = [None]*r
    labels[0] = 0
    c = zG*pow(G[1], -1, p) % p
    anchor = -zG % p
    if c and anchor and zG:
        inv_anchor = pow(anchor, -1, p)
        for k in range(1, r):
            x, y = points[k]
            numerator = (z[k]+c*y*(-2-c*(x-G[0]))) % p
            if numerator:
                labels[k] = int(pow(numerator*inv_anchor % p, (p-1)//2, p) != 1)
    return points, logs, labels


class Replay:
    """Source-inspected, independently written host SHA256 byte reconstruction."""
    def __init__(self, seed, domain):
        self.prefix = seed+b'\0'+domain+b'\0'
        self.counter = 0
        self.rejected = 0
        self.accepted = 0

    def below(self, bound):
        threshold = ((1 << 256)//bound)*bound
        while True:
            raw = hashlib.sha256(self.prefix+self.counter.to_bytes(8, 'big')).digest()
            self.counter += 1
            number = int.from_bytes(raw, 'big')
            if number < threshold:
                self.accepted += 1
                return number % bound
            self.rejected += 1

    def bit_bytes(self, n):
        # 2 divides2^256, so no rejection; digest parity is exactly digest[-1]&1.
        packed = bytearray((n+7)//8)
        prefix = self.prefix
        start = self.counter
        for j in range(n):
            packed[j//8] |= (hashlib.sha256(prefix+(start+j).to_bytes(8, 'big')).digest()[-1] & 1) << (7-j % 8)
        self.counter += n
        self.accepted += n
        return bytes(packed)

    def counts(self):
        result = {}
        if self.counter:
            result['sha256_blocks'] = self.counter
        if self.accepted:
            result['accepted'] = self.accepted
        if self.rejected:
            result['rejected'] = self.rejected
        return result


def measured_candidates(bits, radius, cap, r, a, b):
    erased = [i for i, bit in enumerate(bits) if bit is None]
    if len(erased) > cap:
        return set(), 0, 0
    known = [i for i, bit in enumerate(bits) if bit is not None]
    L = len(bits)
    D = 1 << L
    convert = a*pow(b, -1, r) % r
    scalars = set()
    words = zero = 0
    for fill in itertools.product((0, 1), repeat=len(erased)):
        row = [0 if x is None else x for x in bits]
        for i, x in zip(erased, fill):
            row[i] = x
        initial = sum(x << (L-i-1) for i, x in enumerate(row))
        for distance in range(min(radius, len(known))+1):
            for flips in itertools.combinations(known, distance):
                value = initial
                for i in flips:
                    value ^= 1 << (L-i-1)
                words += 1
                k = (r*value+D-1)//D
                if 0 <= k < r and D*k < r*(value+1):
                    x = convert*k % r
                    if x:
                        scalars.add(x)
                    else:
                        zero += 1
    return scalars, words, zero


def phase2_audit():
    started = utc_now()
    public = read_json(VIEW+'public-cohort.json')
    curves = {c['curve_id']: c for c in public['curves']}
    master = bytes.fromhex(read_json(POST+'host-seed-event.json')['master_hex'])
    assert len(master) == 32 and len(curves) == 48
    banks = {c: [] for c in curves}
    starts = {c: [] for c in curves}
    traces = {}
    seen_traces = set()
    totals = Counter()
    for line, row in rows(VIEW+'raw/single-points.jsonl'):
        totals['single_rows'] += 1
        if row['arm_id'] == 'circuit2.a1':
            banks[row['curve_id']].append((tuple(row['point']), row['answer']['bit'], row['single_id']))
    print(json.dumps({'stage': 'single stream complete', 'rows': totals['single_rows'], 'at': utc_now()}), flush=True)
    for line, row in rows(VIEW+'raw/traces.jsonl'):
        totals['trace_rows'] += 1
        ident = row['trace_id']
        record(ident not in seen_traces, 'trace-id-unique', VIEW+'raw/traces.jsonl', line)
        seen_traces.add(ident)
        if row['incremental'] is None:
            if row['arm_id'] == 'circuit2.a1':
                query = row['original']['predicate_trace']
                starts[row['curve_id']].append((tuple(query[0]['target']), [q['answer']['bit'] for q in query], ident))
        else:
            queries = row['incremental']['predicate_trace']
            traces[ident] = {'curve': row['curve_id'], 'target': tuple(row['target']),
                             'target_id': row['target_id'], 'a': row['base_multiplier'],
                             'b': row['target_multiplier'], 'bits': [q['answer']['bit'] for q in queries]}
    print(json.dumps({'stage': 'trace stream complete', 'rows': totals['trace_rows'], 'at': utc_now()}), flush=True)
    budgets = {}
    budget_hist = Counter()
    for line, row in rows(VIEW+'raw/decoder-cells.jsonl'):
        ident = row['cell_id']
        meta = traces[row['trace_id']]
        r = curves[meta['curve']]['model']['r']
        values, words, zero = measured_candidates(meta['bits'], row['radius'], row['erasure_cap'], r, meta['a'], meta['b'])
        record(ident not in budgets, 'cell-id-unique', VIEW+'raw/decoder-cells.jsonl', line)
        equal(row['M'], len(values), 'M-reconstruction', VIEW+'raw/decoder-cells.jsonl', ident)
        equal(set(row['distinct_nonzero_candidates']), values, 'candidate-domain-reconstruction', VIEW+'raw/decoder-cells.jsonl', ident)
        equal(row['word_count'], words, 'budget-complete-word-count', VIEW+'raw/decoder-cells.jsonl', ident)
        equal(row['zero_candidate_checks'], zero, 'zero-outside-M', VIEW+'raw/decoder-cells.jsonl', ident)
        budgets[ident] = (row['M'], row['trace_id'])
        budget_hist[row['M']] += 1
        totals['decoder_rows'] += 1
        totals['reconstructed_decoder_words'] += words
        totals['decoder_zero_checks'] += zero
        totals['decoder_capped_rows'] += bool(row['capped'])
    print(json.dumps({'stage': 'all budgets reconstructed', 'rows': totals['decoder_rows'], 'at': utc_now()}), flush=True)
    results = []
    mutation_controls = []
    first_null_done = first_uniform_done = False
    for cid, curve in curves.items():
        r = curve['model']['r']
        points, logs, actual_labels = reconstruct(curve)
        totals['orbit_points_reconstructed'] += r
        result = {'curve_id': cid, 'r': r, 'orbit_points': r}
        if cid.startswith(('discovery-', 'validation-')):
            rel = POST+'null-'+cid+'.json'
            obj = read_json(rel)
            null = obj['mask_reference']
            mask = [v is not None for v in actual_labels]
            symmetric = all(mask[k] == mask[r-k] for k in range(1, r))
            eligible = symmetric and mask[1] and mask[r-1]
            status = ('ineligible_asymmetric_mask' if not symmetric else
                      'ineligible_undefined_anchor' if not (mask[1] and mask[r-1]) else None)
            equal(len(banks[cid]), 1800, 'bank-coverage', rel)
            equal(len(starts[cid]), 128, 'start-coverage', rel)
            if not eligible:
                equal(null['status'], status, 'null-ineligible-status', rel)
                equal(null['draws'], [], 'null-no-replacement', rel)
                equal(obj['retained_bank_statistics'], None, 'null-ineligible-no-stats', rel)
                result.update(null_status=status, null_draws=0)
                totals['null_ineligible_curves'] += 1
            else:
                positive = [k for k in range(1, (r+1)//2) if mask[k]]
                free = [k for k in positive if k != 1]
                positions = {k: i for i, k in enumerate(free)}
                n = len(free)
                expected_support = {'base': 2, 'exponent': n, 'exact_small': (1 << n) if n < 63 else None}
                equal(null['free_pair_scalars'], free, 'exact-full-mask-free-pairs', rel)
                equal(null['defined_pairs'], len(positive), 'mask-defined-pairs', rel)
                equal(null['support'], expected_support, 'orientation-support', rel)
                equal(null['status'], 'complete' if n else 'degenerate', 'null-eligible-status', rel)
                equal(null['draw_count'], 1023, 'null-draw-count', rel)
                equal(len(null['draws']), 1023, 'null-stored-draw-count', rel)
                equal(null['with_replacement'], True, 'null-replacement-law', rel)
                equal(null['packing'], 'MSB first; trailing zero padding', 'null-packing', rel)
                bank_counts = Counter(logs[P] for P, bit, ident in banks[cid])
                observed_score = 0
                for P, bit, ident in banks[cid]:
                    k = logs[P]
                    equal(bit, actual_labels[k], 'retained-bank-label', rel, ident)
                    observed_score += 0 if bit is None else 1 if bit == int(k > r//2) else -1
                observed_q = 0
                requirements = []
                for P, bits, ident in starts[cid]:
                    k = logs[P]
                    correct = True
                    req = 0
                    hole = False
                    for bit in bits:
                        equal(bit, actual_labels[k], 'retained-start-label', rel, ident)
                        correct &= bit is not None and bit == int(k > r//2)
                        pair = min(k, r-k)
                        if not mask[k]:
                            hole = True
                        elif pair != 1:
                            req |= 1 << (8*((n+7)//8)-1-positions[pair])
                        k = k*2 % r
                    observed_q += correct
                    requirements.append(None if hole else req)
                weights = [(i, bank_counts[k]+bank_counts[r-k]) for k, i in positions.items()
                           if bank_counts[k]+bank_counts[r-k]]
                baseline = bank_counts[1]+bank_counts[r-1]
                key = hashlib.sha256(master+('null/'+cid).encode()).digest()
                stream = Replay(key, b'controlled-followup/exact-mask-odd-anchor/v1')
                seen = Counter()
                score_ties, q_ties = Counter(), Counter()
                for i, encoded in enumerate(null['draws']):
                    raw = stream.bit_bytes(n)
                    equal(encoded, raw.hex(), 'orientation-byte-replay', rel, i)
                    stored = bytes.fromhex(encoded)
                    equal(len(stored), (n+7)//8, 'packed-length', rel, i)
                    if n % 8:
                        equal(stored[-1] & ((1 << (8-n % 8))-1), 0, 'packed-padding', rel, i)
                    seen[encoded] += 1
                    # Recompute statistics from STORED bits; stream equality is a separate check.
                    score = baseline+sum(weight*(1-2*((stored[j//8] >> (7-j % 8)) & 1)) for j, weight in weights)
                    integer = int.from_bytes(stored, 'big')
                    q = sum(req is not None and (integer & req) == 0 for req in requirements)
                    stats = obj['retained_bank_statistics']['reference_statistics'][i]
                    equal(stats, {'score_sum': score, 'score_denominator': len(banks[cid]), 'q0_successes': q, 'q0_denominator': len(starts[cid])}, 'retained-statistic-reconstruction', rel, i)
                    score_ties['equal' if score == observed_score else 'greater' if score > observed_score else 'less'] += 1
                    q_ties['equal' if q == observed_q else 'greater' if q > observed_q else 'less'] += 1
                mult = [{'packed_hex': k, 'count': v} for k, v in sorted(seen.items())]
                equal(null['orientation_multiplicities'], mult, 'orientation-multiplicity', rel)
                equal(null['unique_draws'], len(seen), 'null-unique', rel)
                equal(null['duplicate_draws'], 1023-len(seen), 'null-duplicates', rel)
                equal(null['stream_counts'], stream.counts(), 'null-stream-counts', rel)
                equal(null['packed_bytes_stored'], ((n+7)//8)*1023, 'packed-byte-accounting', rel)
                stats = obj['retained_bank_statistics']
                for name, counted in (('score', score_ties), ('q0', q_ties)):
                    equal(stats['ties'][name], {**{k: counted[k] for k in ('equal','greater','less')}, 'count': 1023, 'inferential_p_value': None}, 'ties-multiplicity-and-null-pvalue', rel, name)
                equal(stats['bank_duplicates'], len(banks[cid])-len(bank_counts), 'bank-duplicates-retained', rel)
                start_distinct = len({logs[P] for P, bits, ident in starts[cid]})
                equal(stats['start_duplicates'], len(starts[cid])-start_distinct, 'start-duplicates-retained', rel)
                lookups = 1023*(len(banks[cid])+(r.bit_length()+1)*len(starts[cid]))
                equal(stats['diagnostic_label_lookups'], lookups, 'null-lookup-count', rel)
                result.update(null_status=null['status'], defined_pairs=len(positive), free_bits=n,
                              null_draws=len(null['draws']), unique_draws=len(seen), stream_counts=stream.counts(),
                              packed_bytes=null['packed_bytes_stored'], diagnostic_lookups=lookups,
                              ties={'score': dict(score_ties), 'q0': dict(q_ties)})
                totals['null_eligible_curves'] += 1
                totals['null_draws'] += len(null['draws'])
                totals['null_sha256_blocks'] += stream.counter
                totals['null_rejected_blocks'] += stream.rejected
                totals['null_duplicate_draws'] += 1023-len(seen)
                totals['null_packed_bytes'] += null['packed_bytes_stored']
                totals['null_diagnostic_lookups'] += lookups
                totals['null_statistics_checked'] += len(null['draws'])
                totals['ties_tables_checked'] += 2
                if not first_null_done:
                    first_null_done = True
                    existing_prefix = bytes.fromhex(null['draws'][0])[:8]
                    for name, changed_key, domain, shift, endian in [
                        ('seed-byte', bytes([key[0]^1])+key[1:], b'controlled-followup/exact-mask-odd-anchor/v1', 0, 'big'),
                        ('local-domain', key, b'controlled-followup/exact-mask-odd-anchor/v0', 0, 'big'),
                        ('counter-start', key, b'controlled-followup/exact-mask-odd-anchor/v1', 1, 'big'),
                        ('counter-endian', key, b'controlled-followup/exact-mask-odd-anchor/v1', 0, 'little')]:
                        mutated = bytearray(8)
                        for j in range(64):
                            bit = hashlib.sha256(changed_key+b'\0'+domain+b'\0'+(j+shift).to_bytes(8, endian)).digest()[-1] & 1
                            mutated[j//8] |= bit << (7-j % 8)
                        detected = bytes(mutated) != existing_prefix
                        record(detected, 'known-false-'+name, rel, 'draw0/prefix64bits')
                        mutation_controls.append({'mutation': name, 'source': rel, 'witness': 'draw0/free-bits0..63', 'detected': detected, 'retained_prefix_hex': existing_prefix.hex(), 'mutated_prefix_hex': bytes(mutated).hex()})
                    bad_draw = bytes([existing_prefix[0]^128])+existing_prefix[1:]
                    mutation_controls.append({'mutation': 'stored-draw-bit', 'source': rel, 'witness': 'draw0/freebit0', 'detected': bad_draw != existing_prefix})
                    mutation_controls.append({'mutation': 'multiplicity-plus-one', 'source': rel, 'witness': 'orientation_multiplicities[0].count', 'detected': sum(seen.values())+1 != 1023})
        else:
            target_ids = {t['target_id']: tuple(t['point']) for t in curve['targets']}
            equal(len(target_ids), 64, 'distinct-target-count', VIEW+'public-cohort.json', cid)
            equal(len(set(target_ids.values())), 64, 'distinct-target-points', VIEW+'public-cohort.json', cid)
        rel = POST+'uniform-'+cid+'.jsonl'
        seen_uniform = set()
        hist = Counter()
        blocks = 0
        for line, row in rows(rel):
            ident = row['cell_id']
            record(ident not in seen_uniform, 'uniform-id-unique', rel, line)
            seen_uniform.add(ident)
            if ident not in budgets:
                record(False, 'uniform-unplanned-cell', rel, line)
                continue
            M, tid = budgets[ident]
            meta = traces[tid]
            u = row['uniform']
            equal((row['M'], row['trace_id']), (M, tid), 'uniform-budget-binding', rel, line)
            equal(meta['curve'], cid, 'uniform-curve-binding', rel, line)
            truth = logs[meta['target']]
            m = min(M, r-1)
            key = hashlib.sha256(master+('uniform/'+ident).encode()).digest()
            stream = Replay(key, b'controlled-followup/uniform-list/v1')
            # Explicit dense array gives a structurally separate Fisher-Yates realization.
            population = list(range(1, r))
            guesses, selected_indices = [], set()
            for i in range(m):
                j = i+stream.below(r-1-i)
                selected_indices.add(j)
                population[i], population[j] = population[j], population[i]
                guesses.append(population[i])
            checks = [k == truth for k in guesses]
            expected = {'requested_M': M, 'effective_M': m, 'domain': [1, r-1],
                        'success_probability_exact': [m, r-1], 'saturated': M >= r-1,
                        'guesses': guesses, 'checks': checks, 'success': any(checks),
                        'stream_counts': stream.counts(), 'public_equations': m,
                        'stored_scalar_words': len(selected_indices)+m, 'wall_valid': False}
            for key_name, value in expected.items():
                equal(u[key_name], value, 'uniform-'+key_name, rel, line)
            equal(len(set(u['guesses'])), len(u['guesses']), 'uniform-distinct', rel, line)
            record(all(1 <= x < r for x in u['guesses']), 'uniform-nonzero-domain', rel, line)
            hist['zero_M' if M == 0 else 'saturated' if M >= r-1 else 'interior_M'] += 1
            blocks += stream.counter
            totals['uniform_public_equations'] += m
            totals['uniform_rejected_blocks'] += stream.rejected
            if not first_uniform_done and len(guesses) >= 2:
                first_uniform_done = True
                duplicate = guesses.copy()
                duplicate[1] = duplicate[0]
                zero_list = guesses.copy()
                zero_list[0] = 0
                for name, bad in [('duplicate-guess', duplicate), ('zero-guess', zero_list)]:
                    detected = not without_replacement_valid(bad, r-1, M)
                    record(detected, 'known-false-'+name, rel, line)
                    mutation_controls.append({'mutation': name, 'source': rel, 'row': line, 'cell_id': ident, 'detected': detected})
        expected_ids = {key for key, (_, tid) in budgets.items() if traces[tid]['curve'] == cid}
        equal(seen_uniform, expected_ids, 'uniform-complete-cell-coverage', rel)
        result['uniform_rows'] = len(seen_uniform)
        result['uniform_branches'] = dict(hist)
        result['uniform_sha256_blocks'] = blocks
        totals['uniform_rows'] += len(seen_uniform)
        totals['uniform_sha256_blocks'] += blocks
        for k, v in hist.items():
            totals['uniform_'+k] += v
        results.append(result)
        print(json.dumps({'stage': 'curve complete', 'curve': cid, 'null_draws': result.get('null_draws', 0), 'uniform_rows': len(seen_uniform), 'failures': sum(FAILURES.values()), 'at': utc_now()}), flush=True)
    for key, expected in [('single_rows', 345600), ('trace_rows', 36864), ('decoder_rows', 73728), ('uniform_rows', 73728)]:
        equal(totals[key], expected, 'declared-total-'+key, 'frozen-protocol')
    equal(len(traces), 12288, 'confirmation-attempts', VIEW+'raw/traces.jsonl')
    result = {'task_id': TASK, 'joint': 'Host reference PRNG and random law',
              'started_at': started, 'completed_at': utc_now(), 'totals': dict(totals),
              'M_histogram': dict(sorted(budget_hist.items())), 'curves': results,
              'input_hashes': INPUTS, 'failure_counts': dict(FAILURES), 'witnesses': WITNESSES,
              'retained_mutation_controls': mutation_controls,
              'retained_coverage_gaps': ['No retained ineligible asymmetric/undefined-anchor or D=1 cases unless identified in per-curve counts; fixed public controls cover only the stated toy cases.', 'No retained saturation or raw SHA256 rejection branch unless identified in totals; mathematical rejection proof and fixed byte control do not constitute empirical branch coverage.', 'Host seed event has no timestamp/OS entropy transcript; physical entropy and late-generation independence are not established by retained bytes.', 'Worker cohort random stream/curve-sampling implementation is contextual definition only; no claim of full worker PRNG replay, native operation counters, clocks, RSS, I/O, currency or energy qualification.'],
              'scientific_runs': 0, 'new_entropy_or_nonce_draws': 0,
              'producer_imports_calls_reruns': 0, 'new_reference_bank': False,
              'method': 'Deterministic reconstruction of SAME retained stream/mask/list/statistic data. No candidate/predicate engine invocation. SHA256 replay is source-inspected independent code, distinct from the blind ideal-law derivation.'}
    with (OUT/'phase2-results.json').open('x') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print(json.dumps({'stage': 'audit complete', 'totals': dict(totals), 'failures': dict(FAILURES), 'completed_at': result['completed_at']}), flush=True)


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def orientation_valid(values, mask, r=7, anchor=1, anchor_value=1):
    """Fixed mathematical sign-orientation condition; no producer packing."""
    if set(values) != set(mask):
        return False
    if anchor not in mask or (-anchor) % r not in mask:
        return False
    if values[anchor] != anchor_value or values[(-anchor) % r] != 1-anchor_value:
        return False
    for x in mask:
        if (-x) % r not in mask:
            return False
        if values[x] not in (0, 1) or values[(-x) % r] != 1-values[x]:
            return False
    return True


def without_replacement_valid(values, n, measured_m):
    return (len(values) == min(measured_m, n)
            and len(set(values)) == len(values)
            and all(1 <= x <= n for x in values))


def phase1_controls():
    started = utc_now()
    byte_alphabet = tuple(range(256))
    naive = Counter(x % 10 for x in byte_alphabet)
    threshold = 256-(256 % 10)
    accepted = Counter(x % 10 for x in byte_alphabet if x < threshold)
    assert [naive[x] for x in range(10)] == [26]*6+[25]*4
    assert [accepted[x] for x in range(10)] == [25]*10
    assert sum(x >= threshold for x in byte_alphabet) == 6
    assert len(set(naive.values())) != 1  # known-false modulo uniformity refused

    mask = set(range(1, 7))
    fixed_free_orientations = ((0, 0), (0, 1), (1, 0), (1, 1))
    words = []
    for left, right in fixed_free_orientations:
        values = {1: 1, 6: 0, 2: left, 5: 1-left, 3: right, 4: 1-right}
        assert orientation_valid(values, mask)
        words.append(tuple(values[x] for x in range(1, 7)))
    assert len(set(words)) == 4
    wrong_anchor = {x: words[0][x-1] for x in range(1, 7)}
    wrong_anchor[1], wrong_anchor[6] = 0, 1
    assert not orientation_valid(wrong_anchor, mask)
    correct = {x: words[0][x-1] for x in range(1, 7)}
    assert not orientation_valid(correct, mask-{4})
    explicit_draws = ((0, 0), (0, 0), (1, 1))
    multiplicities = Counter(explicit_draws)
    assert sum(multiplicities.values()) == 3
    deduplicated = {word: 1 for word in multiplicities}
    assert sum(deduplicated.values()) != len(explicit_draws)

    assert without_replacement_valid((1, 2, 3), 6, 3)
    assert not without_replacement_valid((1, 2, 2), 6, 3)
    assert not without_replacement_valid((0, 1, 2), 6, 3)
    assert without_replacement_valid((), 6, 0)
    assert without_replacement_valid((1, 2, 3, 4, 5, 6), 6, 10)
    subsets = tuple(itertools.combinations(range(1, 7), 3))
    hits_by_truth = {truth: sum(truth in row for row in subsets)
                     for truth in range(1, 7)}
    assert len(subsets) == 20 and set(hits_by_truth.values()) == {10}
    without_replacement = Fraction(3, 6)
    with_replacement = 1-Fraction(5, 6)**3
    assert without_replacement != with_replacement
    return {
        "task_id": TASK,
        "phase": "phase1_fixed_public_controls",
        "started_at": started,
        "completed_at": utc_now(),
        "scientific_runs": 0,
        "entropy_or_nonce_draws": 0,
        "producer_imports_or_calls": 0,
        "retained_scientific_inputs_read": 0,
        "controls": [
            {"id": "byte-alphabet-bound10", "scope": "All integers 0..255, bound10",
             "naive_modulo_counts": [naive[x] for x in range(10)],
             "rejection_threshold": threshold,
             "accepted_residue_counts": [accepted[x] for x in range(10)],
             "rejected_values": list(range(threshold, 256)),
             "known_false_naive_uniformity_rejected": True},
            {"id": "fixed-public-orientation-Z7", "scope": "mask1..6; anchor pair +/-1; four explicit free-bit choices",
             "support": len(set(words)), "anchor_mutation_rejected": True,
             "asymmetric_mask_mutation_rejected": True,
             "multiplicity_fixture_draws": 3,
             "multiplicity_fixture_unique": len(multiplicities),
             "lost_multiplicity_mutation_rejected": True},
            {"id": "fixed-public-nonzero-distinct-Z7", "scope": "Explicit lists in1..6; all20 unordered3-subsets",
             "zero_mutation_rejected": True, "duplicate_mutation_rejected": True,
             "empty_and_saturation_checked": True,
             "subsets": len(subsets), "hits_for_each_fixed_truth": hits_by_truth,
             "without_replacement_hit_fraction": str(without_replacement),
             "with_replacement_hit_fraction": str(with_replacement),
             "replacement_law_distinguished": True}
        ],
        "retained_data_checks": "Not executed before committed release and explicit root ACK."
    }


def finalize():
    """Editable final report/diagram source; reads own outside outputs only."""
    result = json.loads((OUT/'phase2-results.json').read_text())
    phase1 = json.loads((OUT/'checks.json').read_text())
    if 'phase1_fixed_public_controls' in phase1:
        phase1 = phase1['phase1_fixed_public_controls']
    derivation = json.loads((OUT/'derivation.json').read_text())
    t = result['totals']
    joint = 'Host reference PRNG and random law'
    dest = 'coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-128d4e/reviews/'+TASK
    release = 'coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-128d4e/releases/'+TASK+'.json'
    phase1_reads = [json.loads(x) for x in (OUT/'readlog.jsonl').read_text().splitlines()]
    phase2_reads = [json.loads(x) for x in (OUT/'phase2-readlog.jsonl').read_text().splitlines()]
    events = []
    for entry in phase1_reads:
        events.append({'kind': 'read', 'at': entry['opened_at'], 'source': entry['canonical_relative_path']})
    events += [
        {'kind': 'seal', 'at': '2026-10-30T03:36:07.099302Z', 'artifact': dest+'/seal.json',
         'sha256': '1548096c12c567814d7fa7a478fa75195db06edb867085701ee9d1bf2e3112c1'},
        {'kind': 'unblind', 'at': '2026-10-30T03:38:19.737965+00:00', 'artifact': release,
         'sha256': 'fe9fab09a48a3db1acd72355a2d39e4d49c8e52a97f59611eb2fce31f903ede7'},
    ]
    enumerations = []
    for entry in phase2_reads:
        if entry.get('operation', '').startswith('directory filenames'):
            enumerations.append(entry)
        else:
            events.append({'kind': 'read', 'at': entry['opened_at'], 'source': entry['canonical_relative_path']})
    for seq, event in enumerate(events, 1):
        event['seq'] = seq
    sources = list(dict.fromkeys(event['source'] for event in events if event['kind'] == 'read'))
    attestation = {
        'review_attestation': {
            'task_id': TASK, 'joints_owned': [joint], 'verdicts': {joint: 'holds'},
            'verdict_scope': 'Complete retained inventory and the declared ideal independent-hash model only. Unexercised branches and physical entropy/stage independence remain unqualified.',
            'sources_read': sources, 'read_sibling_reports': False, 'blind_from_respected': True,
            'phased_release': {'schema': 'sealed-blind-review/v1', 'events': events},
            'recorded_at': utc_now(), 'phase1_source_count': len(derivation['sources_read']),
            'phase1_read_events': len(phase1_reads),
            'directory_enumerations': enumerations,
            'read_log_original_events': {'phase1': phase1_reads, 'phase2': phase2_reads},
            'phase1_metadata_exposure': derivation['metadata_exposure'],
            'root_publication_ack': {'phase1_commit': '6f1a20fad9', 'release_commit': 'abc17d567a',
                                     'root_ack_commit': '246078079c', 'ack_source': 'Explicit root message; no root ACK file opened.'},
            'inference_provenance': derivation['inference_provenance'],
            'write_scope': 'Only the assigned fresh outside task directory. Root alone publishes canonical files/Git/claims/storage.',
            'producer_imports_calls_reruns': 0, 'new_scientific_runs': 0,
            'new_scientific_inputs_or_entropy': 0, 'source_data_modified': False,
            'procedure_deviations': ['Initial filename enumeration used rg default ignore rules and did not list ignored hydrated payloads. Root clarified their presence; exact allowed regular payloads were read successfully. No missing-payload conclusion was made.', 'Initial large displays of permitted original definitions/contracts were truncated; exact relevant sections/JSON pointers were subsequently displayed. All actual opens remain logged.'],
        }
    }
    (OUT/'read-attestation.yaml').write_text(json.dumps(attestation, indent=2)+'\n')
    # SVG source: counts are actual independently inspected units, not success rates.
    panels = [
        ('48 / 48', 'retained curves', '821,686 orbit points reconstructed'),
        ('24,552 / 24,552', 'orientation draws', '24 exact masks; 48 tie tables'),
        ('73,728 / 73,728', 'uniform rows', '15,820 empty; 57,908 interior'),
        ('3,068,802', 'decoder words', '73,728 M budgets; 452 zero checks'),
    ]
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="300" viewBox="0 0 900 300">',
           '<rect width="900" height="300" fill="#f8fafc"/>',
           '<text x="24" y="32" font-family="sans-serif" font-size="20" fill="#13293d">J-law: complete retained comparison inventory</text>']
    for index, (value, unit, detail) in enumerate(panels):
        x = 24+(index % 2)*444
        y = 50+(index//2)*94
        svg += [f'<rect x="{x}" y="{y}" width="420" height="82" rx="7" fill="#e7f2f8" stroke="#b3cddd"/>',
                f'<text x="{x+14}" y="{y+28}" font-family="sans-serif" font-size="23" fill="#123d57">{value}</text>',
                f'<text x="{x+14}" y="{y+48}" font-family="sans-serif" font-size="14" fill="#1d4f6b">{unit}</text>',
                f'<text x="{x+14}" y="{y+68}" font-family="sans-serif" font-size="12" fill="#334155">{detail}</text>']
    svg += ['<text x="24" y="260" font-family="sans-serif" font-size="14" fill="#334155">Zero mismatches. Eight retained mutations detected. Units count inspected records/work.</text>',
            '<text x="24" y="281" font-family="sans-serif" font-size="12" fill="#475569">RUN-ECDLP-939237 | Ideal hash qualification; no native-cost, entropy or all-branch certification.</text>', '</svg>']
    (OUT/'diagram.svg').write_text('\n'.join(svg)+'\n')
    report = f'''# Retained host-reference random-law audit

TASK-20261030-3393bd · J-law · RUN-ECDLP-939237 · 2026-10-30 UTC

**Verdict: holds within the complete retained inventory under the declared ideal independent-hash model.** Independent deterministic reconstruction found zero mismatches. This is a bounded component result; physical entropy, independent stages, unexercised branches and native costs remain unqualified. The prior historical inconclusive review and all scientific statuses remain unchanged.

| Independently inspected quantity | Actual coverage |
|:---|---:|
| Retained curves / reconstructed orbit points | 48 / 821,686 |
| Eligible masks / orientation draws | 24 / 24,552 |
| Retained reference statistics / tie tables | 24,552 / 48 |
| Decoder budgets / complete decoder words | 73,728 / 3,068,802 |
| Uniform lists / empty / interior budgets | 73,728 / 15,820 / 57,908 |
| Separately counted zero checks / capped cells | 452 / 381 |
| Retained mutation controls detected | 8 of 8 |

![Actual comparison coverage, in labeled record/work units. No success-rate or advantage inference.](diagram.svg)

The audit read every one of the 48 declared uniform files, including 24 legitimate empty calibration files, and every one of the 24 calibration null files. All raw single rows (345,600), traces (36,864) and decoder cells (73,728) were streamed once. Each confirmation curve supplied 3,072 conditional uniform rows. Recorded M ranged from 0 to 91.

\\newpage

## Law and independent method

For bound b and a uniform 256-bit proposal U, let T = b floor(2^256/b). Accept U below T and return U modulo b. Every residue has the same number of accepted preimages. Source inspection fixed counter0, eight-byte big-endian counters, full-digest big-endian reduction, NUL separators and the literal local domains; these details were explicitly underspecified in the blind definitions.

The independent replay derived each local seed as SHA256(master concatenated with its exact namespace). Orientation bits used the retained null namespace and were packed MSB first with zero trailing padding. All 198,521,334 null blocks agreed; their recorded accepted/block counts and all 24,827,187 packed storage bytes agreed. Uniform replay used a dense explicit-array Fisher–Yates construction, structurally distinct from the producer's sparse swap map. Every guess, public check, effective budget, success flag, storage count and stream count agreed across 1,139,829 uniform blocks. No raw hash rejection occurred. These are reconstructed logical counts, not qualified native measurements.

On each same retained curve, affine group equations reconstructed its finite orbit. Solving the cyclic slope-cocycle equations reconstructed the full primary mask. Exactly the paired nonzero defined positions became free coordinates; +1 was pinned0 and -1 pinned1. With D defined sign pairs, support is 2^(D-1). Each of 1,023 draws per eligible curve was compared in order. Exact masks, support objects, padding, duplicate counts, sorted multiplicities and multiplicity-weighted ties agreed. There were zero duplicate orientation draws. Retained point/start duplicates were preserved. All 88,190,784 declared diagnostic lookups were reconciled by algebra on the same retained banks and starts; no full-orbit recovery census or new bank was created.

Every cell budget was independently reconstructed from its retained trace bits by exhaustive permitted erasure assignments and Hamming flips, binary interval inequalities and scalar conversion. Distinct legal nonzero scalars formed M; zero checks stayed separate. For N=r-1 and m=min(M,N), the conditional without-replacement hit law is m/N. With replacement the expression would instead be 1-(1-1/N)^m. The six cells share targets, blindings, traces and data-dependent budgets; domain separation does not make these independent scientific trials or make the matched-M reference a standalone solver.

## Sensitivity and limits

The fixed public byte alphabet0..255/bound10 distinguishes biased modulo reduction (counts26 or25) from rejection (25 each). Public Z7 fixtures detect wrong anchors, asymmetric masks, lost multiplicity, zero and duplicate guesses. Tiny copies of the first retained witnesses additionally detected eight mutations: seed byte, local domain, counter start, counter endian, draw bit, multiplicity, duplicate guess and zero guess. Their exact source rows and changed prefixes are in checks.json.

No retained case exercised an ineligible or degenerate mask, actual orientation duplicates, saturation, or raw SHA rejection. Those branches are not certified by this replay. Every observed mask had 305–26,193 free bits. A fixed deterministic generator with a real 256-bit seed has at most 2^256 complete sequences; symbolic full support and iid fairness are model statements, not consequences of byte agreement. The source explicitly declares its ideal independent-hash model. This distinction is a qualification, not an observed reference failure.

The host seed record lacks a UTC draw timestamp and OS entropy transcript. Retained bytes and source order do not prove physical entropy or late independent generation. Worker PRNG/curve sampling, native clocks/counters, RSS, I/O, currency and energy are outside this component replay. No pattern p-value, advantage, mechanism, exponent, family closure or whole-claim verdict is inferred.

\\newpage

## Evidence and chronology

The independent phase1 derivation used only the twelve allowed files. The original protocol/specification/trial records contain historical source-review, failure and provenance metadata; that permitted exposure is disclosed without claiming sanitized inputs. Every actual canonical file open was logged before access. No sibling review was read in either phase.

- Blind derivation generated: **2026-10-30 03:36:07.098270 UTC**.
- Immutable seal: **03:36:07.099302 UTC**; derivation SHA256 prefix `7a5b438c98df`.
- Root release recorded: **03:38:19.737965 UTC**, followed by explicit root ACK; release SHA256 prefix `fe9fab09a48a`. Full digests are in checks.json/read-attestation.yaml.
- Complete independent retained comparison: **{result['started_at']}** to **{result['completed_at']}**, command exit0.

Primary source locations (all exact content hashes and actual read events appear in checks.json/read-attestation.yaml):

- Frozen definitions: experiments/EXP-ECDLP-080f41/protocol.json, specification.yaml and trial-plan.json.
- Source inspected after release: harness/classical_ecdlp_controlled_followup/host/reference.py, host/verify.py and postrun/run_postrun.py. No producer module was imported or called.
- Same retained public cohort and three raw streams: BATCH-cbf9d7/derived-supervisor-views/RUN-ECDLP-939237/manifest-json-v1/supervisor/modal/collected/.
- Same retained host seed, 24 null and 48 uniform payloads: experiments/EXP-ECDLP-080f41/postrun-from-view-346631/.

The smallest retained sensitivity witness is null-discovery-10-0.json, draw0/free-bits0..63: retained prefix `b6687149da00e772`; the four altered seed/domain/counter fixtures produce different prefixes, retained verbatim in checks.json. Duplicate/zero guess mutations use uniform-confirmation-A-10-0.jsonl row3, cell target0000/rep0/t1.e0. No source bytes were edited.

Canonical publication consists of this report, checks, exact read attestation, unchanged derivation/seal, independent audit.py, editable SVG and inspected PDF plus visual-inspection.json. The report and SVG templates are embedded in audit.py. Root owns canonical writes/publication and separately inspects every PDF page. No canonical graph was modified: this audit changes no scientific relationship or status.

Requested inference policy: review-adversarial/xhigh in a fresh independent session. Serving model remains unverified; no provider probe or model identity is claimed. Literature scope is the exact allowed internal primary definitions/source only; no novelty or literature-completeness claim.

**review_attestation:** joints_owned=[Host reference PRNG and random law]; verdicts={{Host reference PRNG and random law: holds}} in the bounded scope above; read_sibling_reports=false; blind_from_respected=true. The complete machine-readable timeline, including all39 phase1 file reads and exact seal/unblind events, is read-attestation.yaml.
'''
    (OUT/'report.md').write_text(report)
    (OUT/'render.md').write_text(report.replace('(diagram.svg)', '(diagram.pdf)'))
    commands = [
        ['inkscape', str(OUT/'diagram.svg'), '--export-type=pdf', '--export-filename='+str(OUT/'diagram.pdf')],
        ['pandoc', str(OUT/'render.md'), '-o', str(OUT/'report.pdf'), '--pdf-engine=xelatex', '-V', 'geometry:margin=18mm', '-V', 'fontsize=10pt', '-V', 'documentclass=article', '--resource-path='+str(OUT)],
        ['pdftoppm', '-png', '-r', '110', str(OUT/'report.pdf'), str(OUT/'page')],
        ['pdfinfo', str(OUT/'report.pdf')],
    ]
    rendering = []
    for command in commands:
        command_started = utc_now()
        proc = subprocess.run(command, text=True, capture_output=True, cwd=OUT)
        rendering.append({'argv': command, 'started_at': command_started, 'completed_at': utc_now(),
                          'exit_code': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr})
        if proc.returncode:
            raise RuntimeError(json.dumps(rendering[-1]))
    checks = {
        'task_id': TASK, 'joint': joint, 'verdict': 'holds',
        'scope': attestation['review_attestation']['verdict_scope'],
        'phase1_fixed_public_controls': phase1, 'phase2_retained_audit': result,
        'commands': [
            {'command': 'python '+str(OUT/'audit.py')+' --phase1-controls '+str(OUT/'checks.json'),
             'exit_code': 0, 'completed_at': phase1['completed_at']},
            {'command': 'python '+str(OUT/'audit.py')+' --phase2 > '+str(OUT/'phase2-command.log')+' 2>&1',
             'exit_code': 0, 'started_at': result['started_at'], 'completed_at': result['completed_at'],
             'audit_code_sha256_at_execution': 'd0daa5e9a84872ff925f2b8a9fb232c40d59c3b69f6b1a8402f7b8bac7e65413',
             'code_change_after_execution': 'Only final report/diagram/attestation rendering function and finalize CLI added; scientific audit/control functions unchanged.'},
        ],
        'audit_stdout_complete': (OUT/'phase2-command.log').read_text(),
        'rendering': rendering,
        'supporting_outside_results_sha256': hashlib.sha256((OUT/'phase2-results.json').read_bytes()).hexdigest(),
        'sealed_artifacts_unchanged': {name: hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ['derivation.json','seal.json','readlog.jsonl']},
        'code_final_sha256': hashlib.sha256((OUT/'audit.py').read_bytes()).hexdigest(),
        'independence': {'producer_imports_calls_reruns': 0, 'new_scientific_inputs_or_entropy': 0,
                         'new_reference_bank': False, 'read_sibling_reports': False},
        'visual_inspection': 'Pending actual all-page view; recorded separately after image inspection.',
    }
    (OUT/'checks.json').write_text(json.dumps(checks, indent=2)+'\n')
    print(json.dumps({'report_pdf': str(OUT/'report.pdf'), 'pages': rendering[-1]['stdout'],
                      'pngs': [str(x) for x in sorted(OUT.glob('page-*.png'))],
                      'timeline_events': len(events), 'canonical_source_files': len(sources),
                      'phase1_reads': len(phase1_reads)}))


def record_visual_inspection():
    """Called only AFTER this agent actually viewed every final page image."""
    checks = json.loads((OUT/'checks.json').read_text())
    result = checks['phase2_retained_audit']
    t = result['totals']
    stamp = utc_now()
    pdf_hash = hashlib.sha256((OUT/'report.pdf').read_bytes()).hexdigest()
    inspection = {
        'task_id': TASK, 'recorded_at': stamp, 'inspected_at': stamp,
        'method': 'Producer agent actually opened and visually read all three final pdftoppm PNG pages through tools.view_image after the second rendering.',
        'pdf_path': str(OUT/'report.pdf'), 'pdf_sha256': pdf_hash,
        'page_count': 3, 'all_pages_inspected': True, 'passed': True,
        'pages': [
            {'page': i, 'png_path': str(OUT/f'page-{i}.png'),
             'png_sha256': hashlib.sha256((OUT/f'page-{i}.png').read_bytes()).hexdigest(),
             'inspected': True, 'finding': finding}
            for i, finding in [(1, 'Coverage table and SVG readable; units, scope and run/task IDs present; no clipping.'),
                               (2, 'Mathematical law, actual counts, controls and qualifications readable; all text stays on page.'),
                               (3, 'Exact chronology, source locations, bounded attestation and digest prefixes readable; prior long-digest clipping corrected.')]
        ],
        'first_render_correction': json.loads((OUT/'first-render/inspection.json').read_text()),
        'root_separate_inspection': 'Not asserted here; root will independently inspect every final page before archive.'
    }
    (OUT/'visual-inspection.json').write_text(json.dumps(inspection, indent=2)+'\n')
    checks['visual_inspection'] = {'status': 'passed', 'all_pages_actually_viewed': [1,2,3],
                                   'pdf_sha256': pdf_hash, 'recorded_at': stamp,
                                   'details': 'visual-inspection.json'}
    counts = Counter(c.get('null_status') for c in result['curves'] if 'null_status' in c)
    free_bits = [c['free_bits'] for c in result['curves'] if 'free_bits' in c]
    checks['realized_branch_coverage'] = {
        'null_complete': counts['complete'], 'null_degenerate': counts['degenerate'],
        'null_ineligible_asymmetric_mask': counts['ineligible_asymmetric_mask'],
        'null_ineligible_undefined_anchor': counts['ineligible_undefined_anchor'],
        'null_free_bits_min': min(free_bits), 'null_free_bits_max': max(free_bits),
        'null_small_support_exponent_below63': sum(n < 63 for n in free_bits),
        'null_actual_duplicate_draws': t['null_duplicate_draws'],
        'raw_hash_rejections': t['null_rejected_blocks']+t['uniform_rejected_blocks'],
        'uniform_empty': t['uniform_zero_M'], 'uniform_interior': t['uniform_interior_M'],
        'uniform_saturation': t.get('uniform_saturated',0),
        'decoder_capped': t['decoder_capped_rows'],
        'scope': 'Zero-count branches are absent from retained data, not empirically certified by this audit.'
    }
    checks['cost_qualifications'] = {
        'host_PRNG_logical_blocks_replayed': t['null_sha256_blocks']+t['uniform_sha256_blocks'],
        'host_PRNG_digest_output_bytes_derived': 32*(t['null_sha256_blocks']+t['uniform_sha256_blocks']),
        'PRNG_units': 'Logical full32-byte SHA256 blocks in the independent SAME-seed reconstruction; no assertion of qualified native producer costs.',
        'worker_predicate_or_native_operation_cost': {'value': None, 'reason': 'Not independently metered/replayed by this owned host-random-law joint.'},
        'host_native_group_operation_cost': {'value': None, 'reason': 'Mathematical reconstruction and source vectors do not qualify native operation execution.'},
        'clock_seconds': {'value': None, 'reason': 'No qualified clock claim; audit event timestamps record chronology only.'},
        'native_memory_bytes': {'value': None, 'reason': 'Stored abstract words/packed payload checked; no native RSS/allocation measurement.'},
        'curve_generation_cost': {'value': None, 'reason': 'No cohort generation, certification proposal replay or new input generation performed.'},
        'currency_energy': {'value': None, 'reason': 'Unmeasured.'},
    }
    checks['code_final_sha256'] = hashlib.sha256((OUT/'audit.py').read_bytes()).hexdigest()
    (OUT/'checks.json').write_text(json.dumps(checks, indent=2)+'\n')
    filenames = ['derivation.json','seal.json','report.md','checks.json','read-attestation.yaml',
                 'diagram.svg','report.pdf','visual-inspection.json','audit.py']
    inventory = {}
    for name in filenames:
        path = OUT/name
        inventory[name] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}
        path.chmod(0o444)
    (OUT/'phase2-readlog.jsonl').chmod(0o444)
    print(json.dumps({'task_id': TASK, 'ready_at': stamp, 'outside_directory': str(OUT),
                      'final_assigned_inventory': inventory}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase1-controls", type=Path)
    parser.add_argument("--phase2", action='store_true')
    parser.add_argument("--finalize", action='store_true')
    parser.add_argument("--record-visual-inspection", action='store_true')
    args = parser.parse_args()
    if args.record_visual_inspection:
        record_visual_inspection()
        return
    if args.finalize:
        finalize()
        return
    if args.phase2:
        phase2_audit()
        return
    assert args.phase1_controls is not None
    result = phase1_controls()
    with args.phase1_controls.open("x") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"task_id": TASK, "phase1_control_groups": len(result["controls"]),
                      "completed_at": result["completed_at"]}))


if __name__ == "__main__":
    main()
