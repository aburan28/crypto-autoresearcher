"""Target-aware zero-completed Prym collector; preprocessing stays fixed.

Rows use v*z - t*k = offset after public-anchor projection. No target scalar
is provided to collection, and no full-base-rank prerequisite is imposed.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
import sys

import prym_completion as producer
from crypto_autoresearcher.index_calculus.curve import Curve
from crypto_autoresearcher.index_calculus.relation_quality import AffineRelations
from crypto_autoresearcher.index_calculus.target_relations import TargetRelations

_NATIVE_CAPABILITY = object()
sys.path.insert(0, str(producer.ROOT/'research/prym_factor_base_width_20261025'))


def prepare(fixture, source_order, witnesses):
    """Verify all preprocessing witnesses; derive anchors only from [s]P."""
    from collect_width import public_projection, project
    from independent import verify_fixture
    verify_fixture(fixture)
    context = producer.CompletionContext(fixture)
    projection = public_projection(context, source_order)
    base = AffineRelations(fixture['r'], projection['U'])
    for row in witnesses:
        if row.get('target_coefficient', 0):
            raise ValueError('preprocessing must be independent of target rows')
        producer.verify_row(fixture, row)
        base.add(*project(row, projection, fixture['r']))
    return projection, base


def collect(fixture, source_order, witnesses, target, multipliers, event, *, capability=None):
    if capability is not _NATIVE_CAPABILITY and not (
            fixture.get('software_control') is True and fixture['p'] <= 211):
        raise ValueError('scientific target collection requires frozen-source and checkpoint admission')
    if (not multipliers or len(set(multipliers)) != len(multipliers) or
            any(type(t) is not int or not 0 < t < fixture['r'] for t in multipliers)):
        raise ValueError('nonempty distinct public multiplier schedule required')
    if (not source_order or len(set(source_order)) != len(source_order) or
            any(type(s) is not int or not 0 < s < fixture['r'] for s in source_order)):
        raise ValueError('nonempty distinct preprocessing source schedule required')
    from collect_width import project
    curve = Curve(fixture['p'], fixture['a'], fixture['b'])
    P, Q = tuple(fixture['P']), tuple(target)
    if not curve.is_on_curve(Q) or curve.mul(fixture['r'], Q) is not None:
        raise ValueError('target must be on the stated subgroup')
    projection, base = prepare(fixture, source_order, witnesses)
    system = TargetRelations(base)
    # Also validates the generator even if no useful target row is found.
    system.verify(curve, P, Q)
    context = producer.CompletionContext(fixture)
    counts, digest, seen, rows = Counter(), sha256(), set(), []
    attempts, first_single, first_combined = 0, None, None
    legend={k:producer.STATUS_LEGEND[k] for k in ('S','D','P','R','X','B','A','+')}
    codes={v:k for k,v in legend.items()};blocks=[]
    for multiplier in multipliers:
        statuses=[];source_digest=sha256()
        for triple in combinations(range(len(context.base)), 3):
            for options in product(range(4), repeat=3):
                attempts += 1
                descriptor, reason = context.descriptor(multiplier, triple, options, source=Q)
                identity = None
                if descriptor is not None:
                    identity = producer.uid(context.canonical_identity(descriptor))
                    if identity in seen:
                        reason = 'canonical_alias'
                    else:
                        seen.add(identity)
                        row, reason = context.construct(descriptor)
                        if row is not None:
                            row.update(source_scalar=0, target_coefficient=multiplier)
                            producer.verify_row(fixture, row, target=Q)
                            # Preserve a valid geometric witness even if the
                            # subsequent projection/certificate path fails.
                            event(dict(kind='verified_witness', attempt=attempts, row=row))
                            coefficients, offset = project(row, projection, fixture['r'])
                            diagnostic = system.add(coefficients, offset, multiplier)
                            if diagnostic['single_row_scalar'] is not None:
                                if curve.mul(diagnostic['single_row_scalar'], P) != Q:
                                    raise ValueError('single-row target recovery failed public verification')
                                if first_single is None:
                                    first_single = dict(attempt=attempts, scalar=diagnostic['single_row_scalar'])
                            certificate = system.verify(curve, P, Q)
                            if certificate is not None and first_combined is None:
                                first_combined = dict(attempt=attempts, certificate=certificate)
                            rows.append(row)
                            event(dict(kind='accepted', attempt=attempts, diagnostic=diagnostic,
                                       target_identifiable=certificate is not None))
                status = reason or 'accepted'
                counts[status] += 1
                statuses.append(codes[status])
                encoded=json.dumps([multiplier, list(triple), list(options), identity, status],
                                   separators=(',', ':')).encode()+b'\n'
                digest.update(encoded);source_digest.update(encoded)
        block=dict(multiplier=multiplier,attempts=attempts,statuses=''.join(statuses),branch_sha256=source_digest.hexdigest())
        blocks.append(block)
        event(dict(kind='multiplier_complete', multiplier=multiplier, attempts=attempts,
                   accepted=len(rows), augmented_rank=system.augmented.rank, counts=dict(counts),
                   statuses=block['statuses'],branch_sha256=block['branch_sha256']))
    base_points = [tuple(atom['point']) for atom in fixture['factor_base']]
    public_points = [tuple(anchor['point']) for anchor in projection['public_derivations']]
    return dict(schema='prym-natural-target-completion/v1', curve_uid=fixture['uid'],
                target=list(Q), source_order=list(source_order), multipliers=list(multipliers),
                target_is_signed_base_point=Q in base_points or curve.neg(Q) in base_points,
                target_is_public_anchor=Q in public_points or curve.neg(Q) in public_points,
                preprocessing=base.summary(), projection=projection, complete=True,
                stopping_rule='full census regardless of recovery', attempts=attempts,
                statuses=dict(counts), branch_sha256=digest.hexdigest(), rows=rows,
                status_legend=legend,status_blocks=blocks,
                first_single_recovery=first_single, first_combined_recovery=first_combined,
                final_target_certificate=system.verify(curve, P, Q),
                target_identification=system.identify(), operation_vector=dict(context.f.counts),
                target_validation_group_ops=curve.ops.group_ops,
                cost_scope='producer field/group counters and separate Curve validation group calls only; excludes inline independent row verification/replay/linear algebra/hash costs and complete S',
                scientific_promotion=False)
