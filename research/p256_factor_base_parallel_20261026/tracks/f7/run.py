"""F7 balanced arithmetic and elliptic norm panel; imports execute no data."""
import hashlib
from panel_io import run_main

TASK = 'TASK-20261026-59f4c9'


def panel(log, seed):
    import field as f
    import balanced as b
    C = b.Context()
    log.set_arm('candidate')
    log.check(f.P % 4 == 3 and f.B % f.P not in (0, 2, f.P-2), 'exact split-model smoothness hypotheses')
    zero, infinity_difference = C.identity(), C.infinity_difference()
    fixtures = []
    rational_points, rational_draws = [], []
    for attempt in range(4096):
        z = int.from_bytes(hashlib.sha256(f'F7-pass2/{seed}/rational/{attempt}'.encode()).digest(), 'big') % f.P
        value = f.evaluate(C.F, z)
        w = b.sqrt_fp(value)
        accepted = w is not None and w != 0 and z not in (0, 1, f.P-1) and z not in [point[0] for point in rational_points]
        rational_draws.append({'attempt': attempt, 'z': z, 'accepted': accepted,
                               'nonlift': w is None, 'excluded_exceptional_z': z in (0, 1, f.P-1)})
        if accepted:
            rational_points.append((z, w))
            if len(rational_points) == 16:
                break
    if len(rational_points) != 16:
        raise RuntimeError('Bounded rational-point generation incomplete; no panel completeness claim')
    for start in range(0, len(rational_draws), 64):
        log.case(f'rational-draws-{start//64:03d}', rational_draws[start:start+64])
    point_classes = []
    for index, point in enumerate(rational_points):
        D = C.point(point, n=index % 2)
        point_classes.append(D)
        fixtures.append((f'rational-{index:02d}', D))
        log.check(D.add(D.negate()).is_identity(), f'rational inverse {index}')
        log.case(f'rational-{index:02d}', {'point': point, 'class': D.record(), 'norm_closed': D.norm()})
    nonsplit, nonsplit_witnesses, quadratic_draws = [], [], []
    for attempt in range(512):
        aa = int.from_bytes(hashlib.sha256(f'F7-pass2/{seed}/quadratic/{attempt}/a'.encode()).digest(), 'big') % f.P
        bb = int.from_bytes(hashlib.sha256(f'F7-pass2/{seed}/quadratic/{attempt}/b'.encode()).digest(), 'big') % f.P
        z = (aa, bb)
        value = b.qe(C.F, z)
        w = b.sqrt_fp2(value) if aa and bb else None
        u = [(aa*aa+bb*bb) % f.P, -2*aa % f.P, 1]
        fresh = tuple(u) not in [D.u for D in nonsplit]
        accepted = w is not None and w != (0, 0) and fresh and aa != 0 and bb != 0
        quadratic_draws.append({'attempt': attempt, 'a': aa, 'b': bb, 'accepted': accepted,
                                'extension_nonlift': w is None, 'fresh_u': fresh})
        if accepted:
            slope = w[1]*pow(bb, -1, f.P) % f.P
            v = [(w[0]-slope*aa) % f.P, slope]
            D = C.make(u, v, 0)
            index = len(nonsplit)
            witness = [(z, w), ((aa, -bb % f.P), (w[0], -w[1] % f.P))]
            log.check(b.support(D)[0][0][1] != 0, f'quadratic support nonsplit {index}')
            nonsplit.append(D)
            nonsplit_witnesses.append(witness)
            fixtures.append((f'quadratic-{index:02d}', D))
            log.case(f'quadratic-{index:02d}', {'class': D.record(), 'Fp2_support_witness': witness,
                                              'norm_closed': D.norm(), 'a_and_b_nonzero': True})
            if len(nonsplit) == 8:
                break
    if len(nonsplit) != 8:
        raise RuntimeError('Bounded degree-two support generation incomplete')
    for start in range(0, len(quadratic_draws), 32):
        log.case(f'quadratic-draws-{start//32:03d}', quadratic_draws[start:start+32])

    operations = []
    for index in range(16):
        left = point_classes[index]
        if index % 4 == 0:
            right, sign = point_classes[(index+1) % 16], 1
        elif index % 4 == 1:
            right, sign = point_classes[(index+5) % 16], -1
        elif index % 4 == 2:
            right, sign = left, 1
        else:
            right, sign = left, -1
        trace = []
        result = left.add(right, trace) if sign == 1 else left.subtract(right, trace)
        expected_norm = C.E.add(left.norm(), right.norm() if sign == 1 else C.E.neg(right.norm()))
        log.check(result.norm() == expected_norm, f'closed norm additivity rational operation {index}')
        if index % 4 == 3:
            log.check(result.is_identity(), f'explicit cancellation {index}')
        fixtures.append((f'operation-{index:02d}', result))
        operations.append((left, right, sign, result))
        log.case(f'operation-{index:02d}', {'left': left.record(), 'right': right.record(), 'right_sign': sign,
                                          'result': result.record(), 'trace': trace, 'norm_expected': expected_norm})
    for index in range(8):
        left, right = nonsplit[index], nonsplit[(index+1) % 8]
        trace = []
        result = left.add(right, trace)
        log.check(result.norm() == C.E.add(left.norm(), right.norm()), f'closed norm additivity nonsplit operation {index}')
        A, B0, D = point_classes[index], point_classes[(index+1) % 16], nonsplit[index]
        log.check(A.add(B0).add(D) == A.add(B0.add(D)), f'balanced associativity {index}')
        fixtures.append((f'nonsplit-operation-{index:02d}', result))
        operations.append((left, right, 1, result))
        log.case(f'nonsplit-operation-{index:02d}', {'left': left.record(), 'right': right.record(),
                                                   'result': result.record(), 'trace': trace})

    scalars = [1, 2, 3, 17, 257, 65537, f.R-1]
    source_points = [C.E.mul(scalar, f.G) for scalar in scalars]
    pullbacks = [C.pullback(point) for point in source_points]
    for index, (point, divisor) in enumerate(zip(source_points, pullbacks)):
        log.check(divisor.norm() == C.E.add(point, point), f'norm after pullback equals two {index}')
        next_index = (index+1) % len(pullbacks)
        source_sum = C.E.add(point, source_points[next_index])
        trace = []
        got = divisor.add(pullbacks[next_index], trace)
        log.check(got == C.pullback(source_sum), f'pullback homomorphism in balanced classes {index}')
        fixtures.append((f'pullback-{index:02d}', divisor))
        log.case(f'pullback-{index:02d}', {'source_scalar': scalars[index], 'source_point': point,
                                         'class': divisor.record(), 'next_sum': got.record(), 'trace': trace})

    # Infinity bookkeeping is checked independently of the noninjective norm.
    log.check(not infinity_difference.is_identity(), 'infinity difference is not the identity')
    log.check(infinity_difference.norm() is None, 'infinity difference has zero norm')
    log.check(infinity_difference.add(infinity_difference.negate()).is_identity(), 'opposite infinity differences cancel')
    log.check((infinity_difference.u, infinity_difference.v) == (zero.u, zero.v) and infinity_difference != zero,
              'dropping infinity balance would identify two different classes')
    coefficient = f.B*pow(3, -1, f.P) % f.P
    principal_affine = C.make([-coefficient, 0, 1], [0, coefficient], 0)
    trace = []
    principal_class = principal_affine.add(infinity_difference.mul(2), trace)
    log.check(principal_class.is_identity(), 'principal divisor w-z^3 includes correct infinity terms')
    fixtures.extend([('infinity-difference', infinity_difference), ('principal-affine', principal_affine)])
    log.case('principal-w-minus-z3', {'finite_class': principal_affine.record(), 'infinity_difference': infinity_difference.record(),
                                    'finite_zeros': 'z^2=b/3, w=z^3',
                                    'principal_divisor': 'finite_zeros + infinity_plus - 3 infinity_minus',
                                    'finite_class_plus_two_infinity_difference': principal_class.record(), 'trace': trace})
    for index, point in enumerate(rational_points[:8]):
        left = C.point(point, n=0)
        conjugate = C.point((point[0], -point[1] % f.P), n=1)
        log.check(left.add(conjugate).is_identity(), f'principal divisor z-zP {index}')
    bad_balance = False
    try:
        C.make([1], [], 3)
    except ValueError:
        bad_balance = True
    log.check(bad_balance, 'invalid infinity normalization refused')
    corrupt_multiplicity = False
    z0, w0 = rational_points[0]
    try:
        C.make(f.mul([-z0, 1], [-z0, 1]), [w0], 0)
    except ValueError:
        corrupt_multiplicity = True
    log.check(corrupt_multiplicity, 'corrupt repeated-point v without tangent correction refused')
    candidate_counters = dict(C.counters)
    log.case('native-candidate-counters', {'balanced': dict(C.counters), 'elliptic': dict(C.E.counters),
                                         'timing_scope': 'shared process diagnostics only; no method clock claim'})
    log.mark_arm('candidate', {'checked_objects': len(fixtures)+len(operations),
                              'rational_points': len(rational_points), 'degree_two_supports': len(nonsplit),
                              'divisor_operations': len(operations), 'pullback_regressions': len(pullbacks)})

    # Reference actually reconstructs every recorded class support in Fp2.
    log.set_arm('reference')
    independent = {}
    for name, divisor in fixtures:
        support = b.support(divisor)
        norm = b.independent_norm_points(support)
        log.check(norm == divisor.norm(), 'independent support norm '+name)
        independent[name] = norm
        log.case('reference-'+name, {'class': divisor.record(), 'support_with_multiplicity': support,
                                     'independent_elliptic_sum': norm, 'closed_norm': divisor.norm(),
                                     'note': 'Both infinities map to O; equal norms alone do not certify class equality.'})
    for index, (left, right, sign, result) in enumerate(operations):
        L = b.independent_norm_points(b.support(left))
        R0 = b.independent_norm_points(b.support(right))
        expected = f.independent_add(L, R0 if sign == 1 else C.E.neg(R0), -3)
        actual = b.independent_norm_points(b.support(result))
        log.check(actual == expected, f'independent norm homomorphism operation {index}')
    missing_conjugate = False
    try:
        b.independent_norm_points(nonsplit_witnesses[0][:1])
    except ValueError:
        missing_conjugate = True
    log.check(missing_conjugate, 'omitted Frobenius conjugate refused by rational norm interface')
    log.case('reference-control', {'omitted_conjugate_refused': missing_conjugate,
                                  'independent_code_scope': 'Fp2 support reconstruction and elliptic point sums; no Sage10.6 pair arithmetic',
                                  'not_established': 'Independent norm equality does not independently prove all Jacobian class relations.'})
    log.mark_arm('reference', {'checked_objects': len(fixtures)+len(operations)+1, 'support_norms': len(fixtures),
                              'norm_homomorphism_cases': len(operations)})
    return {'_completion_sentinel': TASK, 'rational_points': len(rational_points), 'degree_two_supports': len(nonsplit),
            'divisor_operations': len(operations), 'pullback_regressions': len(pullbacks),
            'infinity_balance_representation': '(u,v,n); identity (1,0,1), infinity difference (1,0,2)',
            'native_candidate_counters': candidate_counters, 'native_all_phase_counters': dict(C.counters),
            'scope_limits': ['No plane-quartic Jacobian arithmetic or target-image relation solver is supplied.',
                             'Primary balanced algorithms plus exact finite checks are not a formal proof certificate.',
                             'Norm checks cannot prove class equality; principal/infinity/class-group controls remain distinct.',
                             'No comparative clock, asymptotic solver cost, or ECDLP advantage is inferred.']}


if __name__ == '__main__':
    raise SystemExit(run_main(panel, TASK, ['checked_objects', 'rational_points', 'degree_two_supports',
                                          'divisor_operations', 'pullback_regressions', 'support_norms',
                                          'norm_homomorphism_cases']))
