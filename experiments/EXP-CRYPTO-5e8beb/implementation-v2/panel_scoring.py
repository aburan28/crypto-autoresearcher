"""Pure exact scoring of supplied metadata; no scientific certificate validation."""
from fractions import Fraction
from math import gcd

SIZES = (11, 17)
QS = (2, 3, 4, 5)
KERNELS = ('R1', 'R2', 'R3', 'R4')
SEEDS = tuple(range(32))
PANEL_IDS = tuple((n, q, k) for n in SIZES for q in QS for k in KERNELS)
CONTROL_NAMES = ('exact_identity_constant', 'C15_cosets', 'hidden_uniform',
                 'public_prime_rigidity', 'matched_sizes',
                 'full_joint_and_freshness', 'independent_exact_tables')
POSITIVE = 'finite_panel_advantage_with_valid_controls'
NEGATIVE = 'complete_valid_panel_no_paired_advantage'
INVALID = 'incomplete_or_invalid_evidence'


class SchemaError(ValueError):
    """Malformed metadata, never a negative scientific observation."""


def _keys(value, keys, where):
    if type(value) is not dict or set(value) != set(keys):
        raise SchemaError(f'{where}: expected exactly {list(keys)}')


def _delta(value, where):
    _keys(value, ('numerator', 'denominator'), where)
    a, b = value['numerator'], value['denominator']
    if type(a) is not int or type(b) is not int:
        raise SchemaError(f'{where}: fraction components must be integers, not bools/floats')
    if b <= 0 or not 0 <= a <= b or gcd(a, b) != 1:
        raise SchemaError(f'{where}: require reduced fraction in [0,1] with positive denominator')
    return Fraction(a, b)


def rational(value):
    """Serialize an already computed Fraction, including negative gaps."""
    return {'numerator': value.numerator, 'denominator': value.denominator}


def score_panel_advantage(metadata):
    """Validate score identities/types, then score all fixed panels and pairs.

    Structural errors raise SchemaError. Missing, false, or unknown gates
    produce INVALID with complete score tables; gate truth is caller supplied
    and is not authenticated here. Input is never modified.
    """
    if type(metadata) is not dict or 'panels' not in metadata:
        raise SchemaError('metadata: panels required')
    if set(metadata) - {'panels', 'validity', 'controls'}:
        raise SchemaError('metadata: unknown fields')
    rows = metadata['panels']
    if type(rows) is not list or len(rows) != 32:
        raise SchemaError('panels: require exactly 32 rows')
    indexed = {}
    for row in rows:
        _keys(row, ('N', 'q', 'kernel', 'coordinate_delta', 'nulls'), 'panel')
        n, q, k = row['N'], row['q'], row['kernel']
        if type(n) is not int or type(q) is not int or type(k) is not str:
            raise SchemaError('panel: N/q require integers and kernel requires string')
        key = (n, q, k)
        if key not in PANEL_IDS or key in indexed:
            raise SchemaError(f'panel: unknown or duplicate identity {key}')
        coordinate = _delta(row['coordinate_delta'], f'{key}.coordinate_delta')
        nulls = row['nulls']
        if type(nulls) is not list or len(nulls) != 32:
            raise SchemaError(f'{key}.nulls: require exactly 32 labeled rows')
        by_seed = {}
        for entry in nulls:
            _keys(entry, ('seed', 'delta'), f'{key}.null')
            seed = entry['seed']
            if type(seed) is not int or seed not in SEEDS or seed in by_seed:
                raise SchemaError(f'{key}.null: unknown or duplicate seed')
            by_seed[seed] = _delta(entry['delta'], f'{key}.seed{seed}')
        indexed[key] = (coordinate, by_seed)
    # Cardinality plus unique membership proves full identity coverage.
    panels = []
    qualifies = {}
    for n, q, k in PANEL_IDS:
        coordinate, nulls = indexed[n, q, k]
        mean = sum(nulls.values(), Fraction(0)) / 32
        gap = mean - coordinate
        wins = sum(nulls[s] > coordinate for s in SEEDS)
        gap_pass, wins_pass = gap >= Fraction(1, 8), wins >= 24
        qualifies[n, q, k] = gap_pass and wins_pass
        panels.append({'N': n, 'q': q, 'kernel': k,
                       'coordinate_delta': rational(coordinate),
                       'nulls': [{'seed': s, 'delta': rational(nulls[s]),
                                  'strict_win': nulls[s] > coordinate} for s in SEEDS],
                       'null_mean': rational(mean), 'gap': rational(gap),
                       'strict_wins': wins, 'gap_pass': gap_pass,
                       'wins_pass': wins_pass, 'qualifies': gap_pass and wins_pass,
                       'reasons': ([] if gap_pass else ['gap_below_1/8']) +
                                  ([] if wins_pass else ['fewer_than_24_strict_wins'])})
    pairs = [{'q': q, 'kernel': k, 'N11_qualifies': qualifies[11, q, k],
              'N17_qualifies': qualifies[17, q, k],
              'qualifies': qualifies[11, q, k] and qualifies[17, q, k]}
             for q in QS for k in KERNELS]
    reasons = []
    validity = metadata.get('validity')
    if validity is not True:
        reasons.append('validity_missing_false_or_unknown')
    controls = metadata.get('controls')
    gate_rows = []
    if type(controls) is not dict:
        reasons.append('controls_missing_or_malformed')
        controls = {}
    if set(controls) - set(CONTROL_NAMES):
        reasons.append('unknown_control_names')
    for name in CONTROL_NAMES:
        passed = controls.get(name) is True
        gate_rows.append({'name': name, 'passed': passed})
        if not passed:
            reasons.append(f'control_not_true:{name}')
    count = sum(p['qualifies'] for p in pairs)
    outcome = INVALID if reasons else POSITIVE if count else NEGATIVE
    return {'evidence_scope': 'precomputed_metadata_only', 'outcome': outcome,
            'validity_passed': validity is True, 'control_gates': gate_rows,
            'gating_reasons': reasons, 'panel_count': 32, 'null_entry_count': 1024,
            'pair_count': 16, 'paired_qualifier_count': count,
            'panels': panels, 'pairs': pairs}
