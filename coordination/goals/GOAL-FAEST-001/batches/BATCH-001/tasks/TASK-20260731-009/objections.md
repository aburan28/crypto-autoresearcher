# Red-team objections — TASK-20260731-009 (GOAL-FAEST-001, BATCH-001 expansion review)

Reviewer role: red-team. Requested policy: `review-adversarial`. Resolved model:
`opencode/deepseek-v4-flash-free`. Fallback used: none. Session independence:
declared — no lineage with the producer session (TASK-20260731-007); all
artifacts read post-hoc from the archived snapshot commit `0e6befda`.

Scope: IDEA-20260731-004, -005, -006 (the BATCH-001 expansion), reviewed under
the six checks in `review_report.yaml`. Verdicts: ADMIT / ADMIT / ADMIT.
Fatal objections: **0**. Nonfatal objections: **11** (4 for IDEA-004,
3 for IDEA-005, 4 for IDEA-006).

---

## Fatal objections

None. No idea is rejected: each names an exact attack object (never "attack
FAEST"), carries a matched baseline under one cost convention with the RSF-1
one-pair caveat and UNVERIFIED labels in place, is falsifiable in its
decisive direction with named controls, and is honestly distinguished from
IDEA-20260731-019, IDEA-20260731-002..003.

---

## Nonfatal objections

### IDEA-20260731-004 (QROM Fiat-Shamir extractor loss)

**OBJ-4-1 (nonfatal_revision_item) — Quantum grinding charge is unnamed in
the extractor-loss reconstruction.**

`L_QROM` lists kappa in its argument list, but the record never states how a
quantum forger's grinding work is charged. The honest prover grinds
classically (2^kappa salt searches), but a QROM forger who must produce a
challenge digest with kappa leading zeros can search the salt with Grover at
~2^{kappa/2} hash queries, with the depth charged under MAXDEPTH. A
2^{kappa/2} term can exceed the slack being probed. Leaving the charge
implicit in "the q-sweep" is a hole in the reconstruction spec; this is
exactly the class of term the reported 2026 retightening is said to address,
so the re-derivation must confront it explicitly.

*Required scope fix*: named re-derivation item in component (1) — the quantum
grinding charging model (2^kappa vs 2^{kappa/2} via Grover on the salt, with
MAXDEPTH depth accounting and the per-query AES-equivalent charge), decided
from the pinned sources' challenge-verification rule.

*Falsification route*: derivation-level sensitivity check — recompute the
charged bound with the grinding term at 2^{kappa/2} vs 2^kappa; if the
difference moves the bound across the category threshold, the reconstruction
is convention-sensitive and must be flagged, not silently resolved. Cheapest
run: the P2/P3 scaling controls (loss must grow with q, decay with |C|).

**OBJ-4-2 (nonfatal_precision_issue) — Dual-baseline framing makes the
quantum-AES comparison nearly content-free.**

The claim requires the charged bound to be >= 2^128 AND >= the matched
quantum AES baseline. Since the quantum AES baseline (Grover 2^64; charged
~2^85.8) is far below the category, any bound clearing 2^128 clears both, and
any bound below 2^128 is already a category break. The second clause cannot
discriminate anything, and it risks a reader treating a bound in
[2^86, 2^128] as a partial confirmation.

*Required scope fix*: state the sole falsification threshold as the claimed
category (2^128) at the deployed set; demote the quantum-AES comparison to an
informational consistency anchor.

*Falsification route*: none needed (framing fix); the decisive check remains
the charged bound at a named (q, tau) versus 2^128.

**OBJ-4-3 (nonfatal_precision_issue) — P4's toy ratio cannot certify the
quantum side and has a half-infinite confirmation band.**

(i) The toy measurement computes Renyi-2 divergences and measure-and-reprogram
bad-event probabilities of *classical* transcript/query distributions; it
cannot certify the loss against a quantum adversary (the record's own
confounder says this). P4's trigger must be phrased as undercharging on the
classical distributional component only. (ii) "direction: lower, ratio <= 1"
makes every ratio below 1 (including an arbitrarily loose bound) a
confirmation outcome; only the > 1 side carries information. The prediction
cannot discriminate a tight bound from a loose one.

*Required scope fix*: relabel P4 as a one-sided "must not undercharge on the
classical distributional component" check; state that a ratio far below 1 is
neutral (a loose bound is not a finding in a barrier lane) and that the
quantum side of the loss is carried by the derivation alone.

*Falsification route*: the > 1 undercharge trigger at any tested toy point,
then re-derivation at deployed parameters before any claim (the record's
FC2).

**OBJ-4-4 (nonfatal_gating_note) — The 2026 Renyi-divergence retightening is
unfiled and secondary-sourced.**

The reconstruction's "current tightest bound" input is a reported work
(RQ-FAEST-001 motivation, secondary reporting), not filed in knowledge/ and
not read. Its identity, existence, and exact form are unverifiable until
filed. novelty_status "unverified" is the honest consequence; this is a hard
dependency for component (1), not a defect in the proposal.

*Required scope fix*: file the retightening as a KN-LIT entry and read it
before any reconstruction output is reported; if unobtainable, state the
reconstruction uses the best *archived* bound and record the unread bound as
an open ingredient.

*Falsification route*: none needed (dependency, not a hypothesis).

---

### IDEA-20260731-005 (algebraic attacks on the degree-3 constraint system under partial openings)

**OBJ-5-1 (nonfatal_precision_issue) — The confirmation side of the algebraic
barrier is near-vacuous at deployed size.**

For any reasonable degree-3 system with n in the thousands, the binomial
accounting C(n + d_reg, d_reg) at d_reg >= 3 gives an exponent far above
126.1. "Extrapolated solve cost >= 2^126.1" is therefore expected to hold for
almost any constraint system, so a confirmation is weak evidence about
FAEST's deployed family specifically. The discriminating content is the
falsification direction: per-S-box cost flatness (P2), super-linear opening
leverage (P3), or a d_reg law that does not accumulate hardness.

*Required scope fix*: state the confirmation side's low epistemic value
explicitly in the experiment contract; require the barrier wording ("this
link is not the source of a forgery cheaper than AES key recovery") to be
justified by the measured law and its extrapolation, not by the sheer size of
the binomial.

*Falsification route*: cheapest — the per-S-box scale control (P2) at the two
smallest toy sizes (1 -> 2 S-boxes) with the existing DREG instrumentation; a
per-S-box cost ratio < 1 anywhere is the flatness tell that the extrapolated
barrier would be unsound.

**OBJ-5-2 (nonfatal_revision_item) — I_open modeling must pin who chooses the
openings.**

The record models openings as "positions a transcript's VOLE openings reveal,
modeled as fixed variables". But the forger chooses the transcript, hence
chooses the openings; the fixed-variable model conflates (a) leaks from
honest transcripts (irrelevant — the key holder has no need to attack) with
(b) openings the forger is free to set. In (b), fixing variables is a freedom
that can only make the solve easier — which is what P3's leverage ratio is
designed to catch — but the binomial baseline and the set of fixed positions
must come from the spec's actual opening pattern (which positions, how many,
challenge-determined vs prover-chosen), not from memory.

*Required scope fix*: elevate I_open pinning (spec v2.0 + pinned faest-ref
commit, per the KN-LIT-7619 layout) to a hard completion gate detail of the
constraint pinning component, mirroring RSF-4 discipline.

*Falsification route*: the opening-leverage ratio (P3) at toy scale with the
pinned I_open; a ratio > 1 is the super-linear-leverage structural finding.

**OBJ-5-3 (nonfatal_precision_issue) — d_reg is size-unstable; the
extrapolation ladder must be a hard gate.**

The degree of regularity is not a size-stable quantity, and the toy census
(1 S-box, 1-4 toy rounds) is a very different algebraic object from the
deployed 10-round family. The record's H4 admits "None beyond the method
itself" as rigorous support — honest, and correct as an assumption under test —
but the scaled-down-instance ladder in H4's validation plan and the d_reg +/-
1 sensitivity (already listed in required_metrics) must be hard completion
gates before any extrapolated number is reported.

*Required scope fix*: make the ladder (full pin -> census -> extrapolation at
each toy size, plus predicted negative cases) a completion gate of the
extrapolation component; enforce the d_reg +/- 1 sensitivity as a mandatory
metric.

*Falsification route*: the unstructured control (random degree-3 system must
match the semi-regular d_reg prediction at each toy size); a mismatch
invalidates the instrumentation before any census result is read.

---

### IDEA-20260731-006 (faest_em_* Even-Mansour matched baseline)

**OBJ-6-1 (nonfatal_revision_item) — Claim wording overstates: the EM
baseline sits at the category boundary with zero slack.**

The claim's "the EM variants' claimed category is backed by [the EM baseline]"
overstates a knife's-edge condition. The derived OWF baseline is exactly
2^n = 2^128 for faest_em_128* — zero slack — so it *supports but does not
establish* the category: the category holds only if the VOLEitH/FS layer
(001/002/004 objects) and the commitment terms (003) are also tight at the EM
instances' parameter sets, and if the charged constants (per-P AES-equivalent
cost, MAXDEPTH accounting) do not push the derived cost below 2^128. The
mechanism and interpretation_limits qualify this correctly; the claim field
itself should say "supported at the boundary, pending the other links".

*Required scope fix*: soften the claim field to "the EM OWF's matched baseline
is established at >= 2^n, which supports the claimed category only at the
boundary and only in conjunction with tightness of the VOLEitH/FS and
commitment links at the EM parameter sets".

*Falsification route*: the definition-pinning derivation (component 1) — if
the pinned definition is single-block with n-bit output, P1 fires immediately
with zero compute (any-preimage inversion ~1 P-evaluation): the cheapest
falsification in the batch.

**OBJ-6-2 (nonfatal_revision_item) — P2's inversion-cost ratio is a weak
discriminator at the tested toy sizes.**

MITM/slidex *search* cost is structure-insensitive: the number of
P-evaluations is 2^n whether P is AES-shaped or random, so the AES-vs-random
inversion-cost ratio is expected to be ~1 by construction and can move only
via per-evaluation cost differences or a qualitatively non-search algorithm
(which at n = 8..32 is unlikely to beat 2^n — a Groebner-style solve of the
inversion system is slower than 2^n search at those sizes). The informative
signals for the "low algebraic degree of P" question are the ANF degree
profile, differential uniformity, and fixed-point counts, which the record
currently demotes to supporting metrics.

*Required scope fix*: reframe P2 as a null-trend check (expected ratio ~1 at
every size; a controlled null is the honest outcome) and promote the ANF
degree profile, differential uniformity, and fixed-point counts to primary
predictions with their own minimum effects.

*Falsification route*: the unstructured control at the smallest toy size
(n = 8) — generic EM with a random P must saturate T*D = 2^n exactly; if it
does not, the harness cannot measure the ratio meaningfully. For the shortcut
question itself, the informative check is the toy P's ANF degree profile vs
the random-P null at matched sizes.

**OBJ-6-3 (nonfatal_gating_note) — The EM chain is not closed by the OWF
baseline alone.**

IDEA-20260731-019, IDEA-20260731-002..004 are specified at the AES-instance parameter sets
(faest_128f/s). The EM instances (faest_em_*) carry their own (kappa, tau,
eps_cc, field) parameters (UNVERIFIED placeholders), and with the OWF
baseline at exactly 2^n, the layer terms must be re-checked at the EM
parameter sets, not carried over from the AES instances. The record's
voleith_fs_soundness block implies the carry-over without naming the
assumption.

*Required scope fix*: name the carry-over assumption explicitly — the layer
terms (001/002/004 objects) must be evaluated at the EM instances' parameter
sets before any statement about the EM variants' full chain; the OWF baseline
alone is the boundary, not the chain.

*Falsification route*: none needed (scope note); the concrete route is the
BATCH-002+ assembly of 002+004 at the EM parameter sets, mirroring open
direction #4 of the ideation report for the AES variants.

**OBJ-6-4 (nonfatal_note) — P3 (charged Grover >= 128) is near-vacuous by
construction.**

Grover over the 2^{2n}-bit key space costs ~2^n = 2^128 OWF evaluations by
construction; the charged value can fall below 128 only through a modeling
error or a smaller-than-assumed key space. The record already labels this a
"parameter-level finding"; keep it as a sanity check and do not treat a pass
as evidence for the category claim.

*Required scope fix*: no change beyond keeping the sanity-check label;
optionally drop P3 from the primary predictions into required_metrics.

*Falsification route*: re-check the charged model and the pinned key-space
size if it ever fires (already the record's FC4).

---

## Summary

| Idea | Verdict | Fatal | Nonfatal | Cheapest falsification control |
|------|---------|-------|----------|-------------------------------|
| IDEA-20260731-004 | admit | 0 | 4 | Derivation: charged bound vs 2^128 at the pinned set with the named quantum-grinding charge (zero compute beyond the pinned sources). Cheapest run: P2/P3 scaling controls at toy scale (loss must grow with q and decay with |C|); the unstructured generic-QROM-loss-shape control must precede any FAEST-shaped interpretation. |
| IDEA-20260731-005 | admit | 0 | 3 | Unstructured control at the smallest toy cell (random degree-3 system d_reg vs semi-regular prediction — instrumentation calibration). Cheapest decisive: per-S-box scale control at 1 -> 2 S-boxes (ratio < 1 = flatness tell). |
| IDEA-20260731-006 | admit | 0 | 4 | Definition-pinning derivation (zero compute): single-block definition fires P1 immediately (~1 P-evaluation inversion). Cheapest run: unstructured control at n = 8 (generic EM with random P must saturate T*D = 2^n); informative shortcut probe: toy P ANF degree / differential profile vs random-P null. |

All three ideas are admitted as measurement/barrier lanes; none claims an
attack or a breakthrough; the 11 nonfatal items are revision items to carry
into the BATCH-002 experiment-design gate alongside the existing RSF-1..5.
The single batch-level gating dependency remains RSF-5 (spec v2.0 PDF-text
blocker), plus IDEA-004's own hard dependency on filing the 2026
Renyi-divergence retightening work (OBJ-4-4).
