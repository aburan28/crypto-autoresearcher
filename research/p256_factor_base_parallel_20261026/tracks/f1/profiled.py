"""Stage instrumentation of the frozen extractor, with identical arithmetic.

Timings are diagnostics, not a calibrated bound. RSS is a process-lifetime
high-water mark (KiB on Linux), never a peak attributable to one phase.
The original core.py and exterior.py remain unchanged.
"""
from collections import Counter
import itertools
import resource
from time import perf_counter_ns, process_time_ns

import exterior as frozen
from core import (AffineCurve, ExtractionUnknown, chain_value, elementary,
                  multiplicity, relation_polynomial)


class Stages:
    def __init__(self, emit, **tags):
        self.emit = emit
        self.tags = tags

    def scoped(self, **tags):
        return Stages(self.emit, **(self.tags | tags))

    def call(self, phase, function, *args, **kwargs):
        wall, cpu = perf_counter_ns(), process_time_ns()
        status, error = 'complete', None
        try:
            return function(*args, **kwargs)
        except BaseException as exc:
            status, error = 'failed', type(exc).__name__
            raise
        finally:
            self.emit(dict(**self.tags, phase=phase, status=status, error_type=error,
                           wall_ns=perf_counter_ns()-wall, cpu_ns=process_time_ns()-cpu,
                           process_maxrss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                           rss_scope='process lifetime high-water; KiB on Linux',
                           clock_scope='diagnostic; no isolation or performance claim'))


def solve_stratum(parameters, depth, terminal, target, name, stages):
    from flint import fmpz_mod_ctx
    p = parameters['p']
    if depth < 1 or terminal in (2, p-2):
        raise ValueError('Separable generic Dickson fibre required')
    context = fmpz_mod_ctx(p)
    scalar = stages.call('scalar_chain', frozen.scalar_columns, depth, terminal, p)
    slots = {'distinct': (0, 1, 2), 'twoequal': (0, 0, 1), 'allequal': (0, 0, 0)}[name]
    width = max(slots)+1
    polynomial, elementary_polys = stages.call('relation_polynomial', relation_polynomial,
                                               parameters, target[0], slots)
    counters = Counter()
    operator, basis = stages.call('relation_operator', frozen.tensor_operator, polynomial,
                                 width, name == 'distinct', scalar, context, p, counters)
    kernel, certificate = stages.call('kernel_elimination', frozen.right_kernel, operator, context, p)
    projection = None
    if name == 'twoequal' and kernel.ncols():
        difference, _ = stages.call('off_diagonal_operator', frozen.tensor_operator,
                                    {(1, 0): 1, (0, 1): p-1}, 2, False, scalar, context, p, counters)
        before = kernel.ncols()
        kernel = stages.call('off_diagonal_projection', lambda: frozen.column_basis(difference*kernel, context))
        projection = dict(pre_projection_dimension=before, off_diagonal_image_dimension=kernel.ncols(),
                          method='image of commuting x-y; removes exactly diagonal eigencharacters')
    operators = [stages.call('elementary_operator', frozen.tensor_operator, poly, width,
                            name == 'distinct', scalar, context, p, counters)[0] for poly in elementary_polys]
    restricted, restriction = stages.call('operator_restriction', frozen.restrict_operators,
                                         kernel, operators, context)
    states, extraction = stages.call('character_extraction', frozen.rational_characters, restricted, context, p)
    assert len(states) == kernel.ncols()
    digest = stages.call('matrix_fingerprint', frozen.fingerprint, operator, p)
    return dict(stratum=name, states=states, basis_dimension=len(basis), scalar_dimension=len(scalar),
                matrix_sha256=digest, scalar_columns=[[[i, v] for i, v in sorted(col.items())] for col in scalar],
                root_polynomial_terms=len(polynomial),
                root_polynomial_maximum_individual_degree=max((max(e) for e in polynomial), default=0),
                kernel_certificate=certificate, off_diagonal_projection=projection,
                restriction=restriction, extraction=extraction, counters=dict(counters),
                root_domain_enumeration_used_by_solver=False, dense_Dickson_expansion_used_by_solver=False)


def signed_recovery(states, depth, terminal, target, parameters, wanted, stages):
    """Same calls/order as core.signed_recovery, with phase boundaries exposed."""
    from flint import fmpz_mod_poly_ctx
    curve, p = AffineCurve(parameters), parameters['p']
    polynomial = fmpz_mod_poly_ctx(p)
    solutions, recovered = set(), []
    for state in states:
        u, v, w = state
        factors = stages.call('cubic_factoring', lambda: polynomial([-w, v, -u, 1]).roots())
        roots = tuple(sorted(int(x) for x, count in factors for _ in range(count)))
        if len(roots) != 3 or multiplicity(roots) != wanted:
            raise ExtractionUnknown('A rational character did not recover its claimed cubic stratum')

        def check_coordinates():
            if any(chain_value(x, depth, p) != terminal for x in roots):
                raise AssertionError('Recovered coordinate does not satisfy the original chain')
            assert elementary(roots, p) == tuple(state)
        stages.call('coordinate_validation', check_coordinates)
        for x in set(roots):
            for point in stages.call('curve_lifting', curve.lifts, x):
                def check_point():
                    assert curve.valid(point)
                    assert curve.multiply(parameters['r'], point) is None
                stages.call('subgroup_verification', check_point)
        choices = [stages.call('curve_lifting', curve.lifts, x) for x in roots]

        def signs():
            for points in itertools.product(*choices):
                value = None
                for point in points:
                    value = curve.add(value, point)
                if value == target:
                    solutions.add(tuple(sorted(points)))
        stages.call('sign_enumeration', signs)
        recovered.append(dict(symmetric=list(state), roots=list(roots), multiplicity=list(wanted)))
    return sorted(solutions), recovered, dict(curve.counts)
