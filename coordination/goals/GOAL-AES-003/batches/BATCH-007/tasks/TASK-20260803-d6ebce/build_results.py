#!/usr/bin/env python3
"""Assemble RESULTS.json for TASK-20260803-d6ebce from the raw run files.
Every number in the arm tables is read from disk, never typed by hand."""
import json, os, glob, hashlib, subprocess, datetime

D = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(D, 'runs')
B4 = '/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-003/batches/BATCH-004/tasks/TASK-20260803-367b1b'

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

def load(n):
    with open(os.path.join(R, n + '.json')) as f:
        return json.load(f)

SKIP = {'geom', 'pin_aes', 'pin_rand', 'environment'}
arms = {}
for f in sorted(glob.glob(os.path.join(R, '*.json'))):
    n = os.path.basename(f)[:-5]
    if n in SKIP:
        continue
    arms[n] = json.load(open(f))

# timings and exit statuses from commands.txt
cmds = []
for line in open(os.path.join(R, 'commands.txt')):
    parts = line.rstrip('\n').split('|')
    e = {'name': parts[0], 'exit': int(parts[1].split('=')[1])}
    if parts[2].startswith('secs='):
        e['seconds'] = float(parts[2].split('=')[1]); e['command'] = parts[3]
    else:
        e['seconds'] = None; e['command'] = parts[2]
    cmds.append(e)

def row(n):
    d = arms[n]
    N = d['nontrivial_trials']
    A = [j for j in range(4) if d['amask'] >> j & 1]
    pred = [0 if j in A else N for j in range(4)]
    return {
        'arm': n, 'sbox_spec': d['sbox_spec'], 'rounds': d['rounds'],
        'amask': d['amask'], 'active_words': A, 'smask': d['smask'],
        'log2N': d['log2N'], 'trials': d['trials'],
        'trivial_swaps_excluded': d['trivial_swaps_excluded'],
        'nontrivial_trials': N, 'W_ge1_nontrivial': d['W_ge1_nontrivial'],
        'W_ge1_by_word': d['W_ge1_by_word'], 'whist': d['whist'],
        'key_hex': d['key_hex'], 'seed': d['seed'], 'arm_id': d['arm_id'],
        'sbox_seed': d['sbox_seed'],
        'null_expectation_analytic': d['null_expectation_analytic'],
        'predicted_W_ge1_by_word': pred,
        'matches_proposition_1': d['W_ge1_by_word'] == pred,
    }

order = ['TIMING', 'S1-a1', 'S1-a2', 'S1-a4', 'S1-a8', 'S1-a3', 'S1-a5', 'S1-a6',
         'S1-a9', 'S1-a12', 'S1-a7', 'S1-a15', 'S2-r1', 'S2-r2', 'S2-r3',
         'B1-r2-a2-s2', 'S3-s2', 'S3-s4', 'S3-s7', 'S3-s13', 'S4-rand-a4',
         'S4-rand-a15', 'S4-key2-a4', 'S4-key2-a2', 'S4-rand-a2-s7', 'B2-r5-a2']
rows = [row(n) for n in order if n in arms]
missing_from_order = sorted(set(arms) - set(order))

TIMING_PARTIAL = {
    'arm': 'TIMING',
    'record_status': 'PARTIAL - RAW FILE NOT RETAINED',
    'why': 'This scoping invocation was made interactively before the driver script '
           'existed, so its stdout went to the terminal and was never written to '
           'runs/TIMING.json. Only the fields observed in the terminal tail are '
           'recorded below. The unobserved fields are NOT reconstructed and NOT '
           'guessed. This arm is excluded from every count and table in this file.',
    'command': '<instrument> arm TIMING aes 4 1 1 24 1 1 2',
    'exit_status': 0,
    'wall_clock_seconds_real': 3.460,
    'observed_fields': {
        'nontrivial_trials': 16777216,
        'trivial_swaps_excluded': 0,
        'W_ge1_nontrivial': 16777216,
        'W_ge1_by_word': [0, 16777216, 16777216, 16777216],
        'whist': [0, 0, 0, 16777216, 0],
        'null_expectation_analytic': 0.015625,
    },
    'unobserved_fields': ['key_hex', 'thread_seeds', 'sbox_first8'],
    'out_of_sample': False,
    'out_of_sample_note': 'Run BEFORE PREREGISTRATION.md was frozen. Its cell '
                          '(r=4, amask=1) reproduces a reading already published in '
                          'BATCH-004/005/006 and is NOT counted as a confirmation.',
    'superseded_by': 'S1-a1, the same cell run under the frozen protocol with its raw '
                     'file retained, which returned the identical vector.',
}

ver = json.load(open(os.path.join(D, 'analysis', 'verify_derivation.json')))
env = json.load(open(os.path.join(R, 'environment.json')))
pin_aes = json.load(open(os.path.join(R, 'pin_aes.json'))); pin_aes.pop('sbox', None)
pin_rand = json.load(open(os.path.join(R, 'pin_rand.json'))); pin_rand.pop('sbox', None)
geom = json.load(open(os.path.join(R, 'geom.json')))

r4 = [r for r in rows if r['rounds'] == 4 and r['amask'] == 2 and r['smask'] == 1
      and r['sbox_spec'] == 'aes' and r['seed'] == 20260803701 and r['arm'] == 'S1-a2'][0]
r5 = [r for r in rows if r['arm'] == 'B2-r5-a2'][0]

out = {}
out['schema'] = 'crypto.autoresearch.task_results.v1'
out['task_id'] = 'TASK-20260803-d6ebce'
out['batch'] = 'BATCH-007'
out['goal_id'] = 'GOAL-AES-003'
out['title'] = 'RANK 1: characterise the active-word preservation structure at r<=4'
out['role'] = 'executor'
out['claim_tier'] = 'toy'
out['certificate'] = {
    'kind': 'none',
    'basis': 'Pure measurement task. No discrete-log solve and no factor-base '
             'relation is claimed, so docs/claims-and-verification.md requires no '
             'solution certificate. The independent re-derivation check in '
             'analysis/verify_derivation.py is a check on the ARGUMENT, not a '
             'solution certificate, and is not presented as one.'
}
out['inference'] = {
    'policy': 'executor-implementation',
    'requested_policy': 'executor-implementation',
    'resolved_model': 'claude-opus-5',
    'fallback_used': True,
    'fallback_reason': 'executor-implementation is a GPT-5.6-family policy alias; '
                       'this harness is Claude Code and resolves only Claude models. '
                       'Recorded, not silently substituted.',
    'model_verified': False,
    'model_verified_reason': 'No `python3 -m orchestration.adapter doctor --probe` '
                             'was run in this task; the identifier is self-reported '
                             'configuration.',
    'standing_basis': '0137a051eb5828789eb267fa83c8278086578d4c',
    'independent_session': True,
}
out['budget'] = {
    'declared_wall_clock_seconds': 5400,
    'declared_memory_gb': 8,
    'maximum_runs': 30,
    'start_utc': '2026-08-03T18:05:51Z',
    'binding_stop_utc': '2026-08-03T19:35:51Z',
    'threads_used': 2,
    'threads_cap': 2,
    'instrument_invocations_used': len(cmds) + 1,
    'instrument_invocations_note': 'commands.txt holds %d lines; the TIMING/scoping '
        'arm was run before the driver script existed and is counted here as the +1. '
        'maximum_runs=30 is taken in the STRICT sense: every invocation of the frozen '
        'instrument counts, including geom and the pins and the one crashed pin.' % len(cmds),
    'peak_memory_note': 'Not instrumented. The instrument allocates per-thread job '
        'structs and 8 KiB of tables; resident set is far below 8 GB, but no '
        'measurement of peak RSS was taken, so no number is reported.',
}
out['instrument'] = {
    'reused_unchanged': True,
    'path': B4 + '/yoyo_sbox_v2',
    'binary_sha256': sha(B4 + '/yoyo_sbox_v2'),
    'source_path': B4 + '/src/yoyo_sbox_v2.c',
    'source_sha256': sha(B4 + '/src/yoyo_sbox_v2.c'),
    'hash_provenance': [
        'BATCH-005/tasks/TASK-20260803-48a239/runs/reused_inputs_sha256.txt',
        'BATCH-006/tasks/TASK-20260803-0764fc/RESULTS.json',
        'BATCH-006/archives/TASK-20260803-cd2b5e/snapshot-receipt.json'],
    'hash_match_against_prior_records': True,
    'fips197_c1_pin': pin_aes,
    'drawn_sbox_pin': pin_rand,
    'geometry': geom,
    'modified_by_this_task': False,
}
out['environment'] = env
out['commands'] = cmds
out['arms'] = rows
out['arms_not_in_ordered_table'] = missing_from_order
out['timing_scoping_arm_partial_record'] = TIMING_PARTIAL

out['deliverable_1_the_fact_pinned_down'] = {
    'question': 'Is the rule exactly "the active word is never preserved and every '
                'other word always is" at r<=4, or something narrower?',
    'answer': 'It is exactly that rule, and it is STRONGER than the card stated: it '
              'holds for multi-word active sets too, it is independent of the swap '
              'mask, and the whole W-histogram is a point mass at W = 4 - |A|.',
    'amasks_measured_here': sorted({r['amask'] for r in rows if r['rounds'] == 4}),
    'single_word_amasks_all_four_covered': True,
    'multi_word_amasks_covered': [3, 5, 6, 9, 12, 7, 15],
    'by_word_table_r4': [
        {'amask': r['amask'], 'active_words': r['active_words'], 'smask': r['smask'],
         'sbox': r['sbox_spec'], 'seed': r['seed'],
         'nontrivial_trials': r['nontrivial_trials'],
         'W_ge1_by_word': r['W_ge1_by_word'], 'whist': r['whist'],
         'matches_proposition_1': r['matches_proposition_1']}
        for r in rows if r['rounds'] == 4],
    'exceptions': 'None. Every r<=4 arm in this task matched the prediction exactly.',
    'falsifier_status': {
        'N1_active_word_ever_preserved_or_inactive_ever_lost': 'NOT OBSERVED',
        'N2_multi_word_amask_breaks_rule': 'NOT OBSERVED (amask 3,5,6,9,12,7,15 all matched)',
        'N3_smask_dependence': 'NOT OBSERVED (smask 1,2,4,7,13 identical at r=4,amask=2)',
        'N4_sbox_or_key_dependence': 'NOT OBSERVED',
        'N5_structure_survives_at_r5': 'NOT OBSERVED (structure is gone at r=5)',
    },
}

out['deliverable_2_round_boundary'] = {
    'answer': 'The structure holds at r = 1, 2, 3, 4 and is GONE at r = 5. The break '
              'is between r=4 and r=5.',
    'r4_vs_r5_side_by_side': {
        'r4': {'arm': r4['arm'], 'rounds': 4, 'amask': 2, 'smask': 1,
               'trials': r4['trials'], 'nontrivial_trials': r4['nontrivial_trials'],
               'W_ge1_nontrivial': r4['W_ge1_nontrivial'],
               'W_ge1_by_word': r4['W_ge1_by_word'], 'whist': r4['whist'],
               'hit_rate': 1.0,
               'reading': 'rate 1.0; by-word vector is [N,0,N,N] with N = nontrivial '
                          'trials; W is a point mass at 3'},
        'r5': {'arm': r5['arm'], 'rounds': 5, 'amask': 2, 'smask': 1,
               'trials': r5['trials'], 'nontrivial_trials': r5['nontrivial_trials'],
               'W_ge1_nontrivial': r5['W_ge1_nontrivial'],
               'W_ge1_by_word': r5['W_ge1_by_word'], 'whist': r5['whist'],
               'null_expectation_analytic': r5['null_expectation_analytic'],
               'observed_over_analytic_null': r5['W_ge1_nontrivial'] / r5['null_expectation_analytic'],
               'reading': 'a rare event, NOT rate 1.0; and the hits are spread over '
                          'ALL FOUR words INCLUDING the active word 1, which takes the '
                          'largest single count. No preservation structure survives.'},
    },
    'r1_r2_r3_readings': [
        {'arm': r['arm'], 'rounds': r['rounds'], 'amask': r['amask'], 'smask': r['smask'],
         'nontrivial_trials': r['nontrivial_trials'], 'W_ge1_by_word': r['W_ge1_by_word'],
         'whist': r['whist'], 'trivial_swaps_excluded': r['trivial_swaps_excluded']}
        for r in rows if r['rounds'] in (1, 2, 3)],
    'round_counts_actually_tested_in_this_task': sorted({r['rounds'] for r in rows}),
    'r6_and_above': 'NOT RUN IN THIS TASK. Dropped on the maximum_runs=30 cap and '
                    'named as dropped. Prior campaign data at r=6 and r=10 exists in '
                    'BATCH-002 and BATCH-006 and was not re-measured here.',
    'caveat_r2': 'Arm S2-r2 (r=2, amask=2, smask=1) returned nontrivial_trials = 0: '
                 'every trial was a trivial swap. That is itself a prediction of the '
                 'derivation (at r=2 a ciphertext-word-j swap IS a plaintext-diagonal-j '
                 'swap, and diagonal 0 is inactive when amask=2). Arm B1-r2-a2-s2 was '
                 'run with an intersecting smask to obtain a measurable r=2 reading.',
}

out['deliverable_3_derivation'] = {
    'outcome': 'DERIVED. A derivation is offered, stated as Proposition 1 with '
               'explicit hypotheses, and its load-bearing steps were verified '
               'mechanistically by independent code as well as by measurement.',
    'honest_labelling': 'The derivation was written down BEFORE the arms that test it '
                        '(PREREGISTRATION.md, frozen 2026-08-03T18:11:55Z), with the '
                        'single exception of the amask=1 TIMING arm which reproduced an '
                        'already-known reading. Every other cell is out of sample.',
    'proposition_1': {
        'statement': 'For the instrument cipher E^r = ARK_r . SR . SB . '
                     '[ARK_i . MC . SR . SB]_{i=r-1..1} . ARK_0, for ANY bijective '
                     'S-box, ANY key, ANY r in {1,2,3,4}, ANY nonempty active word set '
                     'A, and ANY swap mask smask in 1..14, on EVERY trial the yoyo '
                     'statistic satisfies W = 4 - |A|, and plaintext word j is '
                     'preserved if and only if j is not in A.',
        'hypotheses': [
            'H1. The S-box is a bijection on bytes. Nothing else about it is used - '
            'not its algebraic form, not its differential or linear profile.',
            'H2. MixColumns is invertible and acts within each column. Its branch '
            'number is NOT used.',
            'H3. AddRoundKey is bytewise and applies the same key byte to both members '
            'of the pair. The key schedule is irrelevant; any round keys work.',
            'H4. ShiftRows is the byte permutation (row,c) -> (row, c-row), so that '
            'PW[j] maps onto column j and CW[j] pulls back to column j.',
            'H5. The pair differs on exactly the diagonals in A, with at least one '
            'differing byte in each - which the instrument enforces by rejecting a '
            'draw that leaves an active word unchanged.',
            'H6. r <= 4. This is where the argument stops, and Step 4 says why.',
        ],
        'lemmas': {
            'L1_diagonal_to_column': 'SR maps PW[j] onto column j and its inverse maps '
                'CW[j] onto column j; so SR.SB carries diagonal j of its input to '
                'column j of its output, and column j of a post-SR state pulls back to '
                'the antidiagonal CW[j] of the pre-SR state.',
            'L2_bytewise_transparency': 'SB, SB^-1 and ARK are bytewise bijections, so '
                'they carry the ZERO PATTERN of a pair difference unchanged in both '
                'directions. They do NOT carry the difference VALUE.',
            'L3_column_transparency_of_MC': 'MC is invertible and column-local, so a '
                'column of the difference is zero iff the same column of the image '
                'difference is zero, and the difference value is carried linearly.',
            'L4_exchange_invariance': 'The yoyo swap sets c0[i],c1[i] := c1[i],c0[i], '
                'so c0 XOR c1 is unchanged at the swap point for ANY swap set. This is '
                'the fact that makes the statistic blind to smask at r<=4.',
        },
        'proof_steps': {
            'step_1_swap_pushback': 'A swap of ciphertext word j equals, by L2, a swap '
                'of the same positions of SR(SB(w_{r-1})); by L1 a swap of column j of '
                'SB(w_{r-1}); by L2 of column j of w_{r-1}; hence of column j of '
                'z_{r-1} = MC(y_{r-1}); by L3 of column j of y_{r-1} = SR(SB(w_{r-2})); '
                'by L1 and L2 of diagonal PW[j] of w_{r-2}; hence of diagonal PW[j] of '
                'z_{r-2}. It stops there: a diagonal meets all four columns, so it does '
                'not commute back through the next MC.',
            'step_2_forward_zero_pattern': 'By H5, L2 and L1, Delta(y_1) is supported '
                'on the columns in A and is nonzero in each; by L3 Delta(z_1) has '
                'column j nonzero iff j in A; by L1 and L2 again Delta(y_2) has its '
                'antidiagonal CW[j] nonzero iff j in A.',
            'step_3_backward_test': 'Plaintext word j is preserved iff the difference '
                'is zero on PW[j], iff (L2, L1) column j of Delta(y_1p) is zero, iff '
                '(L3) column j of Delta(z_1p) is zero.',
            'step_4_join': 'By Step 1 the swap acts at z_{r-2}, and by L4 '
                'Delta(z_{r-2}p) = Delta(z_{r-2}). For r=2 the swap point is the '
                'plaintext and the claim is immediate. For r=3 the swap point IS z_1, '
                'so Step 3 applies directly with zero S-box layers crossed. For r=4 the '
                'swap point is z_2, and Delta(y_2p) = MC^-1(Delta(z_2p)) = '
                'MC^-1(Delta(z_2)) = Delta(y_2) as an equality of difference VALUES, '
                'because only the linear L3 was crossed; one SB^-1 layer is then '
                'crossed, which by L2 preserves the zero pattern, and column j of '
                'Delta(z_1p) is zero iff CW[j] of Delta(y_2) is zero, iff j not in A by '
                'Step 2.',
        },
        'why_it_stops_at_r5': 'At r=5 the swap point is z_3. Delta(y_3p) = '
            'MC^-1(Delta(z_3)) is still known and the ZERO PATTERN of Delta(z_2p) still '
            'follows by L2. The argument then needs Delta(y_2p) = MC^-1(Delta(z_2p)); '
            'MC^-1 is linear in the difference VALUE, but crossing SB^-1 delivered only '
            'the zero PATTERN. That is the exact step that fails, and it fails first at '
            'r=5. This was written down before the r=5 arm was run.',
        'corollaries': [
            'C1. The r<=4 yoyo statistic is INDEPENDENT OF THE SWAP MASK. It carries no '
            'information about the swap at all: L4 makes the difference at the swap '
            'point invariant, and everything downstream of that in the argument uses '
            'only the forward difference. Confirmed by arms S3-s2/s4/s7/s13.',
            'C2. The statistic at r<=4 is a deterministic function of |A| alone. The '
            'reported rate 1.0 is not a rare-event measurement; it is a certainty.',
            'C3. The amask=15 null-object control the BATCH-006 validator ran, which '
            'drove the statistic to W=0 on every trial, is the |A|=4 case of W = 4-|A|. '
            'The control and the signal are the same formula evaluated at two points.',
            'C4. At r=2 the swap of ciphertext word j is exactly a swap of plaintext '
            'diagonal j, so if smask and amask are disjoint EVERY trial is a trivial '
            'swap. Confirmed unexpectedly by S2-r2 (16777216 of 16777216 trivial) and '
            'then predicted in advance and confirmed by B1-r2-a2-s2 (0 trivial).',
        ],
    },
    'independent_verification_of_the_argument': {
        'code': 'analysis/verify_derivation.py (byte-oriented reimplementation written '
                'for this task; the frozen instrument is T-table based)',
        'command': 'python3 analysis/verify_derivation.py 20260803',
        'exit_status': 0,
        'output': 'analysis/verify_derivation.json',
        'fips197_c1_kat_of_the_verifier': {
            'encrypt_match': ver['kat_fips197_c1_encrypt'],
            'ciphertext': ver['kat_fips197_c1_ciphertext'],
            'decrypt_match': ver['kat_fips197_c1_decrypt'],
            'roundtrip_r1_to_r6': ver['kat_roundtrip_r1_to_r6'],
        },
        'per_round': ver['per_round'],
        'reading': 'Step 1 (the pushback) was verified as FULL-STATE EQUALITY on 60/60 '
                   'random trials at each of r=2,3,4,5 - it is valid at r=5 too. L4 held '
                   '60/60 at every r. The value-level identity Delta(y_2p) = Delta(y_2), '
                   'which is what Step 4 needs, held 60/60 at r=2,3,4 and 0/60 at r=5. '
                   'Proposition 1 held on every non-trivial trial at r=1,2,3,4 with zero '
                   'violations, and collapsed at r=5. The measurement and the argument '
                   'therefore fail at the SAME place, and it is the place the argument '
                   'named in advance.',
        'caveat': 'This verifier shares the CONVENTION of the frozen instrument (it had '
                  'to, to test the same object) but not its code. It is independent in '
                  'implementation, not in specification. If the convention itself were '
                  'misread from BATCH-002, both would be wrong together; the geometry '
                  'output of the frozen instrument was checked against the PW/CW tables '
                  'used by the verifier and they agree.',
    },
}

out['deliverable_4_sbox_and_key_dependence'] = {
    'sbox_dependence': {
        'measured': True,
        'arms': [r['arm'] for r in rows if r['sbox_spec'] != 'aes'],
        'drawn_sbox_spec': 'rand:20260803702',
        'drawn_sbox_pin_pass': pin_rand['pin_pass'],
        'drawn_sbox_first8': pin_rand['sbox_first8'],
        'finding': 'The by-word structure is NOT AES-S-box-specific. Arms S4-rand-a4, '
                   'S4-rand-a15 and S4-rand-a2-s7 under a drawn bijective S-box give '
                   'byte-identical by-word vectors and histograms to their AES-S-box '
                   'counterparts.',
        'derivation_agreement': 'Predicted by hypothesis H1: the argument uses only '
                                'bijectivity of the S-box.',
    },
    'key_dependence': {
        'measured': True,
        'arms': [r['arm'] for r in rows if r['seed'] == 20260803999],
        'keys': sorted({r['key_hex'] for r in rows}),
        'finding': 'The by-word structure is key-independent across the two keys '
                   'tested. S4-key2-a4 and S4-key2-a2 under a different key reproduce '
                   'the same vectors.',
        'derivation_agreement': 'Predicted by hypothesis H3: the argument never uses '
                                'the key schedule.',
        'CONFOUND_RECORDED': 'The instrument derives the key from the `seed` argument, '
                             'which ALSO seeds the trial stream. A key change is '
                             'therefore not independent of the plaintext stream. Only '
                             'TWO keys were tested here. This is a narrow test and is '
                             'not reported as key-independence in general.',
    },
}

out['prior_data_cited_not_remeasured'] = {
    'rule': 'A claim that something has never been measured is an empirical claim '
            'about the repository (CORR-20260803-c92db5), so the paths searched are '
            'named and prior measurements are cited rather than re-run.',
    'paths_searched': [
        'coordination/goals/GOAL-AES-003/batches/BATCH-002/tasks/*/',
        'coordination/goals/GOAL-AES-003/batches/BATCH-004/tasks/TASK-20260803-367b1b/ (runs/, src/, RESULTS.json)',
        'coordination/goals/GOAL-AES-003/batches/BATCH-005/tasks/TASK-20260803-48a239/runs/*.json',
        'coordination/goals/GOAL-AES-003/batches/BATCH-006/tasks/TASK-20260803-0764fc/',
        'coordination/goals/GOAL-AES-003/batches/BATCH-006/tasks/TASK-20260803-a13de8/validation_report.yaml',
        'repo-wide grep for the two instrument sha256 values',
    ],
    'r5_arms_already_on_disk': {
        'path': 'coordination/goals/GOAL-AES-003/batches/BATCH-005/tasks/TASK-20260803-48a239/runs/D-{AES,R1,R2}-K{1,2,3}.json',
        'count': 9,
        'parameters': 'r=5, amask=1, smask=1, log2N=30; D-R1 and D-R2 are drawn '
                      'S-boxes, K1/K2/K3 are three keys',
        'relevance': 'These already cover r=5 under drawn S-boxes and multiple keys, '
                     'and their by-word vectors (e.g. [4,4,2,4], [6,5,1,2], [5,5,5,7]) '
                     'already show r=5 hits landing on all four words including the '
                     'active word 0. This task adds the amask=2 case at 2^31, which '
                     'agrees.',
    },
}

out['deviations_and_failures'] = [
    {'id': 'DEV-1', 'classification': 'implementation_error',
     'what': 'My driver run_arms.sh invoked `yoyo_sbox_v2 pin rand:20260803702` '
             'without the mandatory seed argument; the instrument dereferenced a NULL '
             'argv[3] and segfaulted (exit 139).',
     'whose': 'MY analysis driver. The frozen instrument was not modified and its own '
              'behaviour is a missing-argument crash, which is a robustness note about '
              'the instrument, not a measurement defect.',
     'resolution': 'Driver corrected, pin re-run, exit 0, pin_pass true. The crashed '
                   'invocation is retained in runs/commands.txt and counted against the '
                   'run cap. Nothing was discarded.'},
    {'id': 'DEV-2', 'classification': 'negative_observation',
     'what': 'Arm S2-r2 produced nontrivial_trials = 0 - every one of 2^24 trials was '
             'a trivial swap - so that arm yields no by-word vector.',
     'resolution': 'Not a failure: it is a sharp confirmation of the pushback step. '
                   'Predicted in Addendum A before B1-r2-a2-s2 was run, and B1 then '
                   'gave 0 trivial swaps with the intersecting mask as predicted. Both '
                   'arms are reported.'},
    {'id': 'DEV-3', 'classification': 'protocol_note',
     'what': 'arm_id 63 was used twice: S3-s13 (seed 20260803701) and S4-key2-a4 '
             '(seed 20260803999).',
     'resolution': 'No collision in practice - thread seeds are derived from seed XOR '
                   'arm_id XOR thread index, and the seeds differ, so the two arms have '
                   'disjoint thread seeds. Recorded rather than hidden.'},
    {'id': 'DEV-4', 'classification': 'protocol_note',
     'what': 'One instrument invocation (the TIMING arm) was made for throughput '
             'scoping BEFORE PREREGISTRATION.md was frozen.',
     'resolution': 'Disclosed in PREREGISTRATION.md "Prior acts", reported as an arm in '
                   'this file, and its cell (r=4, amask=1) is flagged as NOT out of '
                   'sample. It reproduced an already-published reading.'},
]

out['checks_not_run'] = [
    {'check': 'Adapter probe of the resolved model identifier',
     'reason': 'No adapter available in this harness; model_verified is false.'},
    {'check': 'r=6 and higher round counts',
     'reason': 'Dropped on the maximum_runs=30 cap. Named as dropped.'},
    {'check': 'r=5 under a drawn S-box or a second key, run by this task',
     'reason': 'Dropped on the maximum_runs=30 cap. Nine such arms already exist in '
               'BATCH-005 and are cited above instead.'},
    {'check': 'A larger-N confirmation of any r<=4 cell beyond 2^24',
     'reason': 'Dropped on the run cap. Not needed for a deterministic statistic, but '
               'the prior 2^31 arm at amask=1 in BATCH-004/006 supplies one.'},
    {'check': 'Peak RSS measurement',
     'reason': 'Not instrumented; no number is reported rather than an estimate.'},
    {'check': 'Any test of a non-bijective S-box',
     'reason': 'The instrument refuses to measure a non-bijective S-box (exit 4), and '
               'hypothesis H1 is therefore untested from below.'},
    {'check': 'Independent re-execution by a second agent',
     'reason': 'Out of scope for a producer task; this is what the reviewer gate is for.'},
    {'check': 'BIT-FOR-BIT REPRODUCTION of a recorded command by re-running it',
     'reason': 'NOT RUN, and this is a real gap in the completion gate. It would have '
               'been the 31st invocation of the frozen instrument against a hard '
               'maximum_runs=30, and a hard budget limit is not to be exceeded for '
               'convenience. The cap was reached because I took the STRICT reading in '
               'which geom, both pins and the one crashed pin all count as runs; under '
               'the narrower reading in which only `arm` invocations count, 26 of 30 '
               'were used and the check would have fit. I flag the ambiguity rather '
               'than resolve it in my own favour, and leave the re-run to the reviewer '
               'or to a Coordinator amendment. What partially substitutes: the same '
               'cell was measured five further times under varying smask and key '
               '(S1-a2, S3-s2, S3-s4, S3-s7, S3-s13, S4-key2-a2) with byte-identical '
               'by-word vectors, and the independent verifier reproduces the structure '
               'from a separate implementation. Neither is the same thing as re-running '
               'the recorded command and getting the recorded bytes.'},
]

out['scope_and_boundaries'] = [
    'TOY TIER. Reduced-round AES-128 in a software T-table reimplementation, r in '
    '{1,2,3,4,5}, one machine, 2^24 to 2^31 trials per arm, two keys, one drawn S-box '
    'in this task. Nothing here is a statement about full-round or deployed AES.',
    'No comparison to published cryptanalysis is made in either direction (RQ-AES-003 R3).',
    'The "excess 2^30" figure at r<=4 is the ARITHMETIC CEILING of the statistic - rate '
    '1.0 over a modeled null of 2^-30 - and is never quoted here as a magnitude. '
    'Proposition 1 explains why the rate is 1.0: at r<=4 the event is certain, not rare.',
    'Proposition 1 is a statement about THIS statistic under THIS cipher convention at '
    'r<=4. It says nothing about the security of anything.',
    'The executor records observations. Whether Proposition 1 is accepted as a proof, '
    'and what it implies for the campaign, is for the Reviewer and Coordinator.',
]

out['what_would_falsify_this'] = [
    'A single r<=4 trial, under any bijective S-box, key, amask and smask, in which a '
    'word not in A fails to be preserved or a word in A is preserved. Proposition 1 is '
    'universally quantified over trials and has no probabilistic escape.',
    'A demonstration that the pushback in Step 1 does not hold for some smask - it was '
    'checked as full-state equality on 60/60 random trials per round count, not proved '
    'exhaustively.',
    'A convention mismatch: if PW/CW or the round structure differ from BATCH-002, both '
    'the instrument and the verifier would be measuring the wrong object together.',
]

out['self_check'] = {}

with open(os.path.join(D, 'RESULTS.json'), 'w') as f:
    json.dump(out, f, indent=1)

# ---- the mandated json.load self-check on the emitted file ----
with open(os.path.join(D, 'RESULTS.json')) as f:
    reloaded = json.load(f)
reloaded['self_check'] = {
    'json_load_on_own_file': 'PASS',
    'json_load_performed_at_utc': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    'top_level_keys': len(reloaded),
    'arm_rows': len(reloaded['arms']),
    'arms_matching_proposition_1_at_r_le_4':
        sum(1 for r in reloaded['arms'] if r['rounds'] <= 4 and r['matches_proposition_1']),
    'arm_rows_at_r_le_4': sum(1 for r in reloaded['arms'] if r['rounds'] <= 4),
    'raw_vs_summary_agreement': 'Every arm row in this file was read programmatically '
        'from runs/<arm>.json by build_results.py; no arm number was typed by hand.',
}
with open(os.path.join(D, 'RESULTS.json'), 'w') as f:
    json.dump(reloaded, f, indent=1)
with open(os.path.join(D, 'RESULTS.json')) as f:
    final = json.load(f)
print('RESULTS.json rewritten and re-parsed: keys=%d arms=%d selfcheck=%s'
      % (len(final), len(final['arms']), final['self_check']['json_load_on_own_file']))
print('r<=4 arms matching Proposition 1: %d/%d'
      % (final['self_check']['arms_matching_proposition_1_at_r_le_4'],
         final['self_check']['arm_rows_at_r_le_4']))
