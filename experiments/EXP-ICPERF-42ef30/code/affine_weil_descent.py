"""S4 Weil descent over an explicitly declared affine binary factor-base slice.

Run with Sage's Python environment.  This is implementation preparation for
EXP-ICPERF-42ef30 AP-2, not an experiment launcher or a solve certificate.
The byte-identity history and remaining parser admission are tracked in
../../../problems/affine-weil-descent-byte-identity.md.
The input x coordinates are x = offset + sum(bit_j * basis_j), independently
for each of the three factor-base points.  The target is an explicit field
element; all field elements use polynomial-basis integer encoding.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from sage.all import GF, Ideal, PolynomialRing, expand


def _field_poly(value: int, variable):
    """Return the polynomial-basis expansion of an encoded GF(2^n) element."""
    return sum(variable**i for i in range(value.bit_length()) if value & (1 << i))


def _sr_mod(poly, modulus, variable):
    """Use the same leading-term cancellation as upstream Weil_descent.sage."""
    while poly.degree() >= modulus.degree():
        poly -= poly.lc() * variable ** (poly.degree() - modulus.degree()) * modulus
    return poly


def _remove_powers(poly, field_equations):
    # Match the upstream Boolean reduction. Output order is handled separately
    # by the C producer's degree/group/coordinate serialization convention.
    for equation in field_equations:
        poly = Ideal(poly, equation).groebner_basis()[0]
    return poly


def _ordered_terms(poly, names):
    """Return nonconstant Boolean terms in the shipped C producer's order."""
    groups = [int(name.split("_")[1]) for name in names]
    coordinates = [int(name.split("_")[2]) for name in names]
    terms = []
    for monomial in poly.monomials():
        exponents = next(iter(monomial.dict()))
        if any(power > 1 for power in exponents):
            raise ValueError("non-Boolean monomial in descended equation")
        indices = tuple(i for i, power in enumerate(exponents) if power)
        if indices:
            terms.append(indices)
    return sorted(terms, key=lambda indices: (
        len(indices), tuple(groups[i] for i in indices),
        tuple(coordinates[i] for i in indices)))


def _anf_terms(poly, names, variable_offset):
    result = ""
    for indices in _ordered_terms(poly, names):
        if len(indices) > 1:
            result += f" .{len(indices)}"
        result += "".join(f" {i + variable_offset + 1}" for i in indices)
    return result


def _anf_x(nb_vars_x, nb_vars, n, equations, names):
    out = f"p cnf {nb_vars} {len(equations) + n}\n"
    equation_id = nb_vars_x
    for poly in equations:
        equation_id += 1
        out += f"x{'' if poly.constant_coefficient() == 1 else ' T'} {equation_id}"
        out += _anf_terms(poly, names, 0)
        out += " 0\n"
    return out


def _anf_e(offset, equations, names):
    out = ""
    for poly in equations:
        out += "x" if poly.constant_coefficient() == 1 else "x T"
        out += _anf_terms(poly, names, offset)
        out += " 0\n"
    return out


def _magma_terms(poly, names):
    return ["*".join(names[i] for i in indices)
            for indices in _ordered_terms(poly, names)]


def build_instance(n: int, basis: list[int], offset: int, target: int):
    """Return (Magma input, WDSat ANF, metadata) without writing files."""
    if n < 3 or not basis or len(basis) >= n:
        raise ValueError("require n >= 3 and 1 <= dimension < n")
    if any(value < 0 or value >= 1 << n for value in [*basis, offset, target]):
        raise ValueError("field element outside polynomial-basis n-bit range")

    l = len(basis)
    field = GF(2**n, name="a")
    modulus_coefficients = [int(v) for v in field.modulus().coefficients(sparse=False)]
    if len(modulus_coefficients) != n + 1:
        raise ValueError("unexpected field modulus degree")
    # Independent F_2-rank check before the basis is used as a slice.
    echelon = [0] * n
    for value in basis:
        residue = value
        while residue:
            pivot = residue.bit_length() - 1
            if echelon[pivot]:
                residue ^= echelon[pivot]
            else:
                echelon[pivot] = residue
                break
        if not residue:
            raise ValueError("factor-base basis is linearly dependent")

    nb_vars_x = 3 * l
    x_names = [f"x_{block + 1}_{j}" for block in range(3) for j in range(l)]
    rx_base = PolynomialRing(field, names=x_names)
    x_poly = PolynomialRing(rx_base, "x")
    x = x_poly.gen()
    xc = rx_base.gens()
    irr_x = sum(modulus_coefficients[k] * x**k for k in range(n + 1))

    def point_x(block):
        poly = _field_poly(offset, x)
        for j, value in enumerate(basis):
            poly += xc[block * l + j] * _field_poly(value, x)
        return poly

    x1, x2, x3 = (point_x(i) for i in range(3))
    e1 = _sr_mod(x1 + x2 + x3, irr_x, x)
    e2 = _sr_mod(x1 * x2 + x1 * x3 + x2 * x3, irr_x, x)
    e3 = _sr_mod(x1 * x2 * x3, irr_x, x)
    widths = [int(poly.degree()) + 1 for poly in (e1, e2, e3)]
    nb_vars_e = sum(widths)
    nb_vars = nb_vars_x + nb_vars_e

    e_names = [f"e_{block + 1}_{j}" for block, width in enumerate(widths)
               for j in range(width)]
    re_base = PolynomialRing(field, names=e_names)
    e_poly = PolynomialRing(re_base, "e")
    e = e_poly.gen()
    ec = re_base.gens()
    field_equations = [var**2 + var for var in ec]
    irr_e = sum(modulus_coefficients[k] * e**k for k in range(n + 1))

    coeffs = []
    for poly in (e1, e2, e3):
        coeffs.extend(expand(coefficient) for coefficient in poly.coefficients(sparse=False))
    eqs_x = coeffs
    eqs_x_str = []
    for i, poly in enumerate(eqs_x):
        summands = [str(ec[i])]
        if poly.constant_coefficient() == 1:
            summands.append("1")
        summands.extend(_magma_terms(poly, x_names))
        eqs_x_str.append(" + ".join(summands))

    offset_e = 0
    symmetric = []
    for width in widths:
        symmetric.append(sum(ec[offset_e + k] * e**k for k in range(width)))
        offset_e += width
    sym1, sym2, sym3 = symmetric
    xr = _field_poly(target, e)
    f3 = (
        xr**4 + sym1**4 + sym3**4 + sym2**4 * xr**4
        + sym3**3 * xr + sym3 * sym2**2 * xr**3
        + sym3 * sym1**2 * xr + sym3 * xr**3
        + sym1**2 * sym3**2 * xr**2 + sym3**2 * xr**4
        + sym3**2 + sym2**2 * xr**2
    )
    f3 = _sr_mod(f3, irr_e, e)
    eqs_e = [_remove_powers(expand(poly), field_equations)
             for poly in f3.coefficients(sparse=False)]
    eqs_e_str = [" + ".join([str(int(poly.constant_coefficient())),
                             *_magma_terms(poly, e_names)]) for poly in eqs_e]

    variable_names = ",".join(map(str, xc))
    symmetric_names = ",".join(map(str, ec))
    equations = eqs_x_str + eqs_e_str
    formatted_equations = "\n, ".join(equations)
    magma = (
        f'R<{variable_names},{symmetric_names}> := BooleanPolynomialRing({nb_vars}, "grevlex");\n'
        f"B := [ {formatted_equations}];\nI := Ideal(B);\nVariety(I);\n"
    )
    anf = _anf_x(nb_vars_x, nb_vars, n, eqs_x, x_names) + _anf_e(nb_vars_x, eqs_e, e_names)
    metadata = {
        "n": n, "dimension": l, "basis": basis, "offset": offset,
        "target_x": target, "field_modulus": sum(bit << i for i, bit in enumerate(modulus_coefficients)),
        "symmetric_widths": widths, "variables": nb_vars,
        "magma_sha256": hashlib.sha256(magma.encode()).hexdigest(),
        "anf_sha256": hashlib.sha256(anf.encode()).hexdigest(),
    }
    return magma, anf, metadata


def target_from_shipped_magma(path: Path):
    """Recover x(R) from the n target equations' constants, using x -> x^4."""
    match = re.search(r"n(\d+)l(\d+)-\d+-[SU]\.in$", path.name)
    if not match:
        raise ValueError("unexpected shipped benchmark name")
    n, l = (int(value) for value in match.groups())
    body = path.read_text().split("B := [ ", 1)[1].rsplit("];", 1)[0]
    equations = [part.strip() for part in body.split(",")]
    if len(equations) != l + (2 * l - 1) + (3 * l - 2) + n:
        raise ValueError("unexpected shipped equation count")
    x4 = 0
    for i, equation in enumerate(equations[-n:]):
        constant = equation.split(" + ", 1)[0]
        if constant not in {"0", "1"}:
            raise ValueError("target equation lacks a Boolean constant")
        x4 |= int(constant) << i
    field = GF(2**n, name="a")
    return n, l, int((field.from_integer(x4) ** (2 ** (n - 2))).to_integer())


def canonical_anf(content: str, symmetric_count: int):
    """Parse an ANF into parity sets, ignoring the order of printed terms."""
    lines = content.splitlines()
    header = tuple(map(int, lines[0].split()[2:]))
    equations = []
    for equation_index, line in enumerate(lines[1:]):
        tokens = line.split()
        if not tokens or tokens[0] != "x":
            raise ValueError("malformed ANF equation")
        constant = len(tokens) == 1 or tokens[1] != "T"
        position = 2 if not constant else 1
        identifier = None
        if equation_index < symmetric_count:
            identifier = int(tokens[position])
            position += 1
        parity = {(): 1} if constant else {}
        while position < len(tokens) - 1:
            if tokens[position].startswith("."):
                degree = int(tokens[position][1:])
                position += 1
            else:
                degree = 1
            term = tuple(sorted(int(v) for v in tokens[position:position + degree]))
            if len(term) != degree:
                raise ValueError("truncated ANF monomial")
            parity[term] = 1 - parity.get(term, 0)
            position += degree
        if tokens[-1] != "0":
            raise ValueError("ANF equation lacks terminator")
        equations.append((identifier, tuple(sorted(term for term, bit in parity.items() if bit))))
    return header, tuple(equations)


def canonical_magma(content: str):
    """Compare the printed Boolean system independent of whitespace and order."""
    names = tuple(name.strip() for name in content.split("R<", 1)[1].split(">", 1)[0].split(","))
    body = content.split("B := [ ", 1)[1].split("];", 1)[0]
    equations = []
    for equation in body.split(","):
        parity = {}
        for summand in equation.strip().split(" + "):
            if summand.strip() == "0":
                continue
            factors = tuple(sorted(summand.strip().split("*")))
            parity[factors] = 1 - parity.get(factors, 0)
        equations.append(tuple(sorted(term for term, bit in parity.items() if bit)))
    return names, tuple(equations)


def verify_shipped(root: Path):
    rows = []
    for path in sorted(root.glob("n*l*-*-*.in")):
        n, l, target = target_from_shipped_magma(path)
        basis = [1 << j for j in range(l)]
        magma, anf, metadata = build_instance(n, basis, 0, target)
        anf_path = path.with_name("X" + path.stem + ".anf")
        shipped_anf = anf_path.read_bytes()
        shipped_magma = path.read_bytes()
        symmetric_count = sum(metadata["symmetric_widths"])
        rows.append({
            "fixture": path.name,
            "magma_equal": magma.encode() == shipped_magma,
            "magma_semantic_equal": canonical_magma(magma)
            == canonical_magma(shipped_magma.decode()),
            "anf_equal": anf.encode() == shipped_anf,
            "anf_semantic_equal": canonical_anf(anf, symmetric_count)
            == canonical_anf(shipped_anf.decode(), symmetric_count),
            "target_x": target,
            "field_modulus": metadata["field_modulus"],
        })
    if len(rows) != 60:
        raise ValueError(f"expected 60 shipped instances, found {len(rows)}")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int)
    parser.add_argument("--basis", help="comma-separated polynomial-basis integers")
    parser.add_argument("--offset", type=lambda value: int(value, 0), default=0)
    parser.add_argument("--target", type=lambda value: int(value, 0))
    parser.add_argument("--out-prefix", type=Path)
    parser.add_argument("--verify-shipped", type=Path)
    args = parser.parse_args()
    if args.verify_shipped:
        rows = verify_shipped(args.verify_shipped)
        print(json.dumps({"count": len(rows), "magma_equal": sum(r["magma_equal"] for r in rows),
                          "magma_semantic_equal": sum(r["magma_semantic_equal"] for r in rows),
                          "anf_equal": sum(r["anf_equal"] for r in rows),
                          "anf_semantic_equal": sum(r["anf_semantic_equal"] for r in rows),
                          "rows": rows}, indent=2))
        raise SystemExit(0 if all(r["magma_equal"] and r["anf_equal"] for r in rows) else 1)
    if None in (args.n, args.basis, args.target, args.out_prefix):
        parser.error("--n, --basis, --target, and --out-prefix are required")
    basis = [int(value, 0) for value in args.basis.split(",")]
    magma, anf, metadata = build_instance(args.n, basis, args.offset, args.target)
    outputs = [(args.out_prefix.with_suffix(".in"), magma),
               (args.out_prefix.with_suffix(".anf"), anf),
               (args.out_prefix.with_suffix(".json"), json.dumps(metadata, indent=2) + "\n")]
    for path, content in outputs:
        with path.open("x") as stream:
            stream.write(content)
    print(json.dumps(metadata, sort_keys=True))


if __name__ == "__main__":
    main()
