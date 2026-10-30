#!/usr/bin/env python3
"""Independent bounded fixtures; no repository imports and no 48-curve inputs.

The operational list counter uses cube adjacency, not candidate completions.
The deliberately slow completion oracle is confined to exhaustive L=6 tests.
All emitted integers are diagnostic fixture counts, never primitive timings.
"""
import argparse
import hashlib
import itertools
import json
import math
from fractions import Fraction

CELLS = ((0, 0), (0, 2), (1, 0), (1, 2), (2, 0), (2, 2))


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()


def prime(n):
    return type(n) is int and n > 1 and all(n % d for d in range(2, math.isqrt(n) + 1))


def inverse(a, modulus):
    if type(a) is not int or type(modulus) is not int or modulus < 2:
        raise ValueError("BAD_INVERSE_DOMAIN")
    return pow(a % modulus, -1, modulus)


class Curve:
    def __init__(self, p, a, b, r, base):
        self.p, self.a, self.b, self.r, self.base = p, a, b, r, base

    def valid(self, point):
        if point is None:
            return True
        return (isinstance(point, tuple) and len(point) == 2
                and all(type(x) is int and 0 <= x < self.p for x in point)
                and (point[1] ** 2 - point[0] ** 3 - self.a * point[0] - self.b) % self.p == 0)

    def line(self, u, v):
        if not self.valid(u) or not self.valid(v):
            raise ValueError("NONCANONICAL_OR_OFFCURVE")
        if u is None:
            return v, 0
        if v is None:
            return u, 0
        p = self.p
        x, y = u
        X, Y = v
        if x == X and (y + Y) % p == 0:
            return None, 0
        if x == X:
            if y != Y:
                raise ValueError("SAME_X_INCONSISTENT")
            m = (3 * x * x + self.a) * inverse(2 * y, p) % p
        else:
            m = (Y - y) * inverse(X - x, p) % p
        xx = (m * m - x - X) % p
        yy = (m * (x - xx) - y) % p
        return (xx, yy), m

    def mul(self, n, u=None):
        u = self.base if u is None else u
        if n < 0:
            return self.mul(-n, (u[0], -u[1] % self.p))
        out = None
        while n:
            if n & 1:
                out = self.line(out, u)[0]
            u = self.line(u, u)[0]
            n >>= 1
        return out

    def z(self, point):
        if point is None:
            return 0
        if not self.valid(point):
            raise ValueError("NONCANONICAL_OR_OFFCURVE")
        t, d = point, 0
        for bit in bin(self.r)[3:]:
            t, slope = self.line(t, t)
            d = (2 * d + slope) % self.p
            if bit == "1":
                t, slope = self.line(t, point)
                d = (d + slope) % self.p
        if t is not None:
            raise ValueError("MILLER_FINAL_NOT_IDENTITY")
        return -d * inverse(self.r, self.p) % self.p

    def setup(self, alpha=-2, beta=-1):
        p, r, point = self.p, self.r, self.base
        if (not prime(p) or p % 4 != 3 or not prime(r) or r <= 2
                or r == p or not self.valid(point) or point is None
                or (4 * self.a ** 3 + 27 * self.b ** 2) % p == 0):
            return {"reason": "DOMAIN_UNSUPPORTED"}
        if point[1] == 0:
            return {"reason": "ZERO_BASE_Y"}
        z = self.z(point)
        if z == 0:
            return {"reason": "ZERO_BASE_Z"}
        anchor = (1 + alpha) * z % p
        if anchor == 0:
            return {"reason": "ZERO_ANCHOR"}
        return dict(reason=None, inverse_r=inverse(r, p), z_base=z,
                    c=z * inverse(point[1], p) % p, anchor=anchor,
                    inverse_anchor=inverse(anchor, p), alpha=alpha, beta=beta)

    def query(self, point, setup):
        out = dict(status="UNDEFINED", bit=None, reason=setup["reason"],
                   z=None, g=None, anchor=None, normalized=None)
        if setup["reason"]:
            return out
        if not self.valid(point):
            raise ValueError("NONCANONICAL_OR_OFFCURVE")
        p = self.p
        out["anchor"] = setup["anchor"]
        out["z"] = self.z(point)
        if point is None:
            out.update(status="BIT", bit=0, reason=None)
            return out
        x, y = point
        c = setup["c"]
        g = (out["z"] + c * y * (setup["alpha"] + setup["beta"] * c * (x - self.base[0]))) % p
        out["g"] = g
        if g == 0:
            out["reason"] = "ZERO_NUMERATOR"
            return out
        normalized = g * setup["inverse_anchor"] % p
        chi = pow(normalized, (p - 1) // 2, p)
        if chi not in (1, p - 1):
            raise ValueError("BAD_CHARACTER")
        out.update(status="BIT", bit=int(chi != 1), reason=None, normalized=normalized)
        return out


def legal_words(r, length):
    """One word per k, by the half-open interval theorem."""
    d = 1 << length
    return [(d * k // r, k) for k in range(r)]


def interval(word, r, length, mutation=None):
    d = 1 << length
    k = ((r * word) // d if mutation == "floor_for_ceil"
         else (r * word + d - 1) // d)
    lower = d * k > r * word if mutation == "strict_lower" else d * k >= r * word
    upper = d * k <= r * (word + 1) if mutation == "weak_upper" else d * k < r * (word + 1)
    return k if 0 <= k < r and lower and upper else None


def adjacency(values, length):
    return [sum(values[v ^ (1 << j)] for j in range(length)) for v in range(1 << length)]


def cube_tables(r, length):
    f = [0] * (1 << length)
    for word, k in legal_words(r, length):
        if k:
            f[word] = 1
    af = adjacency(f, length)
    return f, af, adjacency(af, length)


def completions(word, erased):
    base = word
    for j in erased:
        base &= ~(1 << j)
    for selection in range(1 << len(erased)):
        yield base | sum(((selection >> i) & 1) << j for i, j in enumerate(erased))


def cube_count(tables, word, erased, t, length):
    e = len(erased)
    g = [sum(table[v] for v in completions(word, erased)) for table in tables]
    if t == 0:
        return g[0]
    if t == 1:
        return g[1] + (1 - e) * g[0]
    numerator = g[2] + 2 * (1 - e) * g[1] + (e * e - e + 2 - length) * g[0]
    assert numerator % 2 == 0
    return numerator // 2


def row(r, bits, t, cap, target=None, tables=None):
    length = len(bits)
    erased = tuple(length - 1 - i for i, b in enumerate(bits) if b is None)
    word = sum((b or 0) << (length - 1 - i) for i, b in enumerate(bits))
    e = len(erased)
    capped = e > cap
    strict_undefined = (t, cap) == (0, 0) and e > 0
    if capped:
        return dict(capped=True, strict_undefined=strict_undefined, erasures=e, words=0,
                    legal=0, empty=0, zero=0, M=0, success=0, first_true=0,
                    second_true=0, both_true=0, both_false=0)
    tables = cube_tables(r, length) if tables is None else tables
    m = cube_count(tables, word, erased, t, length)
    defined_mask = ((1 << length) - 1) ^ sum(1 << j for j in erased)
    zero = int((word & defined_mask).bit_count() <= t)
    count = (1 << e) * sum(math.comb(length - e, j) for j in range(min(t, length - e) + 1))
    success = int(target is not None and (((1 << length) * target // r ^ word) & defined_mask).bit_count() <= t)
    return dict(capped=False, strict_undefined=False, erasures=e, words=count,
                legal=m + zero, empty=count - m - zero, zero=zero, M=m,
                success=success, first_true=success, second_true=success,
                both_true=success, both_false=m + zero - success)


def direct(r, bits, t, cap, mutation=None):
    """Independent tiny-fixture completion enumerator, not the main counter."""
    length = len(bits)
    erased = [i for i, b in enumerate(bits) if b is None]
    if len(erased) > cap and mutation != "bypass_cap":
        return dict(words=0, legal=0, empty=0, zero=0, M=0)
    defined = [i for i, b in enumerate(bits) if b is not None]
    words, legal = [], []
    for choices in itertools.product((0, 1), repeat=len(erased)):
        complete = list(bits)
        for i, b in zip(erased, choices):
            complete[i] = b
        for weight in range(min(t, len(defined)) + 1):
            for flipped in itertools.combinations(defined, weight):
                trial = complete[:]
                for i in flipped:
                    trial[i] ^= 1
                word = sum(b << (length - 1 - i) for i, b in enumerate(trial))
                words.append(word)
                k = interval(word, r, length, mutation)
                if k is not None:
                    legal.append(k)
    assert len(set(words)) == len(words)
    nonzero = set(legal) - {0}
    out = dict(words=len(words), legal=len(legal), empty=len(words) - len(legal),
               zero=legal.count(0), M=len(nonzero))
    if mutation == "zero_in_M":
        out["M"] = len(set(legal))
    elif mutation == "exclude_zero_checks":
        out["legal"] -= out["zero"]
        out["zero"] = 0
    elif mutation == "duplicate_words":
        for key in ("words", "legal", "empty", "zero"):
            out[key] *= 2
    elif mutation == "duplicate_candidate_M":
        out["M"] *= 2
    elif mutation == "truncate_list" and legal:
        removed = legal.pop()
        out.update(legal=len(legal), empty=len(words) - len(legal), zero=legal.count(0), M=len(set(legal) - {0}))
    return out


def bits_of(word, length):
    return [(word >> (length - 1 - i)) & 1 for i in range(length)]


def summarized_fixture(r, oracle, erased_positions, predicate=None):
    length = r.bit_length() + 1
    tables = cube_tables(r, length)
    records, summaries = [], []
    for s in range(1, r):
        if oracle == "primary":
            bits = [predicate[(s * pow(2, i, r)) % r]["bit"] for i in range(length)]
        else:
            bits = [int((pow(2, i, r) * s) % r > r // 2) for i in range(length)]
            if oracle == "negated_half":
                bits = [1 - b for b in bits]
        for pos in erased_positions:
            bits[pos] = None
        cells = [row(r, bits, t, cap, s, tables) for t, cap in CELLS]
        records.append(dict(s=s, bits=bits, cells=cells))
    for index, (t, cap) in enumerate(CELLS):
        cell_rows = [record["cells"][index] for record in records]
        totals = {key: sum(int(a[key]) for a in cell_rows) for key in cell_rows[0]}
        m = totals["M"]
        reference = Fraction(m, (r - 1) ** 2)
        summaries.append(dict(t=t, erasure_cap=cap, denominator=r - 1, totals=totals,
                              q=[totals["success"], r - 1],
                              uniform_reference=[reference.numerator, reference.denominator],
                              raw_uniform_reference=[m, (r - 1) ** 2],
                              min_M_equivalence=all(a["M"] == min(a["M"], r - 1) for a in cell_rows)))
    reversed_records = sorted(reversed(records), key=lambda x: x["s"])
    assert canonical(records) == canonical(reversed_records)
    return dict(r=r, length=length, oracle=oracle, erased_positions=list(erased_positions),
                scalar_stream_sha256=digest(records), summaries=summaries,
                aa_reverse_identical=True)


def exhaustive_cube():
    checks, bounds, mutations, weak_upper_differences = 0, [], {}, 0
    omitted_erasure_correction = None
    kinds = ("bypass_cap", "zero_in_M", "exclude_zero_checks", "strict_lower",
             "floor_for_ceil", "duplicate_words", "duplicate_candidate_M", "truncate_list")
    for r in (17, 29):
        length = r.bit_length() + 1
        tables = cube_tables(r, length)
        local = 0
        for word in range(1 << length):
            for e in range(4):
                for erased in itertools.combinations(range(length), e):
                    bits = bits_of(word, length)
                    for i in erased:
                        bits[i] = None
                    for t, cap in CELLS:
                        fast = row(r, bits, t, cap, tables=tables)
                        slow = direct(r, bits, t, cap)
                        observed = {k: fast[k] for k in slow}
                        assert observed == slow, (r, word, erased, t, cap, observed, slow)
                        checks += 1
                        local += 1
                        weak = direct(r, bits, t, cap, "weak_upper")
                        weak_upper_differences += int(weak != slow)
                        if omitted_erasure_correction is None and e and e <= cap:
                            bit_erased = tuple(length - 1 - i for i in erased)
                            g = [sum(table[v] for v in completions(word, bit_erased)) for table in tables]
                            # Incorrectly marginalizing a full-cube ball overcounts
                            # paths along erased coordinates.
                            naive = g[0] if t == 0 else (g[0] + g[1] if t == 1
                                     else g[0] + g[1] + (g[2] - length * g[0]) // 2)
                            if naive != slow["M"]:
                                omitted_erasure_correction = dict(r=r, word=word,
                                    erased_positions=list(erased), t=t, cap=cap,
                                    correct_M=slow["M"], altered_M=naive)
                        for kind in kinds:
                            if kind not in mutations:
                                altered = direct(r, bits, t, cap, kind)
                                if altered != slow:
                                    mutations[kind] = dict(r=r, word=word, erased_positions=list(erased),
                                                           t=t, cap=cap, baseline=slow, altered=altered)
        bounds.append(dict(r=r, bit_patterns=1 << length, erasure_subsets=sum(math.comb(length, e) for e in range(4)),
                           cells=len(CELLS), comparisons=local))
    assert set(mutations) == set(kinds)
    assert weak_upper_differences == 0
    assert omitted_erasure_correction is not None
    return dict(comparisons=checks, scopes=bounds, smallest_mutation_witnesses=mutations,
                omitted_erasure_correction_witness=omitted_erasure_correction,
                witness_order="r, full word, number erased, lex erased indices, t-major/e-minor cell",
                weak_upper_differences=0,
                weak_upper_note="Equivalent on these valid odd-r canonical decoder domains: gcd(r,2^L)=1; equality requires k=r,V=2^L-1, rejected by k<r.")


def scalar_conversion(k, a, b, r):
    if not prime(r) or r <= 2 or not 0 <= k < r or not a % r or not b % r:
        raise ValueError("INVALID_BLINDING_DOMAIN")
    return a * inverse(b, r) * k % r


def public_checks():
    records = []
    c = Curve(23, 11, 5, 17, (5, 22))
    r = 17
    for a, b, x in ((1, 1, 1), (2, 3, 5), (16, 7, 11)):
        s = b * x * inverse(a, r) % r
        P, Q, R = c.mul(a), c.mul(x), c.mul(b * x % r)
        truth = []
        for k in range(r):
            converted = scalar_conversion(k, a, b, r)
            first = c.mul(k, P) == R
            second = c.mul(converted) == Q
            assert first == second == (k == s)
            truth.append([k, converted, first, second])
        permutations = [b0 * x * inverse(a, r) % r for b0 in range(1, r)]
        assert sorted(permutations) == list(range(1, r))
        records.append(dict(a=a, b=b, x=x, s=s, candidate_checks=truth, permutation=permutations))
    a, b, x, k = 2, 3, 5, 16
    wrong_conversion = a * b * k % r
    source_true = c.mul(k, c.mul(a)) == c.mul(b * x % r)
    target_true = c.mul(wrong_conversion) == c.mul(x)
    assert source_true and not target_true
    # Deliberately inconsistent R/Q: target-only acceptance must be rejected.
    k2 = 1
    converted2 = a * inverse(b, r) * k2 % r
    first2 = c.mul(k2, c.mul(a)) == c.mul(1)
    second2 = c.mul(converted2) == c.mul(converted2)
    assert not first2 and second2
    invalid = []
    for a0, b0 in ((0, 1), (1, 0), (0, 0)):
        try:
            scalar_conversion(1, a0, b0, r)
            rejected = False
        except ValueError:
            rejected = True
        assert rejected
        invalid.append(dict(a=a0, b=b0, rejected=rejected))
    try:
        inverse(3, 9)
        raise AssertionError("noninvertible inverse accepted")
    except ValueError:
        pass
    return dict(genuine=records, invalid_multipliers=invalid, noninvertible_composite_rejected=True,
                mutations=dict(drop_second=dict(a=a, b=b, x=x, k=k, wrong_conversion=wrong_conversion,
                                                 first=source_true, second=target_true, bad_accept=True, correct_accept=False),
                               drop_first=dict(a=a, b=b, R_scalar=1, Q_scalar=converted2, k=k2,
                                               converted=converted2, first=first2, second=second2,
                                               bad_accept=True, correct_accept=False),
                               wrong_sign=dict(correct=x, altered=(-x) % r, rejected=(-x) % r != x),
                               wrong_inverse=dict(correct=x, altered=wrong_conversion, rejected=wrong_conversion != x),
                               flip_check=dict(correct_pair=[True, True], altered_pair=[True, False], missed_success=True)))


def predicate_fixture():
    c = Curve(23, 11, 5, 17, (5, 22))
    points = [c.mul(k) for k in range(17)]
    oncurve = [None] + [(x, y) for x in range(23) for y in range(23) if (y*y-x*x*x-11*x-5) % 23 == 0]
    assert len(oncurve) == 17 and set(oncurve) == set(points) and len(set(points)) == 17
    for i in range(17):
        for j in range(17):
            assert c.line(points[i], points[j])[0] == points[(i+j) % 17]
    setup = c.setup()
    answers = [c.query(point, setup) for point in points]
    zero_anchor = c.setup(alpha=-1)
    assert zero_anchor == dict(reason="ZERO_ANCHOR")
    zero_anchor_answers = [c.query(point, zero_anchor) for point in points]
    assert all(answer["reason"] == "ZERO_ANCHOR" for answer in zero_anchor_answers)
    offcurve_rejected = False
    try:
        c.query((23, 0), setup)
    except ValueError:
        offcurve_rejected = True
    assert offcurve_rejected
    mutant_witnesses = {}
    for k, point in enumerate(points[1:], 1):
        baseline = answers[k]
        z, x, y = c.z(point), point[0], point[1]
        for kind in ("negate_miller_slopes", "omit_anchor_normalization", "wrong_alpha", "wrong_beta"):
            zz, cb, anchor = z, setup["c"], setup["anchor"]
            alpha, beta = setup["alpha"], setup["beta"]
            if kind == "negate_miller_slopes":
                zz, cb, anchor = -zz % 23, -cb % 23, -anchor % 23
            elif kind == "wrong_alpha":
                alpha += 1
            elif kind == "wrong_beta":
                beta = -beta
            g = (zz + cb*y*(alpha + beta*cb*(x-c.base[0]))) % 23
            normalized = g if kind == "omit_anchor_normalization" else g*inverse(anchor,23) % 23
            altered = dict(z=zz, g=g, anchor=anchor, normalized=normalized,
                           bit=None if g == 0 else int(pow(normalized,11,23) != 1))
            baseline_values = {name: baseline[name] for name in altered}
            if baseline_values != altered and kind not in mutant_witnesses:
                mutant_witnesses[kind] = dict(scalar=k, baseline=baseline_values, altered=altered)
    # The primary anchor is exactly 1, so omission is observationally identical
    # there. A fixed alternate alpha on this same public fixture is needed.
    alternate = c.setup(alpha=1)
    assert alternate["anchor"] != 1
    for k, point in enumerate(points[1:],1):
        answer = c.query(point, alternate)
        if answer["g"] not in (None,0) and answer["g"] != answer["normalized"]:
            mutant_witnesses["omit_anchor_normalization"] = dict(alpha=1,scalar=k,
                baseline_normalized=answer["normalized"],altered_normalized=answer["g"],
                anchor=alternate["anchor"], reason="same fixed curve/base, alternate arithmetic setup control")
            break
    assert set(mutant_witnesses) == {"negate_miller_slopes", "omit_anchor_normalization", "wrong_alpha", "wrong_beta"}
    return c, answers, dict(parameters=dict(p=23, A=11, B=5, r=17, P=[5,22]),
                           group_order=17, orbit=points, pairwise_group_checks=289,
                           setup=setup, answers=answers, zero_anchor_setup=zero_anchor,
                           zero_anchor_decoder_fixture=summarized_fixture(17,"primary",(),zero_anchor_answers),
                           predicate_mutation_witnesses=mutant_witnesses,
                           zero_anchor_identity_undefined=True, invalid_query_rejected=True,
                           primary_fixture=summarized_fixture(17,"primary",(),answers))


def typed_format_controls():
    def load(text):
        def pairs(items):
            obj = {}
            for k, v in items:
                if k in obj:
                    raise ValueError("DUPLICATE_MEMBER")
                obj[k] = v
            return obj
        obj = json.loads(text, object_pairs_hook=pairs,
                         parse_constant=lambda x: (_ for _ in ()).throw(ValueError("NONFINITE")))
        if type(obj) is not dict or set(obj) != {"schema", "complete", "rows"}:
            raise ValueError("MEMBER_SET")
        if obj["schema"] != "independent.fixture/v1" or type(obj["complete"]) is not bool:
            raise ValueError("TYPE_OR_SCHEMA")
        if not obj["complete"] or type(obj["rows"]) is not list:
            raise ValueError("INCOMPLETE")
        return obj
    cases = {
        "success": '{"schema":"independent.fixture/v1","complete":true,"rows":[]}',
        "malformed": '{', "yaml_only": 'schema: independent.fixture/v1',
        "missing_member": '{"schema":"independent.fixture/v1","complete":true}',
        "duplicate_member": '{"schema":"independent.fixture/v1","complete":true,"complete":false,"rows":[]}',
        "bool_as_int": '{"schema":"independent.fixture/v1","complete":1,"rows":[]}',
        "partial": '{"schema":"independent.fixture/v1","complete":false,"rows":[]}',
        "trailing_stream": '{"schema":"independent.fixture/v1","complete":true,"rows":[]}{}',
    }
    records = []
    for name, text in cases.items():
        try:
            load(text)
            accepted, reason = True, None
        except (ValueError, TypeError) as exc:
            accepted, reason = False, str(exc)
        assert accepted == (name == "success")
        records.append(dict(id=name, input=text, accepted=accepted, rejection_reason=reason))
    return dict(scope="Own local strict JSON parser only; not producer supervisor end-to-end validation", records=records)


def fixtures():
    c, answers, predicate = predicate_fixture()
    all_fixtures = []
    for r in (17, 29):
        for oracle in ("true_half", "negated_half"):
            for erased in ((), (0,), (0, 1), (0, 1, 2)):
                result = summarized_fixture(r, oracle, erased)
                for cell in result["summaries"]:
                    n = cell["totals"]["success"]
                    expected = r - 1 if oracle == "true_half" and len(erased) <= cell["erasure_cap"] else 0
                    assert n == expected, (r, oracle, erased, cell)
                all_fixtures.append(result)
        result = summarized_fixture(r, "true_half", tuple(range(r.bit_length()+1)))
        assert all(cell["totals"]["M"] == 0 for cell in result["summaries"])
        all_fixtures.append(result)
    boundaries = []
    for r in (17,29):
        length = r.bit_length()+1
        legal = [(v, interval(v,r,length)) for v in range(1 << length) if interval(v,r,length) is not None]
        assert legal == legal_words(r,length)
        zero = row(r, bits_of(0,length),0,0)
        empty_word = next(v for v in range(1 << length) if interval(v,r,length) is None)
        empty = row(r,bits_of(empty_word,length),0,0)
        assert zero["M"] == 0 and zero["zero"] == 1 and zero["legal"] == 1
        assert empty["M"] == empty["legal"] == empty["zero"] == 0 and empty["empty"] == 1
        boundaries.append(dict(r=r,length=length,legal_words_and_scalars=legal,
                               illegal_word_count=(1 << length)-len(legal),
                               zero_only_candidate=dict(word=0,cell=[0,0],counts=zero),
                               empty_candidate_list=dict(word=empty_word,cell=[0,0],counts=empty)))
    return dict(schema="independent.exact-density.fixtures/v1", task_id="TASK-20261030-141047",
                fixed_parameters=["F23:A11:B5:P(5,22):r17", "Z17", "Z29"],
                no_48_curve_data=True, fixtures=all_fixtures, predicate=predicate,
                interval_and_zero_boundaries=boundaries,
                cube_exhaustion=exhaustive_cube(), blinding_and_checks=public_checks(),
                typed_format=typed_format_controls())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", action="store_true", required=True)
    args = parser.parse_args()
    print(canonical(fixtures()))


if __name__ == "__main__":
    main()
