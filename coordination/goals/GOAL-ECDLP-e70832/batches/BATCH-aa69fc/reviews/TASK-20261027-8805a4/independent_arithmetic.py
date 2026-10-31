#!/usr/bin/env python3
"""Blind primitive-law software check; no production imports or native replay.

Only scientific input: the adjacent batch's sanitized statement. All scalars
below are fixed public test inputs. No benchmark, private input, or clocks.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATEMENT = HERE.parent.parent / "blind-packet" / "statement.json"
SPEC = json.loads(STATEMENT.read_text())
p, a, b, r = (SPEC["parameters"][n] for n in ("p", "a", "b", "r"))
P = tuple(SPEC["parameters"]["P"])
O = None


def on_curve(q):
    return q is O or (q[1] * q[1] - q[0] ** 3 - a * q[0] - b) % p == 0


def opposite(q):
    return O if q is O else (q[0], -q[1] % p)


def reference_add(u, v):
    """Uninstrumented repeated-add oracle; inverse via Fermat, no Probe use."""
    if u is O:
        return v
    if v is O:
        return u
    x, y = u
    X, Y = v
    if x == X and (y + Y) % p == 0:
        return O
    numerator, denominator = ((3 * x * x + a, 2 * y) if u == v else (Y - y, X - x))
    m = numerator * pow(denominator % p, p - 2, p) % p
    z = (m * m - x - X) % p
    return (z, (m * (x - z) - y) % p)


class Probe:
    def __init__(self):
        self.events = []
        self.scalar_calls = 0

    def add(self, u, v, *, role="primitive", scalar_nested=False):
        # Exactly one callback at function entry, including all shortcuts.
        event = dict(index=len(self.events) + 1, u=u, v=v, role=role,
                     scalar_nested=scalar_nested)
        self.events.append(event)
        assert on_curve(u) and on_curve(v)
        if u is O or v is O:
            event["branch"] = "identity"
            out = v if u is O else u
        elif u[0] == v[0] and (u[1] + v[1]) % p == 0:
            event["branch"] = "inverse"
            out = O
        else:
            if u == v:
                event["branch"] = "tangent"
                m = (3 * u[0] ** 2 + a) * pow(2 * u[1] % p, -1, p) % p
            else:
                event["branch"] = "chord"
                m = (v[1] - u[1]) * pow((v[0] - u[0]) % p, -1, p) % p
            x = (m * m - u[0] - v[0]) % p
            out = (x, (m * (u[0] - x) - u[1]) % p)
        event["out"] = out
        assert on_curve(out)
        return out

    def scalar(self, k, point=P):
        if not isinstance(k, int) or k < 0:
            raise ValueError("Specified algorithm has domain integer k >= 0")
        self.scalar_calls += 1
        out, base = O, point
        while k > 0:
            if k & 1:
                out = self.add(out, base, role="accumulator-add", scalar_nested=True)
            k >>= 1
            if k > 0:
                base = self.add(base, base, role="base-double", scalar_nested=True)
        return out

    def counts(self):
        return dict(group_invocations=len(self.events), scalar_calls=self.scalar_calls,
                    scalar_nested_group_invocations=sum(e["scalar_nested"] for e in self.events),
                    scheduled_doubling_invocations=sum(e["role"] in ("base-double", "explicit-double")
                                                       for e in self.events),
                    affine_branch_counts=dict(Counter(e["branch"] for e in self.events)))


def prediction(k):
    bits, weight = k.bit_length(), k.bit_count()
    return dict(bit_length=bits, popcount=weight, accumulator_adds=weight,
                scheduled_doublings=max(bits - 1, 0),
                group_invocations=weight + max(bits - 1, 0))


def check_advertisement(answer, expected_answer, advertised_count, expected_count):
    # Witness equality alone must never certify the cost statement.
    witness_valid = answer == expected_answer
    cost_valid = advertised_count == expected_count
    return dict(witness_valid=witness_valid, cost_valid=cost_valid,
                accepted=witness_valid and cost_valid)


def main():
    assert all(n % d for n in (p, r) for d in range(2, math.isqrt(n) + 1))
    discriminant = (-16 * (4 * a ** 3 + 27 * b ** 2)) % p
    assert discriminant != 0 and on_curve(P) and P is not O
    # Deterministic public, finite softwarecheck; no random trials/cohort.
    oracle = [O]
    for k in range(1, 513):
        oracle.append(reference_add(oracle[-1], P))
    assert oracle[r] is O
    assert all(oracle[k] is not O for k in range(1, r))
    primitive_cases = []
    Q = oracle[2]
    # Include the y=0 exceptional case on the same curve, outside <P>.
    two_torsion = next((x, 0) for x in range(p) if (x ** 3 + a * x + b) % p == 0)
    for name, u, v, expected, role in [
        ("identity-both", O, O, O, "primitive"),
        ("identity-left", O, P, P, "primitive"),
        ("identity-right", P, O, P, "primitive"),
        ("inverse", P, opposite(P), O, "primitive"),
        ("double-P", P, P, Q, "explicit-double"),
        ("ordinary-chord", P, Q, oracle[3], "primitive"),
        ("double-order-two", two_torsion, two_torsion, O, "explicit-double"),
    ]:
        probe = Probe()
        answer = probe.add(u, v, role=role)
        assert answer == expected and len(probe.events) == 1
        primitive_cases.append(dict(name=name, expected=expected, answer=answer,
                                    counts=probe.counts(), events=probe.events))

    selected = [0, 1, 2, 3, 5, 8, 15, 16, 127, 128, 180, 181, 182, 256, 331, 362, 512]
    scalar_cases = []
    all_rows = []
    for k in range(513):
        probe = Probe()
        answer = probe.scalar(k)
        pred, actual = prediction(k), probe.counts()
        assert answer == oracle[k]
        assert actual["group_invocations"] == pred["group_invocations"]
        assert actual["scheduled_doubling_invocations"] == pred["scheduled_doublings"]
        assert actual["scalar_nested_group_invocations"] == actual["group_invocations"]
        assert actual["scalar_calls"] == 1
        row = dict(k=k, prediction=pred, actual=actual, answer=answer)
        all_rows.append(row)
        if k in selected:
            scalar_cases.append(dict(**row, events=probe.events))

    chosen = next(x for x in scalar_cases if x["k"] == 181)
    count = chosen["prediction"]["group_invocations"]
    positive = check_advertisement(chosen["answer"], oracle[181], count, count)
    false_plus_one = check_advertisement(chosen["answer"], oracle[181], count + 1, count)
    assert positive["accepted"] and false_plus_one["witness_valid"]
    assert not false_plus_one["accepted"] and not false_plus_one["cost_valid"]
    wrong_answer = check_advertisement(P, oracle[181], count, count)
    assert not wrong_answer["accepted"] and wrong_answer["cost_valid"]
    branch_example = next(x for x in scalar_cases if x["k"] == 331)
    assert branch_example["actual"]["scheduled_doubling_invocations"] == 8
    assert branch_example["actual"]["affine_branch_counts"]["tangent"] == 9
    identity_base_cases = []
    for k in (0, 1, r, r + 1, 2 * r):
        probe = Probe()
        answer = probe.scalar(k, O)
        pred, actual = prediction(k), probe.counts()
        assert answer is O
        assert actual["group_invocations"] == pred["group_invocations"]
        assert actual["scheduled_doubling_invocations"] == pred["scheduled_doublings"]
        assert actual["affine_branch_counts"].get("identity", 0) == pred["group_invocations"]
        identity_base_cases.append(dict(k=k, point=O, answer=answer, prediction=pred,
                                        actual=actual, events=probe.events))
    payload = dict(
        schema="classical.ecdlp.independent-primitive-check/v1",
        task_id="TASK-20261027-8805a4", joint="J-primitive-law",
        statement_sha256=hashlib.sha256(STATEMENT.read_bytes()).hexdigest(),
        implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        parameters=dict(p=p, a=a, b=b, r=r, P=P),
        validity=dict(p_prime=True, r_prime=True, discriminant_mod_p=discriminant,
                      point_on_curve=True, exact_point_order=r,
                      order_check="All jP for 1 <= j < 181 nonidentity; 181P=O",
                      two_torsion_point=two_torsion),
        analytical_law="G(k)=popcount(k)+max(bit_length(k)-1,0), integer k>=0",
        diagnostic_definitions=dict(scalar_calls="One method entry; zero group charge",
            scalar_nested_group_invocations="Subset of group events in scalar method",
            scheduled_doubling_invocations="Subset tagged base-double or explicit-double",
            affine_branch_counts="Independent branch labels; tangent need not equal scheduled double"),
        primitive_cases=primitive_cases, scalar_cases=scalar_cases,
        identity_base_scalar_cases=identity_base_cases,
        exhaustive_public_softwarecheck=dict(k_min=0, k_max=512, cases=513,
            answer_mismatches=0, group_count_mismatches=0, scheduled_double_mismatches=0,
            summary_sha256=hashlib.sha256(json.dumps(all_rows, sort_keys=True).encode()).hexdigest()),
        controls=dict(scalar=181, exact_group_count=count, positive=positive,
            false_plus_one=dict(advertised_count=count+1, **false_plus_one), wrong_answer=wrong_answer),
        scope="Independent public-fixture primitive softwarecheck only; no native execution, benchmark or clock qualification")
    destination = HERE / "predicted-counts.json"
    destination.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps(dict(output=str(destination), cases=513, primitive_cases=len(primitive_cases),
                          law=payload["analytical_law"], controls=payload["controls"],
                          validity=payload["validity"]), indent=2))


if __name__ == "__main__":
    main()
