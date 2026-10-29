"""Verify prime-field symmetry actions before using them on relation rows.

Diagonal curve automorphisms, subgroup scalars, signed base closure and affine
translation frames are separate checks. No eigenvalue or target log is found
by a discrete-log oracle. This is an audit interface, not a faster collector.
"""
from hashlib import sha256
import json

from .curve import is_probable_prime
from .relation_quality import AffineRelations


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def subgroup(curve, generator, order, points):
    if curve.p <= 3 or not is_probable_prime(curve.p) or not is_probable_prime(order):
        raise ValueError('odd characteristic >3 and prime subgroup order required')
    if generator is None or not curve.is_on_curve(generator) or curve.mul(order, generator) is not None:
        raise ValueError('invalid nonzero subgroup generator')
    for point in points:
        if point is not None and (not curve.is_on_curve(point) or curve.mul(order, point) is not None):
            raise ValueError('point outside the stated curve/subgroup')


def diagonal_point(curve, u, point):
    """Map (x,y) -> (u²x,u³y); the coefficient identity is checked separately."""
    return None if point is None else (pow(u, 2, curve.p)*point[0] % curve.p,
                                      pow(u, 3, curve.p)*point[1] % curve.p)


def certify_diagonal(curve, generator, order, base, u, eigenvalue):
    base = list(base)
    if any(point is None for point in base):
        raise ValueError('base must contain nonzero points')
    base = [tuple(point) for point in base]
    subgroup(curve, generator, order, base)
    if type(u) is not int or type(eigenvalue) is not int or not u % curve.p or not eigenvalue % order:
        raise ValueError('nonzero integer map parameter and subgroup eigenvalue required')
    u, eigenvalue = u % curve.p, eigenvalue % order
    # Substitution in y²=x³+ax+b proves these exact coefficient obligations.
    if (curve.a*(pow(u, 4, curve.p)-1) % curve.p or
            curve.b*(pow(u, 6, curve.p)-1) % curve.p):
        raise ValueError('diagonal membership action is not an automorphism of this curve')
    keys = [min(point, curve.neg(point)) for point in base]
    if len(keys) != len(set(keys)):
        raise ValueError('base must have distinct nonzero signed point classes')
    image = diagonal_point(curve, u, generator)
    if image != curve.mul(eigenvalue, generator):
        raise ValueError('false subgroup eigenvalue on public generator')
    index = {key: i for i, key in enumerate(keys)}
    mapping, escaped, constraints = [], [], []
    for i, point in enumerate(base):
        image = diagonal_point(curve, u, point)
        if image != curve.mul(eigenvalue, point):
            raise ValueError('subgroup eigenvalue fails on a base point')
        j = index.get(min(image, curve.neg(image)))
        if j is None:
            mapping.append(None)
            escaped.append(dict(column=i, point=list(point), image=list(image)))
            continue
        sign = 1 if image == base[j] else -1
        mapping.append([j, sign])
        row = [0]*len(base)
        row[j] += 1
        row[i] -= sign*eigenvalue
        constraints.append([x % order for x in row])
    system = AffineRelations(order, len(base))
    for row in constraints:
        system.add(row, 0)
    return dict(schema='prime-field-diagonal-action/v1',
                context_sha256=digest(dict(p=curve.p, a=curve.a % curve.p, b=curve.b % curve.p,
                                           r=order, generator=generator, base=base)),
                u=u, eigenvalue=eigenvalue, map='(x,y)->(u^2*x,u^3*y)',
                coefficient_identity_checked=True, generator_action_checked=True,
                all_base_actions_checked=True, signed_mapping=mapping,
                closed_for_full_row_transport=not escaped, escaping_points=escaped,
                known_log_constraints=constraints, known_constraint_rank=system.rank,
                closure_note='Partial known orbit edges remain valid even when full closure fails.')


def group_equation(curve, generator, base, row, target=None):
    coefficients, rhs, t = list(row['coefficients']), row['rhs'], row.get('target_coefficient', 0)
    if len(coefficients) != len(base) or any(type(c) is not int for c in coefficients+[rhs, t]):
        raise ValueError('exact integer coefficients and matching base dimension required')
    if t and target is None:
        raise ValueError('nonzero target coefficient requires public target')
    lhs = None
    for c, point in zip(coefficients, base):
        lhs = curve.add(lhs, curve.mul(c, point))
    if lhs != curve.add(curve.mul(rhs, generator), curve.mul(t, target)):
        raise ValueError('relation fails original public group equation')


def audit_orbit_rows(curve, generator, order, base, u, eigenvalue, rows, *, target=None):
    """Score orbit rows only after including their publicly known log action.

If phi(P_i)=sign_i P_j and phi=[lambda], then z_j=sign_i*lambda*z_i.
Modulo these constraints a transported affine row is lambda times its seed.
Keeping the target coefficient prevents assuming phi fixes the target.
"""
    base = [tuple(point) for point in base]
    rows = list(rows)
    action = certify_diagonal(curve, generator, order, base, u, eigenvalue)
    subgroup(curve, generator, order, [target])
    p, width, coefficient = order, len(base), action['eigenvalue']
    constraints = action['known_log_constraints']
    before = AffineRelations(p, width+1)
    seeds = AffineRelations(p, width+1)
    for row in constraints:
        before.add(row+[0], 0)
    for row in rows:
        group_equation(curve, generator, base, row, target)
        augmented = list(row['coefficients'])+[-row.get('target_coefficient', 0)]
        seeds.add(augmented, row['rhs'])
        before.add(augmented, row['rhs'])
    old_rank = before.rank
    output = []
    for row in rows:
        transported = [0]*width
        for c, mapping in zip(row['coefficients'], action['signed_mapping']):
            if c % p and mapping is None:
                raise ValueError('row support escapes base; outside columns cannot be silently dropped')
            if mapping is not None:
                j, sign = mapping
                transported[j] = (transported[j]+sign*c) % p
        rhs = coefficient*row['rhs'] % p
        t = coefficient*row.get('target_coefficient', 0) % p
        transformed = dict(coefficients=transported, rhs=rhs, target_coefficient=t)
        group_equation(curve, generator, base, transformed, target)
        certificate = before.identify(transported+[-t])
        if not certificate.identifiable or certificate.value != rhs:
            raise ArithmeticError('transported row is not certified by known action and seed rows')
        output.append(dict(**transformed, original_row_weights=list(certificate.row_weights)))
    for row in output:
        before.add(row['coefficients']+[-row['target_coefficient']], row['rhs'])
    if before.rank != old_rank:
        raise ArithmeticError('orbit transport added rank after its own known action constraints')
    return dict(schema='prime-field-orbit-information-audit/v1', action=action,
                seed_rank=seeds.rank, rank_with_action_before=old_rank, rank_after=before.rank,
                additional_rank_after_known_action=before.rank-old_rank, transported_rows=output,
                certificate_row_order='known action rows followed by original seed rows',
                cost_scope='correctness audit only; no complete-cost or speedup claim')


def project_public_translation(curve, generator, order, base, shift_scalar, row, *, target=None):
    """Use F_i+[s]P as an affine frame, retaining the original unknowns z_i.

    sum c_i(F_i+[s]P)=bP+tQ becomes sum c_i F_i=(b-s*sum c_i)P+tQ.
    Translation is not certified as a subgroup endomorphism. No new log
    variables are introduced; zero/sign aliases are retained and flagged.
    """
    base = list(base)
    if any(point is None for point in base):
        raise ValueError('original base must contain nonzero points')
    base = [tuple(point) for point in base]
    subgroup(curve, generator, order, base+[target])
    if type(shift_scalar) is not int:
        raise ValueError('integer public shift scalar required')
    shift = curve.mul(shift_scalar % order, generator)
    translated = [curve.add(point, shift) for point in base]
    group_equation(curve, generator, translated, row, target)
    coefficients = list(row['coefficients'])
    rhs = (row['rhs']-shift_scalar*sum(coefficients)) % order
    projected = dict(coefficients=[c % order for c in coefficients], rhs=rhs,
                     target_coefficient=row.get('target_coefficient', 0) % order)
    group_equation(curve, generator, base, projected, target)
    seen, aliases, zeros = {}, [], []
    for i, point in enumerate(translated):
        if point is None:
            zeros.append(i)
            continue
        key = min(point, curve.neg(point))
        if key in seen:
            aliases.append([seen[key], i])
        else:
            seen[key] = i
    return dict(schema='prime-field-public-translation-frame/v1',
                shift_scalar=shift_scalar % order, shift_point=shift,
                translated_base=translated, original_columns=len(base), new_unknown_columns=0,
                zero_atoms=zeros, signed_alias_pairs=aliases, projected_row=projected,
                point_equations_checked=True,
                scope='affine log frame, not extra automorphism or measured collection improvement')
