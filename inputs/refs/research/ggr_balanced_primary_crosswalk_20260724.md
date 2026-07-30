# GGR 2025/1243 vs Balanced-Primary Crosswalk

Date: 2026-07-24

## Handoff: balanced-primary novelty crosswalk against GGR

### Claim or task

Determine whether the Galbraith--Gilchrist--Robert ascending-isogeny framework
already implies the balanced-primary sign-free Kummer-row criterion.

### Status

`NOVELTY-UNVERIFIED / ORTHOGONAL FORMULATION / NOT-A-BREAKTHROUGH`

### Source basis

This crosswalk uses the user-provided text of Galbraith--Gilchrist--Robert
2025/1243 and the public ePrint metadata.  Direct PDF retrieval from ePrint
returned HTTP 403 in this environment, so this is not a full independent PDF
audit.

Public metadata URL: <https://eprint.iacr.org/2025/1243>

### GGR mechanism in the supplied text

The relevant GGR route has three parts.

1. A distorted Weil/self-pairing computation gives partial information about
   how an oriented isogeny acts on torsion.

2. For nonramified torsion, the missing action is encoded as a conic

   ```text
   x^2 + xy Tr(omega_R) + y^2 N(omega_R) = v mod n.
   ```

   The nondegenerate case gives about `n` candidate torsion actions.

3. For ramified torsion `n | Delta_R`, the conic degenerates.  One obtains
   cyclic information on a point `Q`: the possible images satisfy

   ```text
   phi(Q0) = alpha Q1,     alpha^2 = v mod n.
   ```

   For squarefree `n` this produces a local square-root branch factor.  GGR
   converts cyclic information into full torsion information by composing with
   an `n`-isogeny and then runs a Kani/interpolation backend.  Their complexity
   theorem keeps the root-count factor `T`.

### Balanced-primary mechanism

Balanced-primary works at a different reconstruction interface.  It assumes
sign-free Kummer rows

```text
x(phi(P_i)) = x(Q_i)
```

for pairwise-coprime primary orders `n_i`.  It then proves that all matching
degree-`d` homomorphisms differ by global sign once

```text
beta(n_1,...,n_r) = min_S (prod_{i in S} n_i + prod_{i notin S} n_i) > 4d.
```

The proof does not enumerate local square roots.  It partitions any attempted
local sign disagreement into subgroups of `ker(phi-psi)` and `ker(phi+psi)`;
the degree parallelogram identity forces one of those two maps to vanish.

### Crosswalk result

No theorem in the supplied GGR text appears to state the balanced-primary
criterion or its complementary-product proof.

The relationship is:

- GGR gives the self-pairing acquisition and Kani conversion framework.
- GGR's ramified cyclic route keeps a `T` factor for square-root choices.
- Balanced-primary gives a sufficient condition under which those local sign
  choices are not distinct degree-bounded Kummer-map identities.
- Balanced-primary still needs a competitive direct Kummer-row decoder or a
  compact output representation to become a complexity improvement.

Thus balanced-primary is best described as an orthogonal reconstruction-stage
criterion layered on top of GGR-style ramified self-pairing rows, not as a
proved improvement over GGR.

### Failure modes

- The full GGR PDF may contain a remark or theorem outside the supplied text
  that already observes the same complementary-product sign collapse.
- Kani/interpolation may remain asymptotically preferable even if sign
  enumeration is redundant at the Kummer-map identity level.
- The balanced-primary decoder currently outputs dense explicit maps, so
  output cost can dominate.
- This crosswalk does not compare against WayFinder 2026/1219.

### Next concrete action

Acquire the full 2025/1243 PDF through a non-403 route or local library copy,
then check the exact wording around Section 4.3 and Theorem 4.3 for any
sign-oblivious Kummer-row uniqueness statement.  If absent, cite GGR for
acquisition/backend and state balanced-primary as a separate reconstruction
criterion.

### Artifact paths

- `research/balanced_primary_ggr_sign_factor_gate_20260724.md`
- `research/isogeny_breakthrough_refresh_20260724.md`
- `papers/balanced_primary_isogeny_identification/paper.tex`
