"""Additive x=0 source/interpolation completion of the retained Prym collector.

Historical Context/collector/checker files remain byte-for-byte unchanged.
No target-secret labels or base construction changes are introduced.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT/'research/prym_experiment_design_20261019/implementation'
sys.path.insert(0, str(OLD))
from relations import Context, uid
from independent import verify_row

from crypto_autoresearcher.index_calculus.relation_quality import AffineRelations

_NATIVE_CAPABILITY = object()


class CompletionContext(Context):
    def lift_source(self, scalar, source=None):
        source = self.P if source is None else source
        key = (scalar, source)
        if key in self.source_cache:
            self.f.counts['source_cache_hits'] += 1
            return self.source_cache[key]
        self.f.counts['source_cache_misses'] += 1
        point = self.e.neg(self.e.mul(scalar, source))
        root = None if point is None else self.f.sqrt(point[0])
        # Zero is a legitimate affine cover coordinate; infinity remains absent.
        result = None if root is None else (root, point[1])
        self.source_cache[key] = result
        return result

    def descriptor(self, scalar, triple, options, source=None):
        if len(triple) != 3 or len(set(triple)) != 3 or len(options) != 3:
            raise ValueError('three distinct atom labels and three options required')
        first = self.lift_source(scalar, source)
        if first is None:
            return None, 'source_no_nonzero_rational_lift'
        points, labels = [first], []
        for j, option in zip(triple, options):
            if not 0 <= j < len(self.lifts) or option not in range(4):
                raise ValueError('invalid atom or sign/deck option')
            x, y = self.lifts[j]
            sign = -1 if option & 1 else 1
            points.append(((-x if option & 2 else x) % self.p, sign*y % self.p))
            labels.append((j, sign, option))
        if len({x for x, _ in points}) != 4:
            return None, 'duplicate_interpolation_x'
        return dict(source_scalar=scalar, points=points, labels=labels), None


def collect(fixture, sources, event, *, include_zero=True, capability=None):
    """Complete source/triple/option stream. No sampling or rank-based stop.

    Direct calls are restricted to explicitly marked small software fixtures.
    The CLI obtains scientific admission before selecting the context.
    """
    if capability is not _NATIVE_CAPABILITY and not (fixture.get('software_control') is True and fixture['p'] <= 211):
        raise ValueError('scientific collection requires frozen-source and checkpoint admission')
    if len(set(sources)) != len(sources) or any(type(s) is not int or not 0 < s < fixture['r'] for s in sources):
        raise ValueError('invalid public source schedule')
    sys.path.insert(0, str(ROOT/'research/prym_factor_base_width_20261025'))
    from collect_width import public_projection, project
    context = (CompletionContext if include_zero else Context)(fixture)
    projection = public_projection(context, sources)
    relations = AffineRelations(fixture['r'], projection['U'])
    seen, rows, counts, digest = set(), [], Counter(), sha256()
    attempts = 0
    for scalar in sources:
        for triple in combinations(range(len(context.base)), 3):
            for options in product(range(4), repeat=3):
                attempts += 1
                descriptor, reason = context.descriptor(scalar, triple, options)
                identity = None
                if descriptor is not None:
                    identity = uid(context.canonical_identity(descriptor))
                    if identity in seen:
                        reason = 'canonical_alias'
                    else:
                        seen.add(identity)
                        row, reason = context.construct(descriptor)
                        if row is not None:
                            verify_row(fixture, row)
                            coefficients, rhs = project(row, projection, fixture['r'])
                            independent = relations.add(coefficients, rhs)
                            rows.append(row)
                            event(dict(kind='accepted', attempt=attempts, row=row,
                                       independent=independent, rank=relations.rank,
                                       touches_zero=any(x == 0 for x, y in descriptor['points'])))
                status = reason or 'accepted'
                counts[status] += 1
                record = [scalar, list(triple), list(options), identity, status]
                digest.update(json.dumps(record, separators=(',', ':')).encode()+b'\n')
        event(dict(kind='source_complete', scalar=scalar, attempts=attempts,
                   accepted=len(rows), rank=relations.rank, counts=dict(counts)))
    return dict(schema='prym-zero-completion/v1', curve_uid=fixture['uid'],
                include_zero=include_zero, source_order=list(sources), complete=True,
                attempts=attempts, statuses=dict(counts), branch_sha256=digest.hexdigest(),
                rows=rows, projection=projection, quality=relations.summary(),
                kernel=relations.kernel(), operation_vector=dict(context.f.counts),
                cost_scope='field/group counters only; no complete S or timing claim',
                scientific_promotion=False)
