"""Full width collector. CLI execution requires the future exact native approval.

Direct collect() is limited to marked p<=211 planted software fixtures unless
the native runtime supplies its post-admission capability. There is no pilot,
sample, branch-limit or early-stop mode.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys
from time import perf_counter, process_time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'research/prym_experiment_design_20261019/implementation'))
from relations import Context, Rank, uid
from independent import verify_row

STATUS = {'source_no_nonzero_rational_lift': 'S',
          'exceptional_interpolation_x_zero': 'D', 'duplicate_interpolation_x': 'D',
          'exceptional_pole_order': 'P', 'residual_not_two_distinct_rational_roots': 'R',
          'intersection_not_squarefree': 'X', 'residual_endpoint_outside_factor_base': 'B',
          'canonical_alias': 'A', None: '+'}
_NATIVE_CAPABILITY = object()


def public_projection(context, sources):
    p, r = context.p, context.r
    known, derivations = {}, {}
    for scalar in sources:
        image = context.e.mul(scalar, context.P)
        if image is None:
            continue
        key = (image[0], min(image[1], -image[1] % p))
        sign = 1 if image == key else -1
        value = sign*scalar % r
        if key in known and known[key] != value:
            raise ValueError('conflicting public anchors')
        if key not in known:
            known[key] = value
            derivations[key] = dict(point=list(key), scalar=value, public_source=scalar, sign=sign)
    atom_keys = {None if atom is None else (atom[0], min(atom[1], -atom[1] % p))
                 for atom in context.base}
    unknown = sorted(k for k in atom_keys if k is not None and k not in known)
    mapping = []
    for atom in context.base:
        if atom is None:
            mapping.append(['zero'])
            continue
        key = (atom[0], min(atom[1], -atom[1] % p))
        sign = 1 if atom == key else -1
        mapping.append(['known', sign*known[key] % r] if key in known else
                       ['unknown', unknown.index(key), sign])
    return dict(U=len(unknown), unknown_points=[list(k) for k in unknown],
                native_to_projected=mapping,
                public_derivations=[v for k, v in derivations.items() if k in atom_keys])


def project(row, projection, r):
    output, rhs = [0]*projection['U'], row['source_scalar'] % r
    for value, mapping in zip(row['coefficients'], projection['native_to_projected']):
        if mapping[0] == 'known':
            rhs = (rhs-value*mapping[1]) % r
        elif mapping[0] == 'unknown':
            output[mapping[1]] = (output[mapping[1]]+value*mapping[2]) % r
    return output, rhs


def finite_certificate(rows, projection, r):
    rank = Rank(projection['U'], r)
    indices, M, b = [], [], []
    for i, row in enumerate(rows):
        coefficients, rhs = project(row, projection, r)
        M.append(coefficients)
        b.append(rhs)
        if rank.add(coefficients, rhs):
            indices.append(i)
    kernel = []
    for free in range(rank.columns):
        if free in rank.pivots:
            continue
        vector = [0]*rank.columns
        vector[free] = 1
        for pivot, row in sorted(rank.pivots.items(), reverse=True):
            vector[pivot] = -sum(x*y for x, y in zip(row[:-1], vector)) % r
        kernel.append(vector)
    return dict(**projection, rank=len(rank.pivots), augmented_rank=len(rank.pivots),
                nullity=rank.columns-len(rank.pivots), consistent=True,
                projected_rows=M, rhs=b, independent_row_indices=indices,
                pivots={str(k): v for k, v in rank.pivots.items()},
                right_kernel=kernel, solution=rank.solve(),
                matrix_operation_units=rank.ops,
                all_columns_publicly_known=rank.columns == 0)


def transport(fixture, row):
    """Fixed signed permutation plus per-atom deck change; no target oracle."""
    n, p, r = len(fixture['factor_base']), fixture['p'], fixture['r']
    permutation = list(reversed(range(n)))
    inverse = {old: new for new, old in enumerate(permutation)}
    other, witness = deepcopy(fixture), deepcopy(row)
    signs = {old: -1 if old % 2 else 1 for old in range(n)}
    decks = {old: -1 if old % 3 else 1 for old in range(n)}
    other['factor_base'] = []
    for old in permutation:
        atom = fixture['factor_base'][old]
        x, y = atom['lift']
        other['factor_base'].append(dict(point=[atom['point'][0], signs[old]*y % p],
                                        lift=[decks[old]*x % p, signs[old]*y % p]))
    witness['coefficients'] = [signs[j]*row['coefficients'][j] % r for j in permutation]
    witness['base_labels'] = []
    for j, sign, option in row['base_labels']:
        new_sign = sign*signs[j]
        new_deck = (-1 if option & 2 else 1)*decks[j]
        witness['base_labels'].append([inverse[j], new_sign,
                                      (1 if new_sign == -1 else 0)+(2 if new_deck == -1 else 0)])
    verify_row(other, witness)
    return other, witness


def collect(fixture, sources, event, *, capability=None):
    if capability is not _NATIVE_CAPABILITY and not (
            fixture.get('software_control') is True and fixture['p'] <= 211):
        raise ValueError('target collection requires exact native admission; only marked small planted fixtures allowed directly')
    if len(set(sources)) != len(sources) or any(not 0 < a < fixture['r'] for a in sources):
        raise ValueError('invalid public source schedule')
    start, cpu = perf_counter(), process_time()
    context = Context(fixture)
    projected = public_projection(context, sources)
    stage_vectors = {'public_projection_setup': Counter(context.f.counts),
                     'source_lift_and_descriptor': Counter(),
                     'cubic_residual_normalization': Counter()}
    online = Rank(projected['U'], fixture['r'])
    triples = list(combinations(range(len(context.base)), 3))
    options = list(product(range(4), repeat=3))
    rows, locations, aa, progress, checkpoints = [], [], [], [], []
    seen, counts, attempts, first = set(), Counter(), 0, None
    storage = Counter()
    inline_wall, inline_cpu = 0.0, 0.0
    try:
        for source in sources:
            statuses, commitment = [], sha256()
            for triple_index, triple in enumerate(triples):
                for option_index, option in enumerate(options):
                    branch = triple_index*64+option_index
                    attempts += 1
                    before = Counter(context.f.counts)
                    descriptor, reason = context.descriptor(source, triple, option)
                    stage_vectors['source_lift_and_descriptor'].update(Counter(context.f.counts)-before)
                    identity = None
                    if descriptor is not None:
                        identity = uid(context.canonical_identity(descriptor))
                        context.f.counts['candidate_hashes'] += 1
                        context.f.counts['candidate_digest_bytes'] += 32
                        if identity in seen:
                            reason = 'canonical_alias'
                        else:
                            seen.add(identity)
                            before = Counter(context.f.counts)
                            row, reason = context.construct(descriptor)
                            stage_vectors['cubic_residual_normalization'].update(Counter(context.f.counts)-before)
                            if row is not None:
                                check_start, check_cpu = perf_counter(), process_time()
                                verify_row(fixture, row)
                                other, transported = transport(fixture, row)
                                if project(row, projected, fixture['r']) != project(
                                        transported, public_projection(Context(other), sources), fixture['r']):
                                    raise ValueError('signed/deck A/A projection failed')
                                inline_wall += perf_counter()-check_start
                                inline_cpu += process_time()-check_cpu
                                aa.append(uid(transported))
                                rows.append(row)
                                locations.append(attempts)
                                # Write each accepted witness immediately so a later
                                # arithmetic/resource failure does not erase earlier
                                # accepted bytes from this unfinished source block.
                                event(dict(schema='prym-width-accepted-witness/v1',
                                           curve_uid=fixture['uid'], scalar=source,
                                           attempt=attempts, row_index=len(rows)-1,
                                           row=row, transported_witness_sha256=aa[-1]))
                                if online.add(*project(row, projected, fixture['r'])):
                                    point = dict(attempt=attempts, accepted_rows=len(rows), rank=len(online.pivots),
                                                 operation_vector=dict(context.f.counts), matrix_units=online.ops)
                                    progress.append(point)
                                    if online.columns > 0 and len(online.pivots) == online.columns and first is None:
                                        first = point
                    status = STATUS[reason]
                    statuses.append(status)
                    counts[status] += 1
                    payload = json.dumps([source, branch, identity, status], separators=(',', ':')).encode()+b'\n'
                    commitment.update(payload)
                    storage['attempt_digest_input_bytes'] += len(payload)
                    storage['attempt_digest_updates'] += 1
            checkpoint = dict(source_scalar=source, attempt=attempts, accepted_rows=len(rows),
                              rank=len(online.pivots), operation_vector=dict(context.f.counts), matrix_units=online.ops)
            checkpoints.append(checkpoint)
            event(dict(schema='prym-width-source-block/v1', curve_uid=fixture['uid'], seed=0,
                       arm='m16_full35840', scalar=source, statuses=''.join(statuses),
                       attempt_digest=commitment.hexdigest(), checkpoint=checkpoint))
            storage['source_blocks'] += 1
            storage['status_bytes'] += len(statuses)
    except BaseException as exc:
        # A partial source remains explicitly censored. Retain its statuses and
        # descriptor/error location; successful witness bytes were emitted at once.
        event(dict(schema='prym-width-partial-source-block/v1', curve_uid=fixture['uid'],
                   scalar=source, attempted=attempts, statuses=''.join(statuses),
                   completed_status_digest=commitment.hexdigest(),
                   last_descriptor=dict(branch=branch, triple=list(triple), options=list(option)),
                   accepted_rows_so_far=len(rows), error=repr(exc),
                   failure_class='resource_exhaustion' if isinstance(exc, MemoryError) else 'implementation_or_infrastructure_error',
                   operation_vector=dict(context.f.counts), matrix_units=online.ops))
        raise
    final = finite_certificate(rows, projected, fixture['r'])
    return dict(curve_uid=fixture['uid'], ec1_curve_uid=fixture.get('ec1', {}).get('curve_uid'),
                p=fixture['p'], b=fixture['b'], seed=0, arm='m16_full35840', attempts=attempts,
                source_order=sources, reasons=dict(counts), distinct_candidates=len(seen),
                rows=rows, row_attempts=locations, projection=final,
                rank_progress=progress, source_checkpoints=checkpoints, first_full_rank=first,
                transported_witness_hashes=aa, attack_operation_vector=dict(context.f.counts),
                attack_stage_operation_vectors={k: dict(v) for k, v in stage_vectors.items()},
                online_matrix_units=online.ops, final_certificate_matrix_units=final['matrix_operation_units'],
                storage_operation_vector=dict(storage),
                inline_checker_wall_seconds=inline_wall, inline_checker_cpu_seconds=inline_cpu,
                cache_entries=dict(source=len(context.source_cache), auxiliary=len(context.aux_cache), canonical_identities=len(seen)),
                wall_seconds=perf_counter()-start, cpu_seconds=process_time()-cpu,
                checker_cost_included_in_attack_vector=False,
                cost_scope='Partial S: field/group/pow-call/hash and matrix units. Pow internals, Python bookkeeping, byte movement, compression/upload/readback and independent counter reconciliation excluded. Wall includes inline verification; inline times recorded separately.')


def run(config, panel, event, *, capability=None):
    if capability is not _NATIVE_CAPABILITY:
        raise ValueError('no native admission capability')
    from check_inputs import validate
    validate(config, panel)
    start, cpu = perf_counter(), process_time()
    artifact_counters = Counter()

    def counted_event(record):
        payload = json.dumps(record, sort_keys=True, separators=(',', ':')).encode()+b'\n'
        artifact_counters['events_jsonl_encoded_bytes'] += len(payload)
        categories = {'prym-width-source-block/v1': 'source_blocks_written',
                      'prym-width-accepted-witness/v1': 'accepted_witnesses_written',
                      'prym-width-partial-source-block/v1': 'partial_source_blocks_written'}
        artifact_counters[categories[record['schema']]] += 1
        event(record)

    cells = [collect(f, f['width_binding']['source_order'], counted_event, capability=capability)
             for f in panel['fixtures']]
    return dict(schema='prym-factor-base-width/v1', complete=True, cells=cells,
                secret_labels_present=False, new_m8_attempts=0,
                input_construction_costs=[f['construction_counts'] for f in panel['fixtures']],
                producer_artifact_counters=dict(artifact_counters),
                historical_reference_sha256=panel['historical_reference_sha256'],
                wall_seconds=perf_counter()-start, cpu_seconds=process_time()-cpu,
                scope='Finite conditional width observation only; raw partial S; no speedup, security or general rank claim.',
                execution_proof=dict(present=False, replay_is_not_prescribed_computation_proof=True))


if __name__ == '__main__':
    from runtime_width import main
    raise SystemExit(main())
