# Independent validator recomputation for EXP-MLKEM-12d9b8 / RUN-MLKEM-12d9b8-001
# Written from scratch by the Validator, WITHOUT reading or copying compute.py's
# code body. Uses only the formulas stated in specification.yaml (base contract)
# and amendments/v1.yaml (MLKEM-CHG-1/2).
#
# Formula (spec preregistered_prediction.formula, and amendment MLKEM-CHG-1/2):
#   n := k_mlkem * 256
#   Q  = k_mlkem * n^(c+1)
#   combinatorial_ceiling(B) = (2*B + 1) ** k_mlkem      [upper bound, B<=q per amendment]

LEVELS = {
    "ML-KEM-512":  {"k_mlkem": 2, "q": 3329},
    "ML-KEM-768":  {"k_mlkem": 3, "q": 3329},
    "ML-KEM-1024": {"k_mlkem": 4, "q": 3329},
}
C_SWEEP = [12, 13, 15, 20]

def Q(k_mlkem, c):
    n = k_mlkem * 256
    return k_mlkem * (n ** (c + 1))

def ceiling(B, k_mlkem):
    return (2 * B + 1) ** k_mlkem

print("=== independent Q table ===")
Q_table = {}
for level, p in LEVELS.items():
    k = p["k_mlkem"]
    for c in C_SWEEP:
        val = Q(k, c)
        Q_table[(level, c)] = val
        print(level, c, val)

print()
print("=== independent combinatorial ceiling table (B=1, B=q) ===")
ceil_table = {}
for level, p in LEVELS.items():
    k = p["k_mlkem"]
    q = p["q"]
    c1 = ceiling(1, k)
    cq = ceiling(q, k)
    ceil_table[(level, 1)] = c1
    ceil_table[(level, q)] = cq
    print(level, "B=1:", c1, "B=q:", cq)

print()
print("=== independent verdicts (UNREALIZABLE iff ceiling(B=q) < Q) ===")
all_unrealizable = True
for level, p in LEVELS.items():
    k = p["k_mlkem"]
    q = p["q"]
    cq = ceil_table[(level, q)]
    for c in C_SWEEP:
        qv = Q_table[(level, c)]
        verdict = "REALIZABLE" if cq >= qv else "UNREALIZABLE"
        shortfall_digits = len(str(qv)) - len(str(cq))
        if verdict != "UNREALIZABLE":
            all_unrealizable = False
        print(level, "c=", c, "Q=", qv, "ceiling(Bq)=", cq, "->", verdict,
              "digit-shortfall approx:", shortfall_digits)

print()
print("ALL UNREALIZABLE:", all_unrealizable)

# Specific checks requested by the task
print()
print("=== SPOT CHECKS REQUESTED ===")
for level, c in [("ML-KEM-512", 12), ("ML-KEM-512", 20), ("ML-KEM-1024", 12), ("ML-KEM-1024", 20)]:
    k = LEVELS[level]["k_mlkem"]
    n = k * 256
    q_val = Q(k, c)
    print(f"{level} c={c}: n={n}, k_mlkem={k}, Q = k_mlkem*n^(c+1) = {q_val}")

for level, B in [("ML-KEM-512", 1), ("ML-KEM-512", 3329), ("ML-KEM-1024", 1), ("ML-KEM-1024", 3329)]:
    k = LEVELS[level]["k_mlkem"]
    print(f"{level} B={B}: ceiling=(2B+1)^k_mlkem = {ceiling(B,k)}")

# amendment's disclosed figures
print()
print("=== amendment disclosed figures cross-check ===")
q512_12 = Q(2, 12)
print("ML-KEM-512 c=12: Q =", q512_12, " (amendment says ~3x10^35, i.e. 2*512^13 = 2*2^117)")
print("2*2^117 =", 2*2**117, " equal to n^13*2?", 512**13*2 == q512_12)
ceil_1024_q = ceiling(3329, 4)
print("ML-KEM-1024 ceiling at B=q=3329:", ceil_1024_q, " (amendment says ~2x10^15; run claims 1966237884282961)")
