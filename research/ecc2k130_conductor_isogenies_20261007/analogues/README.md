# Analogues: conductor-changing isogenies on Koblitz curves similar to ECC2K-130

**Question.** Does the ECC2K-130 picture repeat on Koblitz curves with similar
traits, in particular m = 83?

The ECC2K-130 picture is: a few conductor-changing prime degrees, one of them
cheap to compute, the others out of reach. "Similar traits" here means: prime
extension degree m; Koblitz form y² + xy = x³ + a x² + 1; near-prime order
(cofactor 2 or 4); End = O_K with K = Q(√−7) and h = 1.

## How cheap a conductor isogeny is (derived)

For each prime ℓ′ | f_π = [O_K : Z[π]], Frobenius acts on E[ℓ′] as an integer
c. The kernel x-coordinates of the ℓ′-isogenies live in F_2^(m·k), where k is
the least integer with c^k = ±1. They lie on E if c^k = 1 and on its quadratic
twist if c^k = −1. So k is the cost driver: arithmetic happens in an
(m·k)-bit field.

ECC2K-130's 263 is the extreme case, k = 1 (c = −1): no extension field at
all.

## Survey, m = 53 to 173, cofactor ≤ 4 (`survey.gp` → `survey.out`)

| curve | conductor primes, with k and kernel-field size | verdict |
|---|---|---|
| m = 83, a = 0, cofactor 4 | 6473 (k = 3236, F_2^268588); 53676929 (k = 6.7·10⁶) | kernel route: **not computable here** (below); the 6473-floor was later computed by the CM route ([`../EXTENSIONS.md`](../EXTENSIONS.md)) |
| m = 97, a = 0, cofactor 4 | 751943 (F_2^3.6e7); 352124743 | no |
| m = 101, a = 1, cofactor 2 | 5857 (F_2^295728); 18583 (F_2^312797); 3996569 | kernel route: no; 5857- and 18583-floors by the CM route ([`../EXTENSIONS.md`](../EXTENSIONS.md)) |
| m = 103, a = 0, cofactor 4 | **11329 (k = 472, F_2^48616)**; 188642399417 | kernel route feasible but heavy (not run); 11329-floor computed by the CM route ([`../EXTENSIONS.md`](../EXTENSIONS.md)) |
| m = 107, a = 0 or 1 | 3209 (F_2^171628); 1703265694433 | kernel route: no; 3209-floor by the CM route ([`../EXTENSIONS.md`](../EXTENSIONS.md)) |
| **m = 109, a = 1, cofactor 2** | **3271 (k = 5, F_2^545)**; 699600307831 | **computed** |
| m = 113, a = 1, cofactor 2 | 77031318395801969 (F_2^4.4e18) | no |
| **m = 131, a = 0, cofactor 4 (ECC2K-130)** | **263 (k = 1, F_2^131)**; 146505763881528721 | computed (main study) |
| **m = 163, a = 1, cofactor 2 (NIST K-163)** | **45641 (k = 20, F_2^3260)**, **82153 (k = 63, F_2^10269)**; 8610311; 56498081 | **both computed** |

*Derived.* (Kronecker symbols, k values and class numbers are in `survey.out`
and `details.out`.)

## m = 83: why the kernel route can't do it here

*Update 2026-10-08:* everything below is about the kernel route and still holds. The CM route, which reads the
floor off a class polynomial mod 2, computes the whole 6473-floor in under a minute; see
[`../EXTENSIONS.md`](../EXTENSIONS.md).

- **Cheapest prime.** Its cheapest conductor prime is 6473 (inert, so all 6474
  isogenies from the crater descend). The kernel x-coordinates need
  F_2^(83·3236) = F_2^268588. *Derived.*
- **The field can't be built.** PARI/GP 2.15 cannot construct that field on
  this machine: `ffinit(2, 268588)` overflows a 4 GB stack. *Measured.*
- **Cost if it could.** Scaling from the measured K-163 runs (about 15 min per
  isogeny in a 10269-bit field), with ladder cost ∝ n^2.58, one 6473-isogeny
  would take about 7 weeks of CPU on this machine. *Extrapolated, not
  measured.*
- **The other prime is worse.** 53676929 needs a field of 5.6·10⁸ bits.
  *Derived.*

So m = 83 does not have ECC2K-130's lucky small-k prime. Its conductor
isogenies exist but are out of practical reach with these tools.

## Computed analogues (`vert_gen.gp`, `cyc_gen.gp`)

Method as in the main study: x-only López–Dahab ladders in F_2^(m·k), on the
twist in all three cases here; char-2 Vélu b′ = 1/j′ = 1 + v + v², valid for
any a₂ with a₁ = 1, a₃ = a₄ = 0, a₆ = 1; Δ′ pulled down to F_2^m through its
F_2-minimal polynomial; `ellcard` check; and an independent level check by
horizontal-isogeny cycle length.

| curve, degree ℓ′ | isogenies computed | time each | distinct Galois orbits reached | #E′ = N | level check (cycle length; crater = 1) |
|---|---|---|---|---|---|
| m = 109 (a = 1), **3271** | 6 | < 1 s | 6 of 30 | 6/6 | 23-cycle **545** = ord[𝔩₂₃] in Cl(−7·3271²), 6/6 |
| K-163, **45641** | 6 | ≈ 1 min | 6 of 280 | 6/6 | 11-cycle **9128** = ord[𝔩₁₁] in Cl(−7·45641²), 6/6 |
| K-163, **82153** | 6 | ≈ 15 min | 6 of 504 | 6/6 | 11-cycle **10269** = ord[𝔩₁₁] in Cl(−7·82153²), 6/6 |

*Measured; level checks independently verified.* Every image has the model
y² + xy = x³ + x² + b′ (a₂ = 1, the same as the crater). The representatives
(the minimum b′ of each Galois orbit, in the bases below) are in
`iso109_3271.txt`, `iso163_45641.txt` and `iso163_82153.txt`.

**Field bases:**
- m = 109: F_2[x]/(x¹⁰⁹ + x⁹ + x² + x + 1).
- K-163: the NIST pentanomial x¹⁶³ + x⁷ + x⁶ + x³ + 1.

**Why K-163 stands out.** It has two independently computable conductor
primes, so both its 45641-floor and its 82153-floor are reachable explicitly.
From a 45641-floor curve, an 82153-isogeny would reach the next level down,
conductor 45641·82153 ≈ 3.7·10⁹, with the same k = 63. That step needs the
floor curve's b′ embedded in the big field, which the b = 1 shortcut used
here avoids. *Proposed, not run here;* run on 2026-10-08, see [`../EXTENSIONS.md`](../EXTENSIONS.md) §3.

## Scope

These are structural isogeny computations; no rho was run on these curves.
The ECDLP consequence follows the main study: every curve below the crater
has no Frobenius endomorphism, and by the m = 37 and m = 41 measurements, rho
there runs with negation only, needing about √m times more steps.
*Extrapolated.*
