# P-256 Isogeny Class: CM/Volcano Structure and Invariant-Based Resistance

Date: 2026-06-01. Branch: main (research/ecdlp-cryptanalysis-resistance-map lineage).
Owner: Theory Agent + Algebra System Agent + Benchmark Agent (synthesis).
Connects to: ledger **H10 (CM-Isogeny-Volcano Lift)**; **NR-007** (small-l isogeny walks); proof
obligation **PO-004 / NR-022** (Semaev per-variable degree is isogeny-invariant).
Reproduction: `experiments/ecdlp_prime_field/round017_p256_cm_volcano.gp` (+ `.log`),
`experiments/ecdlp_prime_field/round017_glv_scan.py`.

External trigger: **Galbraith, "Climbing and Descending Tall Volcanos"** (2024, submitted to ANTS;
the paper PDF is in this repo as `document_pdf.pdf` and has now been read directly). It improves
the worst-case ordinary-curve isogeny-finding bound from ~Õ(q^{3/2}) (Galbraith 1999) to
heuristically **Õ(q^{2/5})**, using the **Kani construction + √Vélu + meet-in-the-middle** (Robert's
efficient large-degree-isogeny representation) to represent a degree-N isogeny in ~Õ(N^{1/2}).
**Exponent attribution, verified from the paper (abstract; §7; resolves the prior `literature_matrix.md`
row-82 mix-up):** the **flat-volcano case (= P-256, conductor f=1) gets a RIGOROUS Õ(q^{1/4})**
algorithm — this was already in Galbraith 1999 for the average/flat case and is the cost of a
class-group BSGS over the crater (√h₀≈q^{1/4}); the heuristic Õ(q^{2/5}) is the *worst case*, a
large-prime conductor gap. So for P-256 the isogeny bridge costs ≈ 2^64, not 2^102. The paper's
motivation: an isogeny transfers ECDLP instances between same-order curves (§10–§11 revisit
Jao–Miller–Venkatesan 2005 and Koblitz–Koblitz–Menezes 2011).

Claim-label discipline (AGENTS.md / CLAUDE.md): every numbered claim carries exactly one of
THEOREM | RESTRICTED THEOREM | HEURISTIC | CONJECTURE | HYPOTHESIS | OBSERVATION | NEGATIVE RESULT | OPEN.
Nothing here says "impossible"; each conservation statement is paired with the exact place a
sub-rho attack would still have to live (§7).

---

## 0. One-paragraph executive summary

The "NSA chose public curve A = P-256, secretly knows an isogenous weak curve B" trapdoor theory
has a precise, testable shape: there must exist a curve **B**, F_p-isogenous to P-256, with an
ECDLP weakness such that `cost(find isogeny A→B) + cost(solve DLP on B) < 2^128` (rho). We
(i) computed P-256's CM structure exactly — **D = t²−4p is a fundamental discriminant
(conductor f = 1), so the isogeny volcano is FLAT at every prime, and every curve in the class has
the maximal endomorphism ring O_K of discriminant ≈ −2^258** (the class is a single Cl(O_K)-torsor
of size h ≈ 2^127 — HEURISTIC, assumes L(1,χ_D)=O(1)); and (ii) proved that the named
special-curve weaknesses are **isogeny-class invariants**: group order n, ordinariness, the
anomalous condition (#E = p), the embedding degree k = ord_n(p) = (n−1)/3 ≈ 2^254, and the
fundamental discriminant D_0 are all identical for every curve in the class and all strong for
P-256. Combined with the prior result that the **Semaev per-variable degree is isogeny-invariant**
(PO-004 / NR-022 — invariance of the solving *degree*, not proven cost-invariance; see §4), this
means **no curve in P-256's isogeny class is more vulnerable than P-256 itself to any of the NAMED
attacks — MOV/Frey–Rück, Smart-anomalous, supersingular, GLV/GLS, or Semaev-degree-reduction**
(THEOREM for the first four; RESTRICTED THEOREM, model M, for the last). The key
conceptual payoff: this **overturns the *cost-barrier* sub-argument of NR-007** (which dismissed
isogeny attacks because "walking to a special curve costs ≫ √n"; NR-007's separate
degree-invariance finding is untouched and is reused in §4) — Galbraith-2024 makes the bridge
*cheap* (for P-256's flat volcano, a rigorous Õ(q^{1/4}) ≈ 2^64) — and **relocates the obstruction
to a stronger, structural fact: no curve in the class is weak via any named attack family.** The
trapdoor theory fails not because the isogeny is hard to find, but because the (named-)weak target
it needs does not exist. *(Scope: whether a curve in the class is weak via a NON-class-invariant,
coefficient-dependent algebraic structure outside model M is OPEN — §7, O-1 — and is the one place
this conclusion does not reach. "Isogenous" = F_p-isogenous = same order; the quadratic twist
(order p+1+t ≠ n) is a different class and out of scope.)*

---

## 1. Parameters and the CM discriminant (verified computation)

P-256 / secp256r1 / NIST SP 800-186, prime field F_p, prime group order n, cofactor 1:

```
p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
```

Frobenius trace `t = p + 1 − n = 89188191154553853111372247798585809583` (127 bits;
|t| ≤ 2√p, Hasse OK). The CM discriminant of the Frobenius order Z[π] is

```
D = t² − 4p = −455213823400003756884736869668539463648899917731097708475249543966132856781915
```

(258-bit, D ≡ 1 mod 4). **Full factorization (verified: all five factors prime, distinct,
product = |D|, PARI `issquarefree` = true):**

```
|D| = 3 · 5 · 456597257999 · 1428624589419343516204097
        · 46523541035814968339936406074986559003387
```

**Claim 1.1 (P-256 CM discriminant is fundamental; conductor f = 1).** **THEOREM** (deterministic
computation). D is squarefree and D ≡ 1 (mod 4), hence D is a fundamental discriminant. Therefore
the conductor of Z[π] in the maximal order O_K of K = Q(√D) is f = 1, i.e. **Z[π] = O_K**, and the
fundamental discriminant is D_0 = D, with |D_0| ≈ 2^257.7.

*Method validation (positive control, in the script):* the same `coredisc`/√(D/D_0) extraction
recovers f = 2 for D = −28 (D_0 = −7), f = 10 for D = −300 (D_0 = −3), and f = 1 for D = −23. The
conductor extraction is exact integer arithmetic, not a heuristic.

**Claim 1.2 (flat volcano at every prime).** **THEOREM.** For each prime ℓ, the height of the
ℓ-isogeny volcano of P-256 equals **v_ℓ(f)** (Kohel; the conductor's ℓ-adic valuation — *not*
⌊v_ℓ(D)/2⌋ in general, which fails at ℓ=2). Since f = 1 (Claim 1.1), v_ℓ(f) = 0 for every ℓ with
no per-prime computation needed: the conductor being 1 settles flatness directly. **P-256 sits on the crater of
every ℓ-volcano; all F_p-isogenies are horizontal.** There is no vertical descent to a "lower"
curve with a smaller endomorphism ring, because no proper sub-order of O_K contains Z[π] (f = 1).

> Robust sub-claim even without the full factorization: `factor(|D|,10^7)` shows the only primes
> ≤ 10^7 dividing D are 3 and 5, each to multiplicity 1. So **for every prime ℓ ≤ 10^7,
> v_ℓ(D) ≤ 1 ⇒ ℓ-volcano height 0** — i.e. all *cheap* (small-degree) isogenies are horizontal —
> independent of whether the 216-bit cofactor were squarefree. The squarefree-cofactor result
> (verified) extends flatness to *all* ℓ.

---

## 2. The same-order curve set is a single CL(O_K)-torsor of size ≈ 2^127

**Claim 2.1 (structure of the isogeny class).** **THEOREM** (Deuring correspondence; uses f = 1).
The set of elliptic curves over F_p with exactly n points (equivalently, Frobenius trace +t) is,
up to F_p-isomorphism, a torsor under the ideal class group **Cl(O_K)**. Because f = 1, every such
curve has End = O_K; there are no other endomorphism-ring types in the class. The class is
connected by horizontal F_p-isogenies (the class-group action), forming the crater.

**Claim 2.2 (crater size).** **HEURISTIC** (Dirichlet analytic class number formula; L(1,χ) not
computed exactly — exact h for |D| ≈ 2^258 needs a subexponential class-group computation under
GRH, which we did not run). `h(D) ≈ (√|D|/π)·L(1,χ_D)` with L(1,χ) = O(1), giving
`h ≈ √|D|/π ≈ 2^127`. So the isogeny class contains ≈ 2^127 curves.

**Consequence (for the trapdoor search).** **HEURISTIC.** Even a brute-force "search the isogeny
class for a lucky weak curve" is a ≈ 2^127 task — the same order as Pollard rho
(0.886·√n ≈ 2^128). The class is too large to enumerate below rho cost. (This is an *independent*
reason the search-version of the trapdoor fails, on top of the structural results in §3–§5.)

---

## 3. Isogeny-class invariants that kill the "classical weak B" theories (THEOREMs)

Let B be **any** elliptic curve F_p-isogenous to P-256. The following are identical for B and
P-256 because each is a function of class-invariant data only.

**Claim 3.1 (group order).** **THEOREM** (Tate). #B(F_p) = #E_{P256}(F_p) = n, prime. No curve in
the class has a composite or smooth order; Pohlig–Hellman gains nothing anywhere in the class.

**Claim 3.2 (ordinary, not supersingular).** **THEOREM.** Supersingularity (E supersingular ⇔
p | t) is an isogeny invariant; the trace t is constant on the F_p-isogeny class. P-256 has
p ∤ t (t ≈ 2^127), so **every** curve in the class is ordinary. No supersingular MOV-degree-≤6
collapse exists anywhere in the class.

**Claim 3.3 (no anomalous curve in the class).** **THEOREM.** The Smart / Satoh–Araki / Semaev
"anomalous" attack (additive/SmartASS, polynomial-time) applies iff #E = p. Since #B = n for all
B in the class and n ≠ p (verified), **no curve in the class is anomalous.** #E is a class
invariant, so this is invariant.

**Claim 3.4 (embedding degree is a class invariant and is huge).** **THEOREM.** For the prime-order
group, the embedding degree is k = ord_n(p) (smallest k with n | p^k − 1), a function of (n, p)
only — both shared across the class. Computed exactly:

```
k = ord_n(p) = 38597363070118749587565815649802524509998985074711920114140753020356170681456
             = (n−1)/3  ≈ 2^254.
```

The MOV/Frey–Rück target field F_{p^k} has ≈ k·256 ≈ 2^262 bits — astronomically infeasible. **No
curve in the class has a small-embedding-degree pairing weakness.**

**Claim 3.5 (no GLV/GLS endomorphism anywhere in the class).** **THEOREM.** Every B in the class
has End(B) = O_K (Claim 1.1, f = 1), of discriminant D_0 = D, |D_0| ≈ 2^258. A GLV/GLS speedup
needs a non-scalar endomorphism ψ computable by *low-degree* rational maps; deg(ψ) = N_{K/Q}(ψ),
and the minimal norm of a non-scalar ψ ∈ O_K is ≈ |D_0|/4 ≈ 2^256. A degree-2^256 isogeny is not
efficiently computable. Hence **no curve in the class admits a GLV/GLS decomposition** beyond the
order-2 negation map [x,y]↦[x,−y] (already in the rho baseline as the √2 negation-map factor). In
particular no curve in the class has j = 0 or j = 1728 (those need D_0 ∈ {−3,−4}).

> *Rigorous, factoring-free corroboration of 3.5:* `round017_glv_scan.py` scans every candidate
> fundamental discriminant |D_0| ≤ 10^8 and finds none with D/D_0 a perfect square ⇒ **|D_0| > 10^8
> unconditionally** ⇒ minimal endomorphism degree > 2.5·10^7 ⇒ no efficient endomorphism. (Real
> GLV curves have |D_0| ≤ ~10^3.) This step needs no factorization of D.

---

## 4. The remaining door — algebraic/Semaev structure — is also shut in model M

The only weakness that is *not* obviously a class invariant is "curve B has a cheaper
index-calculus / Semaev / descent representation." Prior campaign work addressed exactly this:

**Claim 4.1 (Semaev per-variable degree does not drop across the class).** **RESTRICTED THEOREM**
(model M). Two distinct prior results bear here, and it is important not to overstate either:
 - **PO-004 (THEOREM, but for Weil restriction, not isogeny):** the per-variable degree of the
   Semaev polynomial is invariant under *scalar Weil restriction* (2^{m−2} for m ≥ 3). This is a
   degree statement, and PO-004 §"boundary" explicitly **does not** claim end-to-end cost-invariance
   (in the one realization actually measured, scalar Weil, D_reg went 9→11, i.e. *worse*).
 - **NR-007 (NEGATIVE RESULT, empirical):** small-ℓ isogeny walks produced no curve with lower GB
   degree / Newton polytope; the degree-3 addition law is isogeny-invariant. This is empirical
   (prior-campaign toy scale), not a proof, and it is about *isogeny* (the relevant map here).
So the bankable statement is: **the per-variable Semaev solving *degree* does not decrease across
the class** (RESTRICTED THEOREM, model M). What is **NOT** proven is end-to-end IC *cost*-invariance,
and what is **not** even addressed by these results is a *coefficient-level* structure (the (a,b) of
a specific curve, which varies across the Cl(O_K)-torsor) triggering an exploitable early fall — see
§7 O-1. (Model M = naive Gröbner/F4–F5 index calculus; PO-004 §0 fixes the precise model boundary.)

Together with §3, this means: **every named ECDLP weakness — Pohlig–Hellman, supersingular MOV,
small-embedding-degree MOV/Frey–Rück, Smart-anomalous, GLV/GLS, and Semaev-degree reduction — is
either a class invariant (THEOREM) or invariant in model M (RESTRICTED THEOREM), and all are
strong for P-256.**

---

## 5. Main result: the trapdoor theory fails for a *structural* reason, not a cost reason

**Claim 5.1 (P-256 isogeny-class resistance).**
**RESTRICTED THEOREM** (clauses (i)–(iv): unconditional THEOREM; clause (v): model M).
Let B be any elliptic curve F_p-isogenous to P-256. Then:
(i)   #B(F_p) = n (prime);
(ii)  B is ordinary and non-anomalous;
(iii) B has embedding degree k = (n−1)/3 ≈ 2^254;
(iv)  End(B) = O_K with disc ≈ −2^258 (no GLV/GLS);
(v)   B has the same per-variable Semaev solving *degree* as P-256 (RESTRICTED THEOREM, model M;
      this bounds the degree exponent under semi-regularity — it is **not** a proof of end-to-end
      IC cost-invariance, and does **not** cover a coefficient-level early-fall, §7 O-1).
Therefore **B is immune to MOV/Frey–Rück, Smart-anomalous, supersingular, GLV/GLS, and
Semaev-degree-reduction attacks to exactly the same extent as P-256 itself.** A hidden isogenous
curve weak via **any of these named methods** does not exist. (This is scoped to the named families;
a weakness via a non-class-invariant, coefficient-dependent structure outside model M is OPEN, §7.)

**Claim 5.2 (reframing NR-007 via Galbraith-2024 — the conceptual contribution).**
**OBSERVATION + RESTRICTED THEOREM.**
NR-007's *cost-barrier sub-argument* dismissed isogeny-to-weak-curve attacks on the grounds that
*reaching* a special curve costs walk-length ≫ √n, already exceeding rho. **Galbraith-2024 refutes
that cost premise** (its degree-invariance core, reused in §4, is untouched). Verified from the
paper itself (`document_pdf.pdf`, abstract + §7): for P-256's **flat volcano (f=1), isogeny finding
is a RIGOROUS Õ(q^{1/4}) ≈ 2^64** — the cost of a class-group BSGS over the crater (√h₀ ≈ |D|^{1/4}),
present already in Galbraith 1999 for the flat/average case. (The heuristic Õ(q^{2/5}) ≈ 2^102 is
the *worst case*, a large-prime conductor gap — not P-256. The earlier `literature_matrix.md` row 82
had this backwards; corrected.) Either way the bridge is *not* the obstruction. Yet the attack still fails, now for the
stronger reason of Claim 5.1: **there is no destination B weak via a named attack.** The obstruction
moves from "the bridge is too expensive" (false for P-256) to "the far bank has no
named-weak curve on it" (THEOREM for the named weaknesses; the non-class-invariant
coefficient-level door, O-1, remains open). This is strictly stronger where it applies and removes
NR-007's reliance on a cost barrier that Galbraith has dismantled.

**Why MOV/anomalous/supersingular were "obviously" ruled out but now rigorously so.** The
correspondent's intuition ("same-order invariants share obvious weaknesses") is upgraded here to
explicit invariance proofs (3.1–3.4) plus the embedding-degree computation, so the ruling-out is
no longer an intuition but a checked theorem with the exact invariant identified for each attack.

---

## 6. Experiment contract + result (for the record)

```markdown
# Experiment Contract: P-256 CM/volcano structure and isogeny-class invariants
## Hypothesis
P-256's isogeny class contains a curve B with an ECDLP weakness exploitable, via a (possibly
cheap, Galbraith-2024) isogeny bridge, below rho 2^128.
## Null hypothesis
Every classical ECDLP weakness is a class invariant strong for P-256; the volcano is flat so no
"special floor curve" exists; hence no such B.
## Parameters
P-256 (fixed). D = t²−4p. ℓ-volcano height = v_ℓ(f). Class invariants n, t, ord_n(p), D_0.
## Metrics
conductor f; per-prime volcano height; embedding degree k; |D_0| lower bound; crater size h(D).
## Positive control
D=−28 (f=2), D=−300 (f=10), D=−23 (f=1): method recovers known conductors. (PASS.)
## Negative control (EXECUTED — `round017_glv_scan.log`)
The GLV scan must return a hit for a curve with small CM disc. Run with `--D`: D=−30000=−3·100²
returns D_0=−3, and D=−343=−7·7² returns D_0=−7 — the control fires. The same code on P-256 returns
[] up to the scanned bound ⇒ |D_0| exceeds it. (Both directions now executed, not merely asserted.)
## Success criterion (for the trapdoor hypothesis)
find a class invariant or volcano level exhibiting a weakness absent from P-256.
## Falsification criterion (for the trapdoor hypothesis)
all named weaknesses are class invariants strong for P-256 AND volcano flat. -> FALSIFIED (this doc).
## Reproduction command
gp -q experiments/ecdlp_prime_field/round017_p256_cm_volcano.gp
python3 experiments/ecdlp_prime_field/round017_glv_scan.py
```

**Result.** Null hypothesis supported; trapdoor hypothesis falsified for all *named* weaknesses
(THEOREM/RESTRICTED THEOREM). See §1–§5 numbers, all reproduced in `round017_*.log`.

---

## 7. What this does NOT rule out (OPEN — where a sub-rho attack would still have to live)

Per AGENTS.md §5/§17, every negative is paired with the next positive question.

- **(O-1) Non-class-invariant, outside-model-M algebraic structure.** Claim 4.1 is model M only.
  A curve B in the class could in principle have a representation enabling crossbred/XL with an
  *exploitable* (gate-meaningful) early fall below D_reg, or an intrinsic abelian-surface relation,
  not captured by the per-variable-degree invariance. This is the *same* frontier the prime-field
  campaign already flagged (PO-004 §1.5; PO-007). **No known mechanism produces such structure over
  a prime field** (no subfield to descend to; the field F_p is isogeny-fixed), but it is not a
  theorem. *Next:* test whether *any* crater-neighbor curve opens a gate-meaningful fall the start
  curve does not — reuse `round016_gated_meter.sage` across ℓ=2,3,5 horizontal neighbors of a
  32-bit P-256-like curve (this is H10's original next action, now with the volcano known to be
  flat so "neighbor" = horizontal CL-action step).
- **(O-2) Horizontal vectorization / class-group navigation.** Galbraith-2024 finds *some* isogeny
  between two *given* curves. Directing the attack to a *chosen* weak B presupposes B exists (O-1).
  The cost of computing the *specific* CL(O_K)-action element linking P-256 to a chosen curve
  (the "vectorization"/discrete-log-in-class-group problem) is itself believed hard (≈ subexp in
  |D_0|); not exploited here. *Next:* literature check on classical (non-quantum) vectorization
  cost for |D_0| ≈ 2^258 vs rho.
- **(O-3) Multi-target amortization via a shared isogeny atlas** (NR-007's original open caveat).
  Precompute the crater once, amortize descents over many targets. Bounded by h ≈ 2^127, itself
  rho-sized, but the amortized exponent across T targets was never measured. *Next:* model the
  amortized cost `cost(atlas) + T·cost(per-target descent)` and compare to `√(T·n)` (batched rho).
- **(O-4) Exact crater size / a genuinely small-crater sub-case.** Claim 2.2 is heuristic; if
  L(1,χ_D) were anomalously small, h could be materially below 2^127. *Next:* bound L(1,χ_D) under
  GRH (cheap) to pin h to within a small factor; confirm the crater is not small.

---

## 8. Three new theories generated by this result (AGENTS.md §14)

1. **Conservative (close to known work).** *Amortized isogeny atlas over the crater.* Precompute a
   navigation structure for Cl(O_K) once; reduce many ECDLP targets on P-256 to a fixed
   "reference" curve via cheap (Galbraith) isogenies, then batch-solve. *Why it might evade the
   barrier:* moves cost from per-target √n to a shared precompute. *Minimal test:* O-3 cost model
   on a 32–40-bit toy class with computable h. *Likely failure:* precompute ≈ h ≈ √n already; no
   net win. *Value if false:* a clean multi-target lower bound tying isogeny amortization to h.
2. **Representation change.** *Search the crater for a curve whose specific (a,b) gives a
   gate-meaningful Semaev early fall*, exploiting that coefficient density (not degree) varies
   across the class. *Why:* PO-004 fixes the *degree*, not the *coefficient pattern*; a sparse/
   structured (a,b) might trigger an exploitable fall outside model M. *Minimal test:* O-1
   gated-meter sweep over horizontal neighbors. *Likely failure:* falls remain FB-localized
   (gate-FAIL), as in NR-018/019/027. *Value if false:* extends NR-022 from "degree-invariant" to
   "exploitability-invariant" across the class — a sharper RESTRICTED THEOREM.
3. **High-risk speculative.** *Use the Kani product-isogeny embedding (the Galbraith-2024 lever)
   directly as an ECDLP relation engine:* the 2-dimensional product isogeny relating
   E_0×E_0 → E_1×E_1 imposes algebraic constraints (Frobenius eigenspaces, Weil pairing) on point
   images; ask whether those constraints yield decomposition relations cheaper than √n *without*
   needing a weak B. *Why:* it changes the object from a single curve to a PPAV with extra
   structure. *Minimal test:* write the Kani-construction constraints for a small E and count
   relations vs cost. *Likely failure:* the constraints encode isogeny-finding (≈ q^{2/5}), not
   DLP; transferring to DLP reintroduces √n. *Value if false:* a precise statement of why
   higher-dimensional isogeny representations don't reduce *discrete log* even when they reduce
   *isogeny finding* — the cleanest separation of the two problems.

---

## 9. Reusable lemmas (bank these)

- **L1.** For an ordinary F_q-isogeny class, the embedding degree k = ord_{#E}(q) is a class
  invariant (function of (#E, q) only). [THEOREM, §3.4.]
- **L2.** For an ordinary F_q-isogeny class with conductor f = 1, every curve has End = O_K; the
  class is one Cl(O_K)-torsor; there is no vertical (endomorphism-ring-changing) isogeny.
  [THEOREM, §1–§2.]
- **L3.** GLV/GLS feasibility is governed by |D_0| (minimal endomorphism degree ≈ |D_0|/4), an
  isogeny-class invariant; large |D_0| ⇒ no GLV anywhere in the class. [THEOREM, §3.5.]
- **L4.** "Isogeny finding is cheap" (Galbraith-2024) does NOT imply "ECDLP transfer is useful":
  usefulness needs a weak *destination*, which §3–§4 rule out for all named weaknesses. The two
  problems (isogeny finding vs discrete log) are separated by the existence-of-weak-target gap.
  [OBSERVATION, §5.2.]
