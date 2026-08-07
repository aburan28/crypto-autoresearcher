# Independent Review: `papers/semaev-conservation-specialization/paper.tex`

Dispatched by the top-level session as an independent, fresh-context review agent
(`general-purpose` subagent type, no memory of the manuscript's authorship), briefed to
act as a skeptical reader with expertise in function fields and arithmetic geometry and
tasked specifically with finding a gap in Lemma 2.3 and Lemma 3.2 — the two steps the
manuscript's own Section 9 named as unreviewed at the time of dispatch. Read the full
manuscript (1103 lines at review time) and independently re-derived, from first
principles, every load-bearing step, rather than trusting the paper's own risk
self-assessment.

**Provenance note, stated as plainly as everywhere else in this session's records:** this
is one automated review pass, by one model, in one session. It is real, adversarial,
independently-derived scrutiny — not a rubber stamp — and its passing verdict is genuine
evidence the arguments are sound. It is **not** peer review by a credentialed
mathematician, and does not substitute for one. See `papers/semaev-conservation-specialization/README.md`
and `paper.tex` §9 ("Status of the proofs") for how this is characterized in the
manuscript itself.

Two of the three findings below (Corollary 3.8's characteristic hypothesis, and the §2 /
Definition 2.2 wording gaps) were applied directly to `paper.tex` after this review
landed; the manuscript now reflects those fixes.

---

## 1. Lemma 2.3 (`lem:gamma`) — VERDICT: PASS

Quoted claim and proof (lines 256–266 at review time):
> "$M/L$ is Galois with $\mathrm{Gal}(M/L) = \Gamma \cong (\mathbb{Z}/2)^n$."
> "$\Gamma$ acts faithfully on $E^n$ by (P2): if $(\varepsilon_1,\dots,\varepsilon_n)$
> acts trivially then each $\varepsilon_i$ acts trivially on $E$, so
> $\varepsilon_i = \mathrm{id}$. Hence by Artin's theorem $M/M^{\Gamma}$ is Galois with
> group $\Gamma$. Finally $M^{\Gamma} = K(E^n/\Gamma) =
> K\bigl((E/\langle\iota\rangle)^n\bigr) = K((\mathbb{P}^1)^n) = L$, using
> $E^n/\Gamma = (E/\langle \iota\rangle)^n$ and (P1)."

**Faithfulness check.** The claimed inference — "trivial coordinatewise action ⟹ each
$\varepsilon_i$ trivial" — is about the action of $\sigma=(\varepsilon_1,\dots,\varepsilon_n)$
being the identity automorphism of the variety $E^n$, not about a single fixed point.
Restricting such a $\sigma$ to the slice varying only the $i$-th coordinate recovers
$\varepsilon_i$ as a self-map of $E$; if $\sigma=\mathrm{id}_{E^n}$ this self-map is
$\mathrm{id}_E$, so by (P2) $\varepsilon_i=\mathrm{id}$. This gives injectivity
$\Gamma \hookrightarrow \mathrm{Aut}(E^n)$. Feeding Artin's theorem needs injectivity
into $\mathrm{Aut}_K(M)$ (field automorphisms), not just scheme automorphisms — not
spelled out in the paper, but standard: $E^n$ is integral and separated, so two
morphisms into a separated scheme agreeing on a dense subset (equivalently, inducing the
same field automorphism) must be equal. Hence $\mathrm{Aut}(E^n) \hookrightarrow
\mathrm{Aut}_K(M)$, correct in every characteristic — the argument nowhere requires
$|\Gamma|$ invertible.

**Quotient identification $E^n/\Gamma = (E/\iota)^n$, re-derived from scratch (the
characteristic-2 concern the task named).** For a $K$-algebra tensor product with a
diagonal finite-group action, $(A \otimes_K B)^{G \times H} = A^G \otimes_K B^H$ holds in
**every characteristic with no restriction on $|G|,|H|$**: $(-)^G$ is the kernel of a
$K$-linear map, and tensoring a $K$-vector space is exact (pick a basis of $B$; then
$A \otimes B \cong \bigoplus A$ coordinatewise with $G$ acting diagonally, so the kernel
is $\bigoplus A^G = A^G \otimes B$). No Reynolds operator or linear reductivity is used,
so the usual char-$p$-divides-$|G|$ obstruction from invariant theory does not arise.
Likewise $\mathrm{Frac}(A^G) = \mathrm{Frac}(A)^G$ for any domain $A$ and finite group
$G$, in any characteristic (norm-clearing: for $x = a/b \in \mathrm{Frac}(A)^G$,
$x \cdot N(b) = a\prod_{g \neq e} g(b) \in A$ is $G$-invariant, and $N(b) \in A^G$).
Together these give $E^n/\Gamma \cong (E/\langle\iota\rangle)^n$ and $M^\Gamma = L$ in
every characteristic. (Sanity check against known geometry: this is the standard fact
that quotienting $E_1 \times E_2$ by the **full** product group $\{\pm1\}\times\{\pm1\}$
gives $\mathbb{P}^1 \times \mathbb{P}^1$, as opposed to quotienting only by the diagonal
$\Delta$, which gives the singular Kummer surface. The paper correctly uses the full
group here and the diagonal separately in Theorem 3.4.)

**Verdict: PASS.** No hidden reliance on $|G|$ being invertible; genuinely
characteristic-free. Minor exposition note (not a correctness issue): the
$\mathrm{Aut}(E^n) \hookrightarrow \mathrm{Aut}(M)$ step and the tensor-invariants
computation are used implicitly without derivation in the manuscript.

---

## 2. Lemma 3.2 (`lem:sep`) — VERDICT: PASS

Quoted proof core, including the paper's own self-assessment:
> "Each $a_{S,\varepsilon}$ is a surjective homomorphism of group varieties... the
> preimage $a_{S,\varepsilon}^{-1}(Z)$ is closed of dimension $n-1$... As $E^n$ is
> integral, its generic point lies in no proper closed subscheme."
> Remark: "$E[2]$ is a finite group scheme of order 4 in every characteristic — in
> characteristic 2 it is non-reduced — and Lemma [sep] only uses that it is finite, so
> no characteristic is excluded."

**(a) Is $a_{S,\varepsilon}$ a surjective group-scheme homomorphism in every
characteristic?** Yes. It factors as projection to the $S$-coordinates, then
$\prod_i [\varepsilon_i]$ (each $[\pm1]$ an automorphism of $E$ in every characteristic
— $[n]$ is always a finite isogeny of degree $n^2$, ordinary or supersingular), then
summation. Restricting to any one factor $i \in S$ already gives the isomorphism
$[\varepsilon_i]: E \to E$, so the image contains all of $E$; since $E^n$ is proper, the
scheme-theoretic image of a group homomorphism is a closed subgroup scheme, forcing it
to be all of $E$.

**(b) Is finiteness of $E[2]$ — not reducedness — actually sufficient?** Checked
carefully as this is exactly the flagged trap. Two independent facts combine:
- *Fibre dimension is translation-invariant, not reducedness-sensitive.* Every fibre of
  a homomorphism of algebraic groups is a torsor under the kernel, hence isomorphic
  after a field extension to a translate of $\ker(a_{S,\varepsilon})$, of dimension
  $n-1$ regardless of whether it is reduced.
- *"Generic point avoids proper closed subschemes" is purely topological*, unaffected by
  nilpotents: $E[2]$ and $E[2]_{\mathrm{red}}$ have the same underlying topological
  space, hence so do their preimages under $a_{S,\varepsilon}$. The generic point of the
  irreducible space $|E^n|$ cannot lie in any closed subset of strictly smaller
  dimension — nilpotent structure on the target is invisible to this argument.

Also verified this is the right notion for what is needed: "$\sum \varepsilon_i P_i \in
E[2]$" as an $M$-point condition is equivalent to $2\sum\varepsilon_i P_i = O$ in
$E(M)$, and $M$-points of $E[2]$ (for $M$ a *reduced* ring) automatically only see
$E[2]_{\mathrm{red}}$ anyway. So even in the supersingular characteristic-2 case, where
$E[2]_{\mathrm{red}} = \{O\}$ despite $E[2]$ having scheme-theoretic order 4, the
argument correctly captures "$2Q \neq O$ generically," which is all Lemma 3.2 needs.

**Verdict: PASS.** The paper's own remark is mathematically accurate. No characteristic-2
counterexample or failure mode could be constructed.

---

## 3. Theorem 3.4 (`thm:main`) — VERDICT: PASS

Independently re-verified the kernel computation. Direct combinatorial check: fixing any
single $\varepsilon_0 \in \{\pm1\}^n$, the condition $\sigma\varepsilon_0 = \varepsilon_0$
forces $\sigma_i = 1$ for every $i$ (coordinatewise cancellation), independent of which
$\varepsilon_0$ was chosen; likewise $\sigma\varepsilon_0 = -\varepsilon_0$ forces
$\sigma = (-1,\dots,-1)$. No "mixed" $\sigma$ can satisfy $\sigma\varepsilon \equiv
\pm\varepsilon$ for the all-ones $\varepsilon$. Matches the paper's claim exactly. The
subsequent Galois-correspondence steps (stabilizer $\Delta$, abelian ⟹ normal, geometric
integrality stable under finite quotients and base change) are standard and correctly
applied, using the same flatness/kernel argument as in Lemma 2.3.

**Verdict: PASS.** Correct assembly of Lemma 2.3 + Lemma 3.2; no unstated hypotheses
smuggled in.

---

## 4. Corollaries — spot-check results

- **Corollary 3.6 (irreducibility): PASS.** Transitivity ⟹ irreducibility is standard;
  correctly invokes Theorem 3.4(4) rather than assuming arithmetic = geometric monodromy.
- **Corollary 3.7 (imprimitivity/blocks): PASS.** Standard permutation-group theory,
  correctly applied to $(\mathbb{Z}/2)^{m-2}$. The side-claim that $H_I$ does not exhaust
  all subgroups for $m \geq 5$ was not independently re-verified (non-load-bearing).
- **Corollary 3.8 (discriminant square class): real scope issue, since fixed.** The
  $m \geq 4$ half carried no characteristic restriction in the statement, but its proof
  invokes "discriminant is a square iff Galois group ⊆ alternating group," which itself
  needs $\mathrm{char} \neq 2$. The manuscript already knew this three pages later
  (§5.2: "Corollary [disc] is not meaningful... in characteristic 2") but the corollary's
  own statement read as unconditional. **Applied fix:** `char K ≠ 2` now stated directly
  on the corollary.
- **Corollary 3.9 (density law): not independently re-verified in full.** The
  Hasse-bound-based $O(m^2/q)$ error estimate is routine but was not redone line by
  line; setup checked and consistent, no red flag found.

---

## 5. Additional issues found, and applied

1. **§2 justification of (P1), char 3 — fixed.** The specific short-Weierstrass form
   $x^3+Ax+B$ needs $\mathrm{char} \neq 2,3$ (eliminating the $x^2$ term needs dividing
   by 3); (P1) itself only needs a general separable cubic, available for any
   $\mathrm{char} \neq 2$. Cosmetic imprecision in one parenthetical, not a substantive
   gap (Definition 2.2 and Corollary 3.8's $m=3$ identity were already correctly scoped
   elsewhere). **Applied fix:** generalized to "a separable cubic," with short
   Weierstrass form noted as the char $\neq 2,3$ specialization.
2. **Definition 2.2 / Lemma 3.1 field-extension step — fixed.** Definition 2.2 states
   $S_m$'s defining property for $\bar{K}$-points; Lemma 3.1's proof applies it over an
   arbitrary algebraically closed $\Omega \supseteq M$, which need not literally contain
   $\bar{K}$. The extension is true and standard (definable by non-emptiness of a
   $K$-scheme, stable under algebraically closed field extension) but was used silently.
   **Applied fix:** one clarifying sentence added to Definition 2.2.
3. **Administrative, not mathematical.** The manuscript ships a placeholder author block
   (`[AUTHOR NAME]`), self-flagged as a pre-submission TODO — blocks literal
   "post as-is" submission but is not a correctness issue.

---

## Overall recommendation

**Lemma 2.3: PASS. Lemma 3.2: PASS. Theorem 3.4: PASS.** Independent re-derivation from
scratch — including re-proving the characteristic-free invariant-theory facts and
confirming the topological (reducedness-insensitive) nature of the generic-point
argument — did not turn up a gap in either flagged step, in any characteristic including
2. The one substantive issue found (Corollary 3.8's missing characteristic hypothesis)
and two minor wording issues have been applied to `paper.tex`.

**Overall, before this review: ready with minor fixes. After the fixes above: the core
mathematical content (Lemma 2.3, Lemma 3.2, Theorem 3.4, Corollaries 3.6–3.8) is sound as
proved**, subject to the standing caveat — stated in the manuscript's own §9 — that this
is independent automated scrutiny, not peer review by a credentialed mathematician
working in function fields or arithmetic geometry, and obtaining that review remains
outstanding.
