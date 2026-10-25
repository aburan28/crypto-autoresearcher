# Independent recheck of every closed proposition in DkExactBatch4.lean
# (DkCert.Holds / Statement semantics re-implemented from DkExact.lean,
# NistCertificates.lean and Discriminant.lean definitions), plus data
# binding to dk_exact.json and proven primality of the `largePrimes`
# hypothesis via PARI isprime.
# Usage: sage dk_batch4_recheck.sage <repo-root>
import re, json, sys
ROOT = sys.argv[1]
src = open(ROOT + "/formal/CryptoResearch/Endosweep/DkExactBatch4.lean").read()
data = json.load(open(ROOT + "/research/endosweep_dk_exact_batch4_20261022/dk_exact.json"))
jcurves = {c["curve"]: c for c in data["curves"]}

def lean_emod(a, b):  # Int.emod: result in [0, |b|)
    return int(a) % abs(int(b))
def lean_ediv(a, b):
    a = int(a); b = int(b)
    r = lean_emod(a, b)
    return (a - r) // b

blocks = re.findall(r"def (\w+) : DkCert where\n(.*?)\n\n", src, re.S)
out = {}
for name, body in blocks:
    f = {}
    for line in body.strip().split("\n"):
        k, v = line.strip().split(" := ", 1)
        f[k] = v
    c = dict(q=Integer(f["q"]), t=Integer(f["t"]), h=Integer(f["h"]), n=Integer(f["n"]),
             DK=Integer(f["DK"]), fc=Integer(f["f"]), deg=Integer(f["deg"]),
             factors=[(Integer(a), int(b)) for a, b in re.findall(r"\((\d+), (\d+)\)", f["factors"])],
             small=[(Integer(a), Integer(b)) for a, b in re.findall(r"\((\d+), (\d+)\)", f["smallPrimes"])],
             large=[Integer(x) for x in re.findall(r"\d+", f["largePrimes"])],
             s=Integer(f["s"]), L=int(f["L"]))
    r = {}
    r["hn"] = c["q"] + 1 - c["t"] == c["h"] * c["n"]
    r["disc_eq"] = c["t"]^2 - 4*c["q"] == c["DK"] * c["fc"]^2
    prod = 1
    for p, e in c["factors"]:
        prod *= p^e
    r["factor_product"] = 4*c["q"] - c["t"]^2 == prod
    odd = [p for p, e in c["factors"] if e % 2 == 1]
    oddPrimes = [p for p, _ in c["small"]] + c["large"]
    r["oddPrimes_eq_filter"] = odd == oddPrimes
    r["nodup"] = len(set(oddPrimes)) == len(oddPrimes)
    P = prod_list = 1
    for p in oddPrimes:
        P *= p
    r["s_eq_prod"] = P == c["s"]
    case1 = c["DK"] == -c["s"] and lean_emod(c["DK"], 4) == 1
    case2 = c["DK"] == -4*c["s"] and lean_emod(-c["s"], 4) in (2, 3)
    r["DK_construction"] = bool(case1 or case2)
    r["DK_case"] = "-s" if case1 else ("-4s" if case2 else None)
    r["IsDisc"] = c["DK"] < 0 and lean_emod(c["DK"], 4) in (0, 1)
    mnd = lean_ediv(abs(c["DK"]) + lean_emod(c["DK"], 2), 4)
    r["minNonscalarDegree_eq_deg"] = mnd == c["deg"]
    r["L_bounds"] = 2^c["L"] <= abs(c["DK"]) < 2^(c["L"] + 1)
    r["deg_ge_2^(L-2)"] = 2^(max(c["L"] - 2, 0)) <= c["deg"]
    r["small_trial_witness"] = all(2 <= p and p < b*b and all(p % d != 0 for d in range(2, b)) for p, b in c["small"])
    r["small_below_1e8"] = all(p < 10^8 for p, _ in c["small"])
    r["large_above_1e8"] = all(p >= 10^8 for p in c["large"])
    r["large_primes_proven_prime_pari"] = all(bool(pari(p).isprime()) for p in c["large"])
    r["all_factors_prime"] = all(bool(pari(p).isprime()) for p, _ in c["factors"])
    # fundamental discriminant check from the PROVED factorisation (no factoring):
    # s = product of distinct proven primes => s squarefree; then textbook rule
    D = c["DK"]
    s_sqfree = r["nodup"] and r["s_eq_prod"] and r["all_factors_prime"]
    if D % 4 == 1:
        fund = s_sqfree and D == -c["s"]
    else:
        m = D // 4
        fund = (D % 4 == 0) and (m % 4 in (2, 3)) and s_sqfree and m == -c["s"]
    r["DK_fundamental_textbook_from_factorisation"] = bool(fund)
    # t^2-4q = D f^2 with D fundamental => D is THE fundamental discriminant of the square class
    r["fundamental_disc_of_square_class"] = bool(fund) and (c["t"]^2 - 4*c["q"]) == D*c["fc"]^2
    r["exact_discriminants_bounds"] = (2^385 <= abs(D)) and (2^383 <= c["deg"])
    # data binding vs dk_exact.json
    j = None
    for key, jc in jcurves.items():
        if key.replace("/", "_").replace("-", "_") == name:
            j = jc
    if j is None:
        r["json"] = "NOT FOUND"
    else:
        r["json_match"] = all([
            Integer(j["p"]) == c["q"], Integer(j["t"]) == c["t"], Integer(j["h"]) == c["h"],
            Integer(j["n"]) == c["n"], Integer(j["D_K"]) == D, Integer(j["conductor_f"]) == c["fc"],
            Integer(j["min_nonscalar_degree"]) == c["deg"], Integer(j["squarefree_part"]) == c["s"],
            [(Integer(a), int(b)) for a, b in eval(j["factorization"]) if True] == c["factors"]
            if isinstance(j["factorization"], str) else
            [(Integer(a), int(b)) for a, b in j["factorization"]] == c["factors"]])
        r["json_curve"] = j["curve"]
    r["p_is_bpsw_probable_prime"] = bool(c["q"].is_pseudoprime())
    r["n_is_bpsw_probable_prime"] = bool(c["n"].is_pseudoprime())
    r["hasse"] = abs(c["t"]) <= 2*sqrt(RealField(2000)(c["q"]))
    out[name] = r
# known prime formulas (only those I am confident of)
known = {"nums_numsp384d1": 2^384 - 317, "other_Curve41417": 2^414 - 17,
         "other_M_511": 2^511 - 187, "other_E_521": 2^521 - 1, "nums_numsp512d1": 2^512 - 569}
for nm, pv in known.items():
    m = re.search(r"def " + nm + r" : DkCert where\n  q := (\d+)", src)
    out[nm]["p_matches_published_formula"] = Integer(m.group(1)) == pv
out["_count"] = len(blocks)
out["_dkCerts_list"] = re.search(r"def dkCerts : List DkCert :=\s*\[(.*?)\]", src, re.S).group(1).split()
print(json.dumps(out, indent=1, default=str))
