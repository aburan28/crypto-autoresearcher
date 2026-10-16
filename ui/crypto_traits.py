"""Reader for the pinned crypto `curve-traits/1` snapshot (`crypto-curve-traits/1`).

Joins on exact `curve_uid` only. Values are copied, never computed. A DiSSECT
slot is filled only where its pinned definition is the same quantity; every
other value stays in the supplementary `crypto.*` rows with crypto's status.
"""
import json
import re

from .comparisons import _read

ADAPTER = 'crypto-curve-traits/1'
EXACT = ('proved', 'probable')
STATUSES = EXACT + ('bounded', 'unknown', 'not_evaluated', 'not_applicable')
UID = re.compile(r'urn:ec-record:1:sha256:[a-f0-9]{64}\Z')
SECTION = 'crypto curve_traits'
DESCRIPTION = ('Computed by aburan28/crypto `curve_traits` from its registry model and recorded order. '
               'Status: proved = exact (deterministic primality); probable = exact if every probable prime is '
               'prime; bounded = only a bound (a conductor is then a lower bound); unknown = attempted, not '
               'determined within the factoring budget; not_evaluated = skipped by a declared limit; '
               'not_applicable = does not apply. Values are invariants or bounds, not routes or advantages.')

# (key, label, path into the record, path to its status). A status path of
# None means traits.json records no per-value status for that field.
ROWS = [
    ('order', 'Curve order #E', ('order',), ('order_check', 'status')),
    ('order_check.method', 'Order check method', ('order_check', 'method'), ('order_check', 'status')),
    ('trace', 'Trace t', ('trace',), ('order_check', 'status')),
    ('trace_ratio', 'Trace ratio t / 2√q', ('trace_ratio',), ('order_check', 'status')),
    ('ordinary', 'Ordinary', ('ordinary',), ('order_check', 'status')),
    ('frobenius.disc', 'Frobenius discriminant Δ = t² − 4q', ('frobenius', 'disc'), ('frobenius', 'disc_status')),
    ('frobenius.disc_primes', 'Δ prime factorization [p, e]', ('frobenius', 'disc_primes'), ('frobenius', 'disc_status')),
    ('frobenius.disc_unfactored', 'Δ unfactored composites', ('frobenius', 'disc_unfactored'), ('frobenius', 'disc_status')),
    ('frobenius.cm_disc', 'CM discriminant d_K of Q(π)', ('frobenius', 'cm_disc'), ('frobenius', 'status')),
    ('frobenius.conductor', 'Frobenius conductor v = [O_K : Z[π]]', ('frobenius', 'conductor'), ('frobenius', 'status')),
    ('frobenius.conductor_primes', 'Frobenius conductor primes [p, e]', ('frobenius', 'conductor_primes'), ('frobenius', 'status')),
    ('frobenius.conductor_bits', 'Frobenius conductor bits', ('frobenius', 'conductor_bits'), ('frobenius', 'status')),
    ('frobenius.conductor_fraction', 'Conductor fraction log v / log √|Δ|', ('frobenius', 'conductor_fraction'), ('frobenius', 'status')),
    ('frobenius.class_number', 'Exact class number h(d_K)', ('frobenius', 'class_number'), ('frobenius', 'class_number_status')),
    ('endomorphism.conductor_divides', 'End(E) conductor divides f₀', ('endomorphism', 'conductor_divides'), ('endomorphism', 'status')),
    ('endomorphism.maximal', 'End(E) = O_K established', ('endomorphism', 'maximal'), ('endomorphism', 'status')),
    ('endomorphism.contains', 'Orders known to lie in End(E)', ('endomorphism', 'contains'), ('endomorphism', 'status')),
    ('small_primes', 'Small primes ℓ ≤ 31: volcano depth v_ℓ(v), splitting, rational ℓ-isogenies', ('small_primes',), None),
    ('subfield.j_field_degree', 'Least k with j ∈ GF(2^k)', ('subfield', 'j_field_degree'), ('subfield', 'status')),
    ('subfield.definition_degree', 'Least field of definition GF(2^k)', ('subfield', 'definition_degree'), ('subfield', 'status')),
    ('subfield.base_trace', 'Trace t_k over the field of definition', ('subfield', 'base_trace'), ('subfield', 'status')),
    ('subfield.base_trace_sign_free', 'Only |t_k| is invariant', ('subfield', 'base_trace_sign_free'), ('subfield', 'status')),
    ('subgroup.order', 'Prime subgroup order r', ('subgroup', 'order'), ('subgroup', 'status')),
    ('subgroup.bits', 'Prime subgroup bits', ('subgroup', 'bits'), ('subgroup', 'status')),
    ('subgroup.cofactor', 'Cofactor #E / r', ('subgroup', 'cofactor'), ('subgroup', 'status')),
    ('subgroup.source', 'Subgroup source', ('subgroup', 'source'), ('subgroup', 'status')),
    ('embedding.degree', 'Embedding degree ord_r(q)', ('embedding', 'degree'), ('embedding', 'status')),
    ('embedding.lower_bound', 'Embedding degree lower bound', ('embedding', 'lower_bound'), ('embedding', 'status')),
    ('embedding.complement_bits', 'Bit length of (r − 1) / k', ('embedding', 'complement_bits'), ('embedding', 'status')),
    ('twist.order', 'Quadratic twist order q + 1 + t', ('twist', 'order'), ('twist', 'status')),
    ('twist.largest_prime_bits', 'Twist largest prime bits', ('twist', 'largest_prime_bits'), ('twist', 'status')),
    ('twist.cofactor', 'Twist cofactor', ('twist', 'cofactor'), ('twist', 'status')),
    ('keys', 'Grouping keys', ('keys',), None),
]


def _get(record, path):
    for part in path:
        if not isinstance(record, dict):
            return None
        record = record.get(part)
    return record


def _int(value):
    if type(value) is int:
        return value
    if isinstance(value, str) and re.fullmatch(r'-?[0-9]+', value):
        return int(value)
    raise ValueError('Expected an exact integer.')


def load(repo, spec, source_pin):
    """Validate the snapshot and return {curve_uid: (record, representation, pins)}."""
    if spec.get('adapter') != ADAPTER:
        raise ValueError('Unsupported supplementary trait adapter')
    raw, _ = _read(repo, spec)
    snap = json.loads(raw)
    if (snap.get('schema') != 'crypto-curve-traits-snapshot/1' or snap.get('adapter') != ADAPTER
            or snap.get('traits_schema') != 'curve-traits/1'):
        raise ValueError('Unsupported traits snapshot')
    pins = {k: source_pin(snap['sources'][k]) for k in ('traits', 'registry', 'definitions')}
    if len({(p['repository'], p['commit']) for p in pins.values()}) != 1:
        raise ValueError('Traits sources come from different commits')
    if snap.get('registry_sha256') != pins['registry']['sha256']:
        raise ValueError('Traits were not built from the pinned registry')
    joined = {}
    for record in snap['records']:
        traits = record['traits']
        if not isinstance(traits, dict) or traits.get('slug') != record['slug']:
            raise ValueError('Traits record does not match its slug')
        for rep in record['representations']:
            if not UID.fullmatch(str(rep.get('curve_uid'))) or rep['curve_uid'] in joined:
                raise ValueError('Invalid or ambiguous curve_uid join')
            joined[rep['curve_uid']] = (record, rep, pins)
    return joined


def _row(label, value, status, pins, extra=None):
    if status not in STATUSES and status is not None:
        raise ValueError('Unsupported traits status')
    return {'label': label, 'value': value, 'status': 'source_reported' if value is not None else 'unknown',
            'evidence_status': status, 'source': pins['traits'] if value is not None else None, **(extra or {})}


def apply(row, joined, identity):
    """Fill one catalog row from its exact-uid traits record, or mark it not joined."""
    match = joined.get(row['curve_uid'])
    definition = {'description': DESCRIPTION, 'section': SECTION}
    if match is None:
        for key, label, _, _ in ROWS:
            row['traits'][f'crypto.{key}'] = {'label': f'{SECTION} · {label}', 'value': None, 'status': 'unknown',
                                              'evidence_status': None, 'source': None, **definition}
        return
    record, rep, pins = match
    if rep['ec1'] != row['curve_id'] or rep['field_sha256'] != identity['field_sha256']:
        raise ValueError('Traits representation conflicts with the capsule identity')
    t = record['traits']
    definition['definition'] = pins['definitions']
    definition['definition_label'] = 'crypto TRAITS.md ↗'
    for key, label, path, status_path in ROWS:
        status = _get(t, status_path) if status_path else None
        extra = dict(definition)
        if status_path is None:
            extra['note'] = 'traits.json records no per-value status here; see TRAITS.md'
        row['traits'][f'crypto.{key}'] = _row(f'{SECTION} · {label}', _get(t, path), status, pins, extra)
    row['crypto_traits'] = {'slug': record['slug'], 'icv1': record['icv1'], 'source': pins['traits']}

    # Same-quantity fills. Each must agree with anything the capsule reports.
    def fill(key, value, status, mapping):
        if value is None or status not in EXACT:
            return
        trait = row['traits'][key]
        if trait['value'] is not None and str(trait['value']) != str(value):
            raise ValueError('Conflicting sourced trait')
        if trait['value'] is None:
            trait.update(value=value, status='source_reported', evidence_status=status,
                         source=pins['traits'], mapping=mapping)

    curve = row['curve']
    for field, value in (('subgroup_order', _get(t, ('subgroup', 'order'))), ('cofactor', _get(t, ('subgroup', 'cofactor')))):
        if curve.get(field) is not None and value is not None and str(curve[field]) != str(value):
            raise ValueError('Conflicting sourced trait')
    order_status, frob, endo = _get(t, ('order_check', 'status')), t.get('frobenius', {}), t.get('endomorphism', {})
    fill('order', _int(t['order']), order_status, 'crypto order (order_check)')
    fill('trace', _int(t['trace']), order_status, 'crypto trace (order_check)')
    if frob.get('cm_disc') is not None:
        fill('cm_discriminant', _int(frob['cm_disc']), frob.get('status'), 'crypto frobenius.cm_disc')
        fill('dissect.discriminant.cm_disc', _int(frob['cm_disc']), frob.get('status'), 'crypto frobenius.cm_disc (d_K)')
    if frob.get('conductor') is not None:
        # DiSSECT's max_conductor is sqrt((t²−4q)/d_K) = [O_K : Z[π]]; a bounded value is not it.
        fill('dissect.discriminant.max_conductor', _int(frob['conductor']), frob.get('status'),
             'crypto frobenius.conductor (v with t²−4q = v²·d_K)')
    if frob.get('disc_primes') is not None and frob.get('disc_unfactored') == []:
        primes = sorted((_int(p), _int(e)) for p, e in frob['disc_primes'])
        fill('dissect.discriminant.factorization', [p for p, e in primes for _ in range(e)], frob.get('disc_status'),
             'crypto frobenius.disc_primes, unpacked as DiSSECT does (primes with multiplicity, sign dropped)')
    if endo.get('maximal') is True and endo.get('conductor_divides') == '1':
        fill('endomorphism_order_conductor', 1, endo.get('status'), 'crypto endomorphism.conductor_divides = 1 (maximal)')
    subgroup = t.get('subgroup', {})
    if subgroup.get('source') == 'registry representation':
        # DiSSECT's cofactor family reports the declared generator order and its cofactor.
        fill('dissect.cofactor.order', _int(subgroup['order']), subgroup.get('status'), 'crypto subgroup.order')
        fill('dissect.cofactor.cofactor', _int(subgroup['cofactor']), subgroup.get('status'), 'crypto subgroup.cofactor')
        emb = t.get('embedding', {})
        if emb.get('degree') is not None:
            # DiSSECT: bit length of φ(n)/e with n the generator order, e = ord_n(q); φ(r) = r − 1.
            fill('dissect.embedding.complement_bit_length', emb.get('complement_bits'),
                 emb.get('status') if subgroup.get('status') in EXACT else None,
                 'crypto embedding.complement_bits (bit length of (r−1)/ord_r(q))')
