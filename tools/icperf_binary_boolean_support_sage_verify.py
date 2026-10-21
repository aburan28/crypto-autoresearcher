"""Independent Sage checks for binary chain ANF support and evaluations."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from sage.all import GF, PolynomialRing
from sage.version import version as sage_version


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--support", type=Path, required=True)
    parser.add_argument("--controls", type=Path, required=True)
    parser.add_argument("--chain", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    support_bytes, control_bytes, chain_bytes = (p.read_bytes() for p in
                                                 (args.support, args.controls, args.chain))
    support, controls, chain = (json.loads(p) for p in
                                (support_bytes, control_bytes, chain_bytes))
    assert support["chain_sha256"] == hashlib.sha256(chain_bytes).hexdigest()
    assert controls["parent_support_sha256"] == hashlib.sha256(support_bytes).hexdigest()
    assert controls["chain_sha256"] == hashlib.sha256(chain_bytes).hexdigest()
    ring = PolynomialRing(GF(2), "t")
    t = ring.gen()
    modulus = t**61+t**5+t**2+t+1
    assert modulus.is_irreducible()
    field = GF(2**61, name="z", modulus=modulus)
    z = field.gen()
    zero = field.zero()

    def elem(bits):
        return sum((z**i for i in range(61) if (int(bits) >> i) & 1), zero)

    def bits(value):
        return sum(int(c) << i for i, c in enumerate(value.polynomial().list()))

    gamma, curve_b = elem(chain["gamma"]), elem(31)

    def add(*polys):
        out = {}
        for poly in polys:
            for key, value in poly.items():
                new_value = out.get(key, zero) + value
                if new_value:
                    out[key] = new_value
                else:
                    out.pop(key, None)
        return out

    def product(a, b):
        out = {}
        for key_a, val_a in a.items():
            for key_b, val_b in b.items():
                key = key_a | key_b  # Boolean quotient in a second representation
                value = out.get(key, zero) + val_a*val_b
                if value:
                    out[key] = value
                else:
                    out.pop(key, None)
        return out

    def square(poly):
        return {key: value**2 for key, value in poly.items()}

    def const(value):
        return {frozenset(): value} if value else {}

    def var(offset, width, first):
        out = const(elem(offset))
        for j in range(width):
            out[frozenset((first+j,))] = z**j
        return out

    def phi3(values):
        linear = [add(square(v), v) for v in values]
        return add(product(product(linear[0], linear[1]), linear[2]),
                   {key: gamma*value for key, value in square(add(*values)).items()})

    def s3(values):
        a,b,c = values
        e2 = add(product(a,b), product(a,c), product(b,c))
        return add(square(e2), product(product(a,b),c), const(curve_b))

    def field_triples(kind, k, offset, target):
        bases = [var(offset,k,i*k) for i in range(8)]
        full = [var(0,61,8*k+i*61) for i in range(6)]
        return [[bases[0],bases[1],full[0]],
                [full[0],bases[2],full[1]],
                [full[-1],bases[-1],const(elem(target))]], bases, full

    def polynomial_stats(poly, nvars):
        degree_hist = {}
        per_bit = [0]*61
        h = hashlib.sha256()
        width = (nvars+7)//8
        rows = []
        for key, coeff in poly.items():
            mask = sum(1 << index for index in key)
            coeff_bits = bits(coeff)
            degree = len(key)
            degree_hist[degree] = degree_hist.get(degree,0)+coeff_bits.bit_count()
            for j in range(61):
                per_bit[j] += (coeff_bits >> j)&1
            rows.append((mask,coeff_bits))
        for mask, coeff in sorted(rows):
            h.update(mask.to_bytes(width,"big"))
            h.update(coeff.to_bytes(8,"big"))
        return {"unique_field_monomials": len(rows),
                "coefficient_bit_terms": sum(per_bit),
                "boolean_degree_bit_terms": {str(k):v for k,v in sorted(degree_hist.items())},
                "max_boolean_input_degree": max(degree_hist,default=0),
                "per_output_bit_terms": per_bit,
                "support_sha256": h.hexdigest()}

    def eval_group(poly, assignment):
        out = zero
        for key, coeff in poly.items():
            if all((assignment >> i)&1 for i in key):
                out += coeff
        return out

    verification = []
    for record, source in ((support,"selected_bases"),(controls,"matched_width_controls")):
        for arm in record["arms"]:
            kind, k = arm["kind"], arm["base_dimension"]
            offset = arm.get("selected_offset", arm.get("offset"))
            nvars = arm["boolean_variables"]
            assert nvars == 8*k+6*61
            triples,bases,full = field_triples(kind,k,offset,arm["target_coordinate"])
            formula = phi3 if kind == "torsion_phi" else s3
            checked = []
            for index, triple in zip((0,1,6),triples):
                poly = formula(triple)
                stats = polynomial_stats(poly,nvars)
                assert stats == arm["equation_stats"][index], (source,kind,index)
                checked.append(index)
            assert all(arm["equation_stats"][i]["coefficient_bit_terms"] ==
                       arm["equation_stats"][1]["coefficient_bit_terms"] for i in range(1,6))

            # Evaluate every recorded assignment using Sage field arithmetic
            # and the original field equations, independent of producer ANF.
            def value_of(poly, assignment):
                return eval_group(poly, assignment)

            all_triples = [[bases[0],bases[1],full[0]]]
            all_triples += [[full[i-1],bases[i+1],full[i]] for i in range(1,6)]
            all_triples += [[full[-1],bases[-1],const(elem(arm["target_coordinate"]))]]
            for trial in arm["trial_rows"]:
                mask = int(trial["assignment_hex"],16)
                values = []
                for triple in all_triples:
                    scalars = [value_of(poly,mask) for poly in triple]
                    if kind == "torsion_phi":
                        v = ((scalars[0]**2+scalars[0]) * (scalars[1]**2+scalars[1]) *
                             (scalars[2]**2+scalars[2]) + gamma*sum(scalars,zero)**2)
                    else:
                        a,b,c = scalars
                        v = (a*b+a*c+b*c)**2 + a*b*c + curve_b
                    values.append(bits(v))
                assert values == trial["field_equation_values"]
            verification.append({"source":source,"kind":kind,"base_dimension":k,
                                 "exact_equation_indices":checked,
                                 "random_assignments_checked":len(arm["trial_rows"])})

    result = {"schema":"icperf-binary-boolean-support-sage-replay-v1",
              "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "support_sha256":hashlib.sha256(support_bytes).hexdigest(),
              "controls_sha256":hashlib.sha256(control_bytes).hexdigest(),
              "chain_sha256":hashlib.sha256(chain_bytes).hexdigest(),
              "sage_version":sage_version,"python_version":sys.version,
              "verification":verification,
              "scope":"independent first/middle/last ANF counts and field evaluations; no solving-degree result"}
    with args.out.open("x") as stream:
        json.dump(result,stream,sort_keys=True,indent=2)
        stream.write("\n")
    print(json.dumps({"path":str(args.out),"arms_checked":len(verification)},sort_keys=True))


if __name__ == "__main__":
    main()
