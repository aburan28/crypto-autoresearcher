"""Fixed paired finite stream, with all attempted statuses retained in source blocks."""
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import random
import sys
from time import perf_counter, process_time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/prym_experiment_design_20261019/implementation'))
from independent import verify_fixture, verify_row
from projection import certificate, projection, row_project
from relations import Context, Rank, uid
from witness import controls, transported

STATUS = {'source_no_nonzero_rational_lift': 'S',
          'exceptional_interpolation_x_zero': 'D', 'duplicate_interpolation_x': 'D',
          'exceptional_pole_order': 'P', 'residual_not_two_distinct_rational_roots': 'R',
          'intersection_not_squarefree': 'X', 'residual_endpoint_outside_factor_base': 'B',
          'canonical_alias': 'A', None: '+'}


def schedule(fixture, seed, config):
    sources = list(range(1, min(config['public_source_max'], fixture['r'] - 1) + 1))
    random.Random(f"{config['domain']}|sources|{fixture['uid']}|{seed}").shuffle(sources)
    pool = list(product(list(combinations(range(len(fixture['factor_base'])), 3)),
                        list(product(range(4), repeat=3))))
    rng = random.Random(f"{config['domain']}|tuples|{fixture['uid']}|{seed}")
    sample = {a: rng.sample(range(len(pool)), config['sample_branches_per_source']) for a in sources}
    return sources, pool, sample


def nullspace(rank):
    """Right-kernel basis of the finite matrix; no universal rank-cap inference."""
    out = []
    for free in range(rank.columns):
        if free in rank.pivots:
            continue
        vector = [0] * rank.columns
        vector[free] = 1
        for pivot, row in sorted(rank.pivots.items(), reverse=True):
            vector[pivot] = -sum(x*y for x, y in zip(row[:-1], vector)) % rank.modulus
        out.append(vector)
    return out


def collect(fixture, seed, config, arm, event):
    start, cpu = perf_counter(), process_time()
    context = Context(fixture)
    sources, pool, sampled = schedule(fixture, seed, config)
    projected = projection(context, sources)
    rank = Rank(len(projected['unknown_columns']), context.r)
    rows, row_attempts, progress, checkpoints, aa = [], [], [], [], []
    seen, reasons, attempts, first = set(), Counter(), 0, None
    for source in sources:
        branches = sampled[source] if arm == 'sample64' else range(len(pool))
        statuses, digest = [], sha256()
        for branch in branches:
            attempts += 1
            triple, options = pool[branch]
            descriptor, reason = context.descriptor(source, triple, options)
            identity = None
            if descriptor is not None:
                identity = uid(context.canonical_identity(descriptor))
                context.f.counts['candidate_hashes'] += 1
                context.f.counts['candidate_digest_bytes'] += 32
                if identity in seen:
                    reason = 'canonical_alias'
                else:
                    seen.add(identity)
                    row, reason = context.construct(descriptor)
                    if row is not None:
                        verify_row(fixture, row)
                        aa.append(transported(fixture, row, seed))
                        rows.append(row)
                        row_attempts.append(attempts)
                        independent = rank.add(*row_project(row, projected, context.r))
                        if independent:
                            point = dict(attempt=attempts, accepted_rows=len(rows), rank=len(rank.pivots),
                                         operation_vector=dict(context.f.counts), matrix_units=rank.ops)
                            progress.append(point)
                            if rank.columns > 0 and len(rank.pivots) == rank.columns and first is None:
                                first = point
            status = STATUS[reason]
            statuses.append(status)
            reasons[status] += 1
            digest.update(json.dumps([source, branch, identity, status], separators=(',', ':')).encode() + b'\n')
        checkpoint = dict(source_scalar=source, attempt=attempts, accepted_rows=len(rows),
                          rank=len(rank.pivots), operation_vector=dict(context.f.counts), matrix_units=rank.ops)
        checkpoints.append(checkpoint)
        event(dict(schema='prym-census-source-block/v1', curve_uid=fixture['uid'], seed=seed,
                   arm=arm, scalar=source, statuses=''.join(statuses),
                   attempt_digest=digest.hexdigest(), checkpoint=checkpoint))
    final = certificate(rows, projected, context.r)
    return dict(curve_uid=fixture['uid'], p=fixture['p'], seed=seed, arm=arm,
                attempts=attempts, reasons=dict(reasons), distinct_candidates=len(seen),
                rows=rows, row_attempts=row_attempts, projection=final, nullspace=nullspace(rank),
                rank_progress=progress, source_checkpoints=checkpoints, first_full_rank=first,
                transported_witness_hashes=aa, attack_operation_vector=dict(context.f.counts),
                online_matrix_units=rank.ops, final_certificate_matrix_units=final['matrix_operation_units'],
                cache_entries=dict(source=len(context.source_cache), auxiliary=len(context.aux_cache),
                                   canonical_identities=len(seen)),
                qualifying_unknown_rank=rank.columns > 0 and len(rank.pivots) == rank.columns,
                wall_seconds=perf_counter()-start, cpu_seconds=process_time()-cpu,
                checker_cost_included_in_attack_vector=False)


def run(config, panel, event):
    start, cpu = perf_counter(), process_time()
    cells = []
    for fixture in panel['fixtures']:
        verify_fixture(fixture)
        for seed in config['seeds']:
            for arm in config['arms']:
                cell = collect(fixture, seed, config, arm, event)
                cells.append(cell)
                print(json.dumps(dict(p=fixture['p'], curve_uid=fixture['uid'], arm=arm,
                                      attempts=cell['attempts'], rows=len(cell['rows']),
                                      rank=cell['projection']['rank'], U=cell['projection']['U'])), flush=True)
    return dict(schema='prym-rank-census/v1', complete=True, cells=cells, controls=controls(),
                input_construction_costs=panel['search_trace'], secret_labels_present=False,
                status_codes={str(k): v for k, v in STATUS.items()},
                wall_seconds=perf_counter()-start, cpu_seconds=process_time()-cpu,
                scope='Finite public-source collector diagnostic; no comparative ECDLP cost claim.',
                execution_proof=dict(present=False, replay_is_not_prescribed_computation_proof=True))
