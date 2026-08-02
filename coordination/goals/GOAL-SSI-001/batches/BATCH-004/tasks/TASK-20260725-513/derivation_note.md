# Derivation note — GOAL-SSI-001 BATCH-004

Task `TASK-20260725-513` · access date 2026-07-25  
Resolved model: `cursor-grok-4.5-high-fast` (research-sol-max unavailable; fallback)  
Idea: `IDEA-20260725-002` (revised public-input model per `DEC-20260725-004`)  
Disposition: **MATERIAL_IN_SOME_REGIME** (narrow auxiliary-orientation class only)

## 1. Tightened public-input model (non-silent-CSIDH)

Public inputs:

1. Supersingular curves \(E_0, E_1\) presented as a **path-finding / CGL-style**
   instance (endpoints), not as a CSIDH public-key tuple.
2. An independently published non-scalar endomorphism
   \(\alpha \in \mathrm{End}(E_0)\) of degree \(d = \mathrm{poly}(\log p)\), with
   known minimal polynomial (effective order \(\mathbb{Z}[\alpha]\), discriminant
   \(\Delta\)).
3. **Orbit membership is falsifiable, not protocol structure:** either
   (i) it is an explicit additional public bit / certificate that \(E_1\) lies
   in the \(\mathrm{Cl}(\mathbb{Z}[\alpha])\)-orbit of \(E_0\), or
   (ii) the derivation must treat unknown orbit membership as failing closed
   (no free search over the full supersingular set).

Forbidden silent identity: \((E_0,[a]*E_0)\) CSIDH public-key packaging without
stating that the claim is only classical CSIDH vectorization vs unoriented
baselines (documentation-only; not used here).

## 2. Reduction to charged Cl-vectorization

When orbit membership is public/certified:

1. Work in \(\mathrm{Cl}(O)\) for \(O=\mathbb{Z}[\alpha]\).
2. Recover a connecting ideal by classical MITM/BSGS in the class group.
3. Charge each class-group action evaluation as an isogeny-walk unit.
4. Step-count heuristic cost \(\tilde{O}(\sqrt{h})\) with \(h=\#\mathrm{Cl}(O)\).
5. If Cl tables of size \(\Theta(\sqrt{h})\) are materialized, apply Wiener
   full-cost analogy: full cost \(\tilde{O}(h^{1/3})\) for high-memory tables
   (reported analogy; same hedge family as `KN-TECH-050`).

If orbit membership is **not** public: testing membership / finding an oriented
path on the full supersingular graph is not charged below the unoriented
`KN-TECH-050` baselines in this note → treat as
`REDUCTION_REQUIRES_UNCHARGED_ORACLE_OR_FULL_END` for that subcase.

## 3. Class-number regimes vs KN-TECH-050

Use the standard heuristic \(h \approx \sqrt{|\Delta|}\).

### Regime A — poly-bounded discriminant (\(|\Delta| = \mathrm{poly}(p^0)\))

- \(\sqrt{h} = \mathrm{poly}(\log p)\) (or small polynomial in the degree bound).
- vs \(\mathbb{F}_{p^2}\) claw-PCS \(\tilde{O}(p^{1/2})\): **strictly cheaper**
  asymptotically when orbit membership is public.
- vs high-memory MITM full-cost \(\tilde{O}(p^{2/3})\): also cheaper.
- vs \(\mathbb{F}_p\) DG \(\tilde{O}(p^{1/4})\): also cheaper **if** the instance
  is somehow \(\mathbb{F}_p\)-rational with tiny \(\Delta\); such curves are
  special CM / known-orientation objects, not generic CGL endpoints.

**Materiality caveat:** publishing a poly-degree non-scalar \(\alpha\) on a
generic supersingular curve is End-hard in the same sense as `KN-LIT-074` /
`KN-OPEN-013`. Cryptographically natural sources of public poly-bounded
\(\alpha\) are special curves (known j-invariants / constructed orientations),
i.e. an **auxiliary-structure** instance class under `KN-OPEN-015`, not pure
unoriented CGL.

### Regime B — CSIDH-like discriminant (\(\Delta \sim -p\))

- \(\sqrt{h} \sim p^{1/4}\).
- vs \(\mathbb{F}_{p^2}\) claw-PCS \(p^{1/2}\): step-count looks better, but
  CSIDH-like orientations live on \(\mathbb{F}_p\)-rational supersingular curves,
  so the honest matched baseline is **Delfs–Galbraith** \(\tilde{O}(p^{1/4})\)
  (`KN-TECH-050`), not claw-PCS.
- vs DG: **same order** under the heuristic — **not** a material asymptotic
  advantage. Default expectation from `DEC-20260725-004`:
  `NEVER_BEATS_BASELINE` on \(\mathbb{F}_p\) for \(\Delta\sim -p\).

## 4. Disposition

**MATERIAL_IN_SOME_REGIME** — only for:

- path-finding endpoints with **independently published** poly-bounded
  \(\alpha\) on \(E_0\),
- **public/certified** orbit membership,
- comparison against \(\mathbb{F}_{p^2}\) `KN-TECH-050` claw-PCS / MITM-full-cost,

and with the interpretation limit that this is an auxiliary-orientation
instance class, not a generic CGL break and not a CSIDH improvement.

For CSIDH-like \(\Delta\sim -p\) on \(\mathbb{F}_p\): record
`NEVER_BEATS_BASELINE` vs DG as the default sub-result.

For missing orbit membership: `REDUCTION_REQUIRES_UNCHARGED_ORACLE_OR_FULL_END`.

## 5. What this does / does not claim

- Does **not** claim a sub-\(p^{1/4}\) attack on generic unoriented End/path-finding.
- Does **not** reopen `IDEA-20260725-001` cost-model hygiene.
- Does **not** use torsion images.
- Does **not** meet GOAL-SSI-001 completion criteria (no independent confirmed
  mechanism with reproducible advantage on a survivor protocol as deployed).

## 6. Cheapest next uncertainty

If the program wants a protocol-relevant positive: either (i) exhibit a
deployed survivor that publishes poly-bounded \(\alpha\) without already
publishing End, or (ii) switch lane to SQIsign-transcript / other auxiliary
leakage with a typed leakage model. Otherwise close IDEA-20260725-002 as
**scoped residual documentation** under `KN-OPEN-013` / `KN-OPEN-015`.
