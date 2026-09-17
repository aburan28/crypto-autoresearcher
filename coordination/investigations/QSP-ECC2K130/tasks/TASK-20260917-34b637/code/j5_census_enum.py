"""J5(a),(b),(d): re-enumerate the n = 131 census candidate set FROM THE
DEFINITION, and confirm the histograms FROM THE ROWS.

Definition (specification.yaml stage_3.candidates): EVERY non-linearized lambda
in F_2[X] of exact degree 3..7; affine lambda included and marked; linearized
lambda excluded.  A linearized polynomial over F_2 is one all of whose monomials
have exponent a power of 2 (X^{2^i}).

Nothing here reads the producer's implementation; it reads only the archived
per-cell JSON rows and rebuilds the declared set independently.
"""
import json, collections

def is_pow2(k):  return k > 0 and (k & (k - 1)) == 0

def exponents(bits):
    return [i for i in range(bits.bit_length()) if (bits >> i) & 1]

def linearized(bits):
    """all monomials have exponent a power of 2 (X^{2^i}); X = X^{2^0} counts,
    the constant term X^0 = 1 does NOT (0 is not a power of 2)."""
    return all(is_pow2(e) or e == 1 for e in exponents(bits)) and 0 not in exponents(bits)

def affine(bits):
    """linearized part plus a constant"""
    e = [x for x in exponents(bits) if x != 0]
    return bool(e) and all(is_pow2(x) or x == 1 for x in e)

# --- build the declared set from the definition -------------------------------
all_exact = {}
for d in range(3, 8):
    all_exact[d] = [b for b in range(1 << d, 1 << (d + 1))]   # exact degree d
tot_exact = sum(len(v) for v in all_exact.values())
lin = [b for d in all_exact for b in all_exact[d] if linearized(b)]
declared = sorted(b for d in all_exact for b in all_exact[d] if not linearized(b))
print("sum_{d=3..7} 2^d (lambda of exact degree d over F_2) :", tot_exact,
      "=", " + ".join(str(len(all_exact[d])) for d in range(3, 8)))
print("linearized of exact degree 3..7                      :", len(lin), "->",
      [(b, [e for e in exponents(b)]) for b in lin])
print("declared census size per cell                        :", len(declared))
print()

CELLS = {33: "n131_np33.json", 44: "n131_np44.json", 66: "n131_np66.json"}
for npr, fn in CELLS.items():
    c = json.load(open(f"experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S3/cells/{fn}"))
    rows = c["rows"]
    bits = [r["lambda_bits"] for r in rows]
    print(f"--- cell n' = {npr} ---")
    print("  rows in file                      :", len(rows), " (declared 'candidates' field:", c["candidates"], ")")
    print("  duplicates                        :", len(bits) - len(set(bits)))
    print("  set equals the declared set       :", sorted(bits) == declared)
    missing = sorted(set(declared) - set(bits)); extra = sorted(set(bits) - set(declared))
    print("  missing from file                 :", missing)
    print("  present but not declared          :", extra)
    print("  any linearized present            :", [b for b in bits if linearized(b)])
    print("  every bit pattern in [2^3, 2^8)   :", all(8 <= b < 256 for b in bits))
    # exact-degree bookkeeping
    degs = collections.Counter(b.bit_length() - 1 for b in bits)
    print("  per exact degree                  :", dict(sorted(degs.items())))
    print("  row 'd' field matches bit degree  :", all(r["d"] == r["lambda_bits"].bit_length() - 1 for r in rows))
    # J5(b): histogram rebuilt FROM THE ROWS
    hist = collections.Counter(r["N"] for r in rows)
    arch = {int(k): v for k, v in c["N_histogram"].items()}
    print("  histogram recomputed from rows    :", dict(sorted(hist.items())))
    print("  archived N_histogram              :", dict(sorted(arch.items())))
    print("  agree                             :", dict(hist) == arch, "| sums to", sum(hist.values()))
    print("  max N from rows / archived        :", max(hist), "/", c["max_N"])
    # J5(d): affine marking
    mism = [(r["lambda_bits"], r["affine"], affine(r["lambda_bits"])) for r in rows
            if r["affine"] != affine(r["lambda_bits"])]
    naff = sum(1 for r in rows if r["affine"])
    print("  rows marked affine                :", naff,
          "->", sorted(r["lambda_printed"] for r in rows if r["affine"]))
    print("  affine-marking mismatches vs defn :", len(mism), mism[:5])
    # bound / ratio consistency, recomputed
    q, r_ = divmod(131, npr)
    bad = [r["lambda_bits"] for r in rows
           if r["bound"] != max(r["d"] ** (q + 1), 2 ** (npr - r_)) or r["q"] != q or r["r"] != r_]
    print("  rows whose bound/q/r disagree     :", len(bad))
    over = [r for r in rows if r["N"] > r["bound"]]
    print("  rows with N > bound               :", len(over))
    print("  rows with N > 0 (certificates)    :", sum(1 for r in rows if r["N"] > 0),
          "| archived 'certificates':", c["certificates"])
    print("  rows with degenerate_D_zero True  :", sum(1 for r in rows if r["degenerate_D_zero"]))
    print()
