# Derivation note — GOAL-SSI-001 BATCH-006

Task `TASK-20260725-521` · access date 2026-07-25  
Resolved model: `cursor-grok-4.5-high-fast` (research-sol-max unavailable; fallback)  
Idea: `IDEA-20260725-003` · Model: **SQI-FS-T0**  
Disposition: **T0_FAILS_KANI_AND_PETIT_NECESSARY_CONDITIONS**

## 1. Restate SQI-FS-T0 from the knowledge spine

Public inputs under SQI-FS-T0 (`KN-TECH-028`, `KN-LIT-072`, `KN-LIT-073`):

1. Public-key curve \(E\) with **no** published \(\mathrm{End}(E)\) and **no**
   torsion-point images under a secret isogeny.
2. Signature parseable as Fiat-Shamir transcript
   \((C,\, c=H(\mathrm{pk},m,C),\, R)\).
3. Response \(R\) consists of **connecting isogenies of publicly recoverable
   degree** between **publicly named** curves (KLPT-produced paths answering
   challenges).

Excluded (not in T0): torsion basis images under a secret isogeny; adaptive
torsion oracles; free \(\mathrm{End}(E)\); uncited SQIsign2D-only fields;
reopening `IDEA-20260725-002`.

Spine sufficiency to freeze T0: **yes** at the level of `KN-TECH-028`'s reported
structure (commitment / challenge / connecting-isogeny responses). No version-
specific bit fields were invented.

## 2. KN-TECH-026 (Kani) necessary-condition check

`KN-TECH-026` applicability limit (quoted sense): requires **both**
(i) the isogeny degree and (ii) its **action on a known torsion basis**.

| Necessary input | Present in SQI-FS-T0? |
| --- | --- |
| Known degree of a secret isogeny to recover | Partial: response isogenies have public degrees, but these are **challenge-response connecting isogenies**, not SIDH's secret \(\phi\) with published torsion action |
| Images of a known torsion basis under a secret isogeny | **No** |

Conclusion: SQI-FS-T0 **fails** the Kani necessary conditions. The
glue-and-split embedding cannot be built from T0 alone.

## 3. KN-LIT-077 (Petit) check without torsion images

Petit (`KN-LIT-077`) exploits **torsion-point images** to improve unbalanced
isogeny instances. SQI-FS-T0 publishes no such images. Without torsion images,
Petit's torsion-using speedups **do not apply**.

## 4. Named non-torsion residual vs KN-TECH-050?

Public connecting isogenies between named curves are already the intended
SQIsign verification objects; they do not, by themselves, supply a new
End/path-finding oracle below `KN-TECH-050` matched baselines without either
(a) recovering \(\mathrm{End}(E)\) (the hardness core, `KN-OPEN-013`) or
(b) inventing additional leakage outside T0.

No named non-torsion auxiliary pathway with charged cost strictly below
`KN-TECH-050` / End baselines is identified inside T0.

## 5. Disposition

**T0_FAILS_KANI_AND_PETIT_NECESSARY_CONDITIONS**

Decision delta for `KN-OPEN-015`: under the frozen SQI-FS-T0 model, published
SQIsign Fiat-Shamir connecting-isogeny responses do **not** meet the necessary
auxiliary conditions of the SIDH-break Kani/Petit template. This is a
**negative classification**, not a cryptanalytic break and not GOAL completion.

## 6. Interpretation limits

- Zero curve/isogeny computation performed.
- Does not analyze SQIsign2D-specific fields absent from the spine.
- Does not claim SQIsign is broken or End is easy.
- Does not reopen orientation Cl-cost (`IDEA-20260725-002`).
