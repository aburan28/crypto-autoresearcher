"""Prospective F3 m=4 P-256 implementation. No panel runs at import or --help.

Execution requires a frozen protocol.json and the repository's real checkpoint
gate. Root must separately release Phase B. No skip-gate option exists.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
P = int('ffffffff00000001000000000000000000000000ffffffffffffffffffffffff', 16)
A = P - 3
B = int('5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b', 16)
R = int('ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551', 16)
G = (int('6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296', 16),
     int('4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5', 16))
SOURCE_FILES = ('run.py', 'oracle.py', 'analysis.py', 'export.py', 'curve-record.json')
PANEL_SEED = 2026102603
PARTITION_SIZE = 8


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def portable(value):
    """Keep large exact integers safe for JSON consumers with binary64 numbers."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and abs(value) > 2**53-1:
        return str(value)
    if isinstance(value, dict):
        return {k: portable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [portable(v) for v in value]
    return value


def write_json(path, value):
    with path.open('x') as f:
        json.dump(portable(value), f, indent=2)
        f.write('\n')


class Affine:
    def __init__(self, event=None):
        self.counts = Counter()
        self.event = event

    def negate(self, point):
        self.counts['negation_calls'] += 1
        return None if point is None else (point[0], -point[1] % P)

    def valid(self, point):
        self.counts['on_curve_tests'] += 1
        return point is None or (0 <= point[0] < P and 0 <= point[1] < P and
                                (point[1]*point[1]-point[0]**3-A*point[0]-B) % P == 0)

    def add(self, point, other):
        self.counts['addition_calls'] += 1
        if point is None:
            return other
        if other is None:
            return point
        x, y = point
        u, v = other
        if x == u:
            if (y+v) % P == 0:
                return None
            self.counts['doubling_calls'] += 1
            numerator, denominator = (3*x*x+A) % P, 2*y % P
        else:
            numerator, denominator = (v-y) % P, (u-x) % P
        self.counts['field_inversions'] += 1
        slope = numerator*pow(denominator, -1, P) % P
        z = (slope*slope-x-u) % P
        return z, (slope*(x-z)-y) % P

    def multiply(self, scalar, point):
        self.counts['scalar_multiplications'] += 1
        if scalar < 0:
            scalar, point = -scalar, self.negate(point)
        result = None
        while scalar:
            if scalar & 1:
                result = self.add(result, point)
            point = self.add(point, point)
            scalar >>= 1
        return result

    def labelled(self, alpha, beta, target):
        self.counts['label_point_evaluations'] += 1
        return self.add(self.multiply(alpha % R, G), self.multiply(beta % R, target))

    def hashed_scalar(self, tag):
        self.counts['sha256_calls'] += 1
        return int.from_bytes(sha256(tag.encode()).digest(), 'big') % R

    def hash_point(self, tag):
        self.counts['sha256_calls'] += 1
        x = int.from_bytes(sha256(tag.encode()).digest(), 'big') % P
        rejected = []
        for attempt in range(1024):
            self.counts['hash_to_point_attempts'] += 1
            self.counts['square_root_exponentiations'] += 1
            rhs = (x*x*x+A*x+B) % P
            y = pow(rhs, (P+1)//4, P)
            if self.event:
                self.event({'stage': 'target_draw', 'attempt': attempt, 'x': x,
                            'accepted': y*y % P == rhs})
            if y*y % P == rhs:
                return (x, min(y, P-y)), rejected
            rejected.append({'attempt': attempt, 'x': x, 'reason': 'quadratic_nonresidue'})
            x = (x+1) % P
        raise RuntimeError('fixed hash-to-point guard reached; target remains unknown')


def generate_base(arithmetic, target, seed, count=32):
    accepted, draws, used = [], [], set()
    for attempt in range(4096):
        alpha = arithmetic.hashed_scalar(f'F3-pass2:{seed}:draw:{attempt}:a')
        beta = arithmetic.hashed_scalar(f'F3-pass2:{seed}:draw:{attempt}:b')
        point = arithmetic.labelled(alpha, beta, target)
        reason = 'identity' if point is None else 'repeated_x_including_inverse' if point[0] in used else None
        draws.append({'attempt': attempt, 'a': alpha, 'b': beta,
                      'point': point, 'accepted': reason is None, 'reason': reason})
        if arithmetic.event:
            arithmetic.event({'stage': 'base_draw', **draws[-1]})
        if reason is None:
            used.add(point[0])
            accepted.append({'a': alpha, 'b': beta, 'point': point})
            if len(accepted) == count:
                return accepted, draws
    raise RuntimeError('fixed base-construction guard reached; panel not completed')


def plant_control(arithmetic, base, target, witness, seed):
    """Alter only the last label; disclose every attempt and witness access."""
    fixed = (0, 8, 16)
    partial_a = sum(base[i]['a'] for i in fixed) % R
    partial_b = sum(base[i]['b'] for i in fixed) % R
    used = {row['point'][0] for row in base[:-1]}
    attempts = []
    for attempt in range(128):
        if witness is None:
            # Deterministic zero-information relation; alternate fixed selection
            # is unnecessary because this point changes only with the base seed.
            beta, alpha = -partial_b % R, -partial_a % R
        else:
            beta = arithmetic.hashed_scalar(f'F3-pass2:{seed}:plant:{attempt}:b')
            net_b = (partial_b+beta) % R
            alpha = (-partial_a-witness*net_b) % R
        point = arithmetic.labelled(alpha, beta, target)
        reason = 'identity' if point is None else 'repeated_x_including_inverse' if point[0] in used else None
        if witness is not None and (partial_b+beta) % R == 0:
            reason = 'zero_target_coefficient'
        attempts.append({'attempt': attempt, 'a': alpha, 'b': beta,
                         'point': point, 'accepted': reason is None, 'reason': reason})
        if arithmetic.event:
            arithmetic.event({'stage': 'control_plant_draw', **attempts[-1]})
        if reason is None:
            base[-1] = {'a': alpha, 'b': beta, 'point': point}
            return attempts
        if witness is None:
            break
    raise RuntimeError('fixed constructed-control guard reached; control not completed')


def validate_search_input(arithmetic, points, partitions):
    if len(partitions) != 4 or not points:
        raise ValueError('four nonempty partitions required')
    if any(not part for part in partitions):
        raise ValueError('empty partition')
    flat = [i for part in partitions for i in part]
    if any(not isinstance(i, int) or isinstance(i, bool) for i in flat):
        raise ValueError('integer indices required')
    if len(set(flat)) != len(flat) or set(flat) != set(range(len(points))):
        raise ValueError('partitions must be a disjoint complete cover')
    if any(q is None or not arithmetic.valid(q) for q in points):
        raise ValueError('finite on-curve points required')
    if len({q[0] for q in points}) != len(points):
        raise ValueError('globally distinct x coordinates required')


def search(arithmetic, points, partitions):
    """Labels, target and target witness are deliberately absent from this API."""
    validate_search_input(arithmetic, points, partitions)
    left, pair_counts, relations = {}, Counter(), []
    for i, j in product(partitions[0], partitions[1]):
        for sign in (1, -1):
            q = arithmetic.add(points[i], points[j] if sign == 1 else arithmetic.negate(points[j]))
            if q is None:
                raise AssertionError('distinct-x premise violated by identity pair')
            left.setdefault(q[0], []).append((i, j, sign, q))
            pair_counts['left_pair_evaluations'] += 1
    pair_counts['table_entries'] = sum(map(len, left.values()))
    pair_counts['table_buckets'] = len(left)
    for k, l in product(partitions[2], partitions[3]):
        for sign in (1, -1):
            q = arithmetic.add(points[k], points[l] if sign == 1 else arithmetic.negate(points[l]))
            if q is None:
                raise AssertionError('distinct-x premise violated by identity pair')
            pair_counts['right_pair_evaluations'] += 1
            pair_counts['membership_probes'] += 1
            for i, j, left_sign, match in left.get(q[0], ()):
                pair_counts['coordinate_bucket_joins'] += 1
                if match == q:
                    relations.append({'indices': [i, j, k, l],
                                      'signs': [1, left_sign, -1, -sign]})
                if match == arithmetic.negate(q):
                    relations.append({'indices': [i, j, k, l],
                                      'signs': [1, left_sign, 1, sign]})
    relations.sort(key=lambda row: (row['indices'], row['signs']))
    return {'relations': relations, 'counters': dict(pair_counts),
            'complete_for': 'one point per fixed partition; signs modulo simultaneous negation'}


def assess(arithmetic, base, target, relation):
    indices, signs = relation['indices'], relation['signs']
    if not indices or len(indices) != len(signs) or any(s not in (-1, 1) for s in signs):
        raise ValueError('invalid signed relation')
    if any(i < 0 or i >= len(base) for i in indices):
        raise ValueError('invalid index')
    if target is None or not arithmetic.valid(target) or arithmetic.multiply(R, target) is not None:
        raise ValueError('invalid target')
    total, alpha, beta = None, 0, 0
    for index, sign in zip(indices, signs):
        row = base[index]
        point = row['point']
        if point is None or not arithmetic.valid(point) or point != arithmetic.labelled(row['a'], row['b'], target):
            raise ValueError('forged label or invalid point')
        total = arithmetic.add(total, point if sign == 1 else arithmetic.negate(point))
        alpha = (alpha+sign*row['a']) % R
        beta = (beta+sign*row['b']) % R
    recovered = -alpha*pow(beta, -1, R) % R if total is None and beta else None
    verified = recovered is not None and arithmetic.multiply(recovered, G) == target
    if total is None and beta == 0 and alpha != 0:
        raise AssertionError('zero point sum has impossible A!=0,B=0')
    return {'A': alpha, 'B': beta, 'point_sum_zero': total is None,
            'recovered': recovered, 'recovered_point_verified': verified,
            'classification': 'useful' if verified else 'zero_Q_dependency' if total is None else 'not_a_relation'}


def conditional_model_premises(coefficients, independent_uniform_labels, point_only_selection):
    """Audit declared lemma premises; this cannot discover hidden adaptivity."""
    return bool(independent_uniform_labels and point_only_selection and
                any(value % R for value in coefficients))


def refusal_controls(target, useful_case):
    from copy import deepcopy
    ar = Affine()
    checks = []

    def check(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)

    def refusal(name, function):
        try:
            function()
        except (ValueError, IndexError) as exc:
            checks.append({'name': name, 'passed': True, 'refusal': str(exc)})
        else:
            raise AssertionError(name)

    base, parts = useful_case['base'], useful_case['partitions']
    relation = {'indices': [0, 8, 16, 31], 'signs': [1, 1, 1, 1]}
    forged = deepcopy(base)
    forged[0]['a'] = (forged[0]['a']+1) % R
    refusal('forged_label_rejected', lambda: assess(ar, forged, target, relation))
    broken = deepcopy(base)
    broken[0]['point'] = (0, 0)
    refusal('off_curve_point_rejected', lambda: search(ar, [x['point'] for x in broken], parts))
    refusal('off_curve_target_rejected', lambda: assess(ar, base, (0, 0), relation))
    duplicate = [x['point'] for x in base]
    duplicate[-1] = ar.negate(duplicate[0])
    refusal('inverse_x_duplicate_rejected', lambda: search(ar, duplicate, parts))
    overlap = deepcopy(parts)
    overlap[1][0] = overlap[0][0]
    refusal('overlapping_partitions_rejected', lambda: search(ar, [x['point'] for x in base], overlap))
    wrong = {'indices': relation['indices'], 'signs': [1, 1, 1, -1]}
    check('wrong_sign_is_nonrelation', not assess(ar, base, target, wrong)['point_sum_zero'])
    repeated = assess(ar, base, target, {'indices': [0, 0], 'signs': [1, -1]})
    check('repeated_index_inverse_cancellation_zero_information',
          repeated['point_sum_zero'] and repeated['A'] == repeated['B'] == 0 and
          not repeated['recovered_point_verified'])
    check('nonzero_integer_vector_reducing_to_zero_ineligible',
          not conditional_model_premises([R, 0, 0], True, True))
    check('declared_adaptive_labels_ineligible',
          not conditional_model_premises([1, -1], False, True))
    check('label_reading_selection_ineligible',
          not conditional_model_premises([1, -1], True, False))
    check('nonzero_mod_r_model_vector_eligible',
          conditional_model_premises([1, -1], True, True))
    return {'checks': checks, 'passed': len(checks), 'counters': dict(ar.counts),
            'premise_control_scope': 'declared premise audit, not a detector of undisclosed label adaptivity'}


def execute_case(case_name, seed, mode, oracle_module, event):
    construction = Affine(event)
    event({'stage': 'case_started', 'case': case_name, 'seed': seed, 'mode': mode})
    witness = None
    if mode == 'useful':
        witness = construction.hashed_scalar(f'F3-pass2:{seed}:public-generation-witness') or 1
        target = construction.multiply(witness, G)
        target_rejections = []
    else:
        target, target_rejections = construction.hash_point(f'F3-pass2:{seed}:unknown-log-target')
    base, draws = generate_base(construction, target, seed)
    planting = plant_control(construction, base, target, witness, seed) if mode != 'natural' else []
    partitions = [list(range(i*8, (i+1)*8)) for i in range(4)]
    points = [row['point'] for row in base]
    event({'stage': 'base_completed', 'accepted_points': len(base),
           'construction_counters': dict(construction.counts)})
    solver_arithmetic = Affine()
    solved = search(solver_arithmetic, points, partitions)
    event({'stage': 'solver_completed', 'relations': solved['relations'],
           'counters': solved['counters']})
    independent = oracle_module.exhaustive(points, partitions)
    event({'stage': 'exhaustive_oracle_completed', **independent})
    if solved['relations'] != independent['relations']:
        raise AssertionError(f'{case_name}: MITM/oracle relation sets differ')
    if independent['signed_quadruples_visited'] != 8*8**4:
        raise AssertionError(f'{case_name}: exhaustive oracle count incomplete')
    labels = oracle_module.check_labels(base, target)
    event({'stage': 'independent_label_checks_completed', 'passed': labels['passed']})
    assessment_arithmetic = Affine()
    assessments = [assess(assessment_arithmetic, base, target, row) for row in solved['relations']]
    independent_assessments = oracle_module.check_assessments(base, target, solved['relations'], assessments)
    if any(not row['point_sum_zero'] for row in assessments):
        raise AssertionError(f'{case_name}: emitted nonrelation')
    planted = {'indices': [0, 8, 16, 31], 'signs': [1, 1, 1, 1]}
    if mode != 'natural' and planted not in solved['relations']:
        raise AssertionError(f'{case_name}: embedded planted relation missed')
    if mode == 'useful':
        planted_assessment = assess(assessment_arithmetic, base, target, planted)
        if not planted_assessment['recovered_point_verified'] or planted_assessment['recovered'] != witness:
            raise AssertionError('constructed useful control failed')
    elif mode == 'zero_Q':
        planted_assessment = assess(assessment_arithmetic, base, target, planted)
        if planted_assessment['A'] != 0 or planted_assessment['B'] != 0:
            raise AssertionError('constructed zero-Q control failed')
    # Natural cases intentionally impose no expected relation or useful count.
    return {'case': case_name, 'mode': mode, 'seed': seed, 'target': target,
            'base': base, 'partitions': partitions, 'base_draws': draws,
            'target_rejections': target_rejections, 'control_planting_attempts': planting,
            'generation_witness': witness,
            'witness_access': 'public witness used only in useful-control generation and expected-output check' if witness is not None else 'no target scalar generated or supplied',
            'sampling': 'deterministic SHA256 fixtures; no independent-uniform statistical law is claimed',
            'solver': solved, 'oracle': independent, 'label_verification': labels,
            'independent_assessments': independent_assessments,
            'assessments': assessments,
            'counters': {'construction': dict(construction.counts),
                         'solver': dict(solver_arithmetic.counts),
                         'assessment': dict(assessment_arithmetic.counts)}}


def host_record():
    cpu = None
    cpuinfo = Path('/proc/cpuinfo')
    if cpuinfo.exists():
        cpu = next((line.split(':', 1)[1].strip() for line in cpuinfo.read_text().splitlines()
                    if line.startswith('model name')), None)
    memory = None
    meminfo = Path('/proc/meminfo')
    if meminfo.exists():
        memory = next((int(line.split()[1])*1024 for line in meminfo.read_text().splitlines()
                       if line.startswith('MemTotal:')), None)
    return {'cpu_model': cpu, 'logical_cpus': os.cpu_count(), 'memory_bytes': memory,
            'kernel': platform.release(), 'hypervisor': None, 'isolation_tier_max': 'none',
            'hostname': platform.node(), 'python': sys.version, 'executable': sys.executable,
            'isolation_blockers': ['shared managed host', 'no exclusive placement receipt', 'no clock comparison']}


def execution_admission(seed, protocol_path, release_path):
    sys.path.insert(0, str(REPO))
    from tools import experiment_protocol as ep
    protocol = ep.read_json(protocol_path)
    errors = ep.schema_errors(protocol, 'experiment.protocol/v1') or ep.lint_protocol(protocol, HERE)
    if errors or protocol['freeze']['status'] != 'frozen':
        raise RuntimeError('valid frozen protocol required: '+str(errors))
    if seed != PANEL_SEED or protocol.get('extensions', {}).get('panel_seed') != seed:
        raise RuntimeError('seed differs from the prospective frozen panel')
    source = {name: digest(HERE/name) for name in SOURCE_FILES}
    expected = protocol.get('extensions', {}).get('source_sha256', {})
    if not expected or any(expected.get(name) != value for name, value in source.items()):
        raise RuntimeError('root must pin every instrument/analysis/export source before execution')
    interpreter_sha = digest(Path(sys.executable).resolve())
    instrument = protocol['arms'][0]['instrument']
    if instrument.get('binary_sha256') and instrument['binary_sha256'] != interpreter_sha:
        raise RuntimeError('observed Python executable differs from pinned binary')
    instrument_commit = instrument.get('commit')
    if instrument_commit:
        for name in SOURCE_FILES:
            rel = str((HERE/name).relative_to(REPO))
            observed = subprocess.check_output(['git', 'show', instrument_commit+':'+rel], cwd=REPO)
            if sha256(observed).hexdigest() != source[name]:
                raise RuntimeError('executed source differs from instrument commit: '+name)
    sys.path.insert(0, str(HERE.parents[1]/'runtime'))
    from checkpoint_gate import require_gate
    gate = require_gate(REPO, release_path, protocol, task='TASK-20261026-821d10')
    return protocol, {'source_sha256': source, 'interpreter_sha256': interpreter_sha,
                      'checkpoint_gate': gate,
                      'instrument_commit': instrument_commit,
                      'instrument_commit_byte_equivalence_checked': bool(instrument_commit),
                      'observed_git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
                      'assigned_scope_dirty_before_outputs': subprocess.check_output(
                          ['git', 'status', '--porcelain', '--', str(HERE)], cwd=REPO, text=True),
                      'global_dirty_before_outputs': bool(subprocess.check_output(
                          ['git', 'status', '--porcelain'], cwd=REPO, text=True))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--protocol', type=Path, default=HERE/'protocol.json')
    parser.add_argument('--release', type=Path, default=HERE/'release.json')
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit('Refusing to overwrite an earlier attempt')
    if not args.protocol.is_file():
        raise SystemExit('Frozen protocol.json absent; Phase B has not been released')
    protocol, source = execution_admission(args.seed, args.protocol, args.release)
    # The real checkpoint gate above precedes all experimental output and math.
    import oracle
    args.out.mkdir(parents=True, exist_ok=False)
    host = host_record()
    write_json(args.out/'host.json', host)
    started, clock = now(), time.monotonic()
    usage_start = resource.getrusage(resource.RUSAGE_SELF)
    execution = {'schema': 'f3-pass2-execution/v1', 'task': 'TASK-20261026-821d10',
                 'command': [sys.executable, *sys.argv], 'source': source, 'seed': args.seed,
                 'producer': {'runtime': os.environ.get('AUTORESEARCH_RUNTIME'),
                              'model': os.environ.get('AUTORESEARCH_RESOLVED_MODEL'),
                              'session': os.environ.get('AUTORESEARCH_SESSION_ID'), 'role': 'executor'},
                 'curve_record': json.loads((HERE/'curve-record.json').read_text()),
                 'protocol_sha256': protocol['freeze']['protocol_sha256'], 'started_at': started,
                 'status': 'started', 'case_order': [], 'case_artifacts': []}
    write_json(args.out/'execution-start.json', execution)
    cases, failure, controls = [], None, None
    def process_guard(signum, frame):
        raise TimeoutError('115-second in-process checkpoint watchdog; unfinished cases remain unknown')
    signal.signal(signal.SIGALRM, process_guard)
    signal.alarm(115)
    memory_limit = 2*1024**3
    current_limit = resource.getrlimit(resource.RLIMIT_AS)
    hard_limit = current_limit[1]
    applied_limit = memory_limit if hard_limit == resource.RLIM_INFINITY else min(memory_limit, hard_limit)
    resource.setrlimit(resource.RLIMIT_AS, (applied_limit, hard_limit))
    try:
        plan = [(f'natural-{i+1:02d}', args.seed*100+i+1, 'natural') for i in range(8)]
        plan += [('constructed-useful', args.seed*100+91, 'useful'),
                 ('constructed-zero-Q', args.seed*100+92, 'zero_Q')]
        for name, seed, mode in plan:
            execution['case_order'].append(name)
            with (args.out/(name+'-events.jsonl')).open('x') as journal:
                def event(value):
                    journal.write(json.dumps(portable(value))+'\n')
                    journal.flush()
                case = execute_case(name, seed, mode, oracle, event)
            path = args.out/(name+'.json')
            write_json(path, case)
            execution['case_artifacts'].append({'path': path.name, 'sha256': digest(path), 'bytes': path.stat().st_size})
            cases.append(case)
            print(json.dumps({'case': name, 'status': 'completed',
                              'relations': len(case['assessments']),
                              'useful': sum(x['classification'] == 'useful' for x in case['assessments'])}), flush=True)
        useful = next(c for c in cases if c['mode'] == 'useful')
        controls = refusal_controls(useful['target'], useful)
        write_json(args.out/'refusal-controls.json', controls)
    except Exception as exc:
        import traceback
        failure = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc(),
                   'not_a_mathematical_empty_set': True}
        write_json(args.out/'failure.json', failure)
    finally:
        signal.alarm(0)
    finished = now()
    usage_end = resource.getrusage(resource.RUSAGE_SELF)
    counters = Counter()
    for case in cases:
        for stage, values in case['counters'].items():
            counters.update({stage+'.'+key: value for key, value in values.items()})
        counters.update({'oracle.'+key: value for key, value in case['oracle']['counters'].items()})
        counters.update({'label_verifier.'+key: value for key, value in case['label_verification']['counters'].items()})
        counters.update({'assessment_verifier.'+key: value for key, value in case['independent_assessments']['counters'].items()})
    if controls:
        counters.update({'refusal_controls.'+key: value for key, value in controls['counters'].items()})
    natural = [case for case in cases if case['mode'] == 'natural']
    constructed = [case for case in cases if case['mode'] != 'natural']
    metrics = {'cases_completed': len(cases), 'natural_cases_completed': len(natural),
               'natural_dependencies': sum(len(c['assessments']) for c in natural),
               'natural_useful': sum(a['classification'] == 'useful' for c in natural for a in c['assessments']),
               'constructed_useful': sum(a['classification'] == 'useful' for c in constructed for a in c['assessments']),
               'constructed_zero_Q': sum(a['classification'] == 'zero_Q_dependency' for c in constructed for a in c['assessments']),
               'oracle_signed_quadruples': sum(c['oracle']['signed_quadruples_visited'] for c in cases),
               'mitm_pair_evaluations': sum(c['solver']['counters']['left_pair_evaluations']+
                                            c['solver']['counters']['right_pair_evaluations'] for c in cases),
               'refusal_and_premise_checks': controls['passed'] if controls else 0}
    status = 'timeout' if failure and failure['type'] == 'TimeoutError' else 'failed' if failure else 'succeeded'
    row = {'run_id': 'F3-pass2-mitm-'+args.out.name, 'arm': 'mitm', 'instance_id': '0',
           'seed': args.seed, 'replicate': 0, 'warmup': False,
           'status': status,
           'verification': 'error' if failure else 'verified',
           'verification_detail': 'complete separate Jacobian signed-quadruple enumeration and label checks',
           **metrics, 'native_counters': dict(counters), 'started_at': started, 'finished_at': finished,
           'wall_seconds': time.monotonic()-clock, 'wall_valid': False,
           'cpu_user_seconds': usage_end.ru_utime-usage_start.ru_utime,
           'cpu_sys_seconds': usage_end.ru_stime-usage_start.ru_stime,
           'max_rss_bytes': int(usage_end.ru_maxrss)*1024,
           'host': 'host.json', 'source': source, 'attempts': 1, 'resumed': 0,
           'isolation': {'tier': 'none', 'contended': None, 'blockers': host['isolation_blockers']},
           'case_artifacts': execution['case_artifacts']}
    oracle_row = {**row, 'run_id': 'F3-pass2-exhaustive-'+args.out.name, 'arm': 'exhaustive',
                  'mitm_pair_evaluations': 0,
                  'verification_detail': 'separate Jacobian exhaustive signed enumeration and label/recovery checks',
                  'shared_diagnostic_interval': True}
    row['oracle_signed_quadruples'] = 0
    row['shared_diagnostic_interval'] = True
    with (args.out/'rows.jsonl').open('x') as f:
        f.write(json.dumps(portable(row))+'\n')
        f.write(json.dumps(portable(oracle_row))+'\n')
    execution.update({'status': row['status'], 'finished_at': finished, 'failure': failure,
                      'metrics': metrics, 'flow': {'panels_planned': 1, 'panels_attempted': 1,
                          'panels_completed': int(not failure), 'cases_planned': 10,
                          'cases_completed': len(cases), 'cases_not_completed': 10-len(cases)},
                      'export_unit': 'one algorithm over the full fixed ten-case panel; MITM and exhaustive share inputs, setup/postprocessing and a diagnostic process interval; no clock comparison'})
    write_json(args.out/'execution.json', execution)
    print(json.dumps({'status': row['status'], 'out': str(args.out), 'metrics': metrics}), flush=True)
    return 124 if status == 'timeout' else 1 if failure else 0


if __name__ == '__main__':
    raise SystemExit(main())
