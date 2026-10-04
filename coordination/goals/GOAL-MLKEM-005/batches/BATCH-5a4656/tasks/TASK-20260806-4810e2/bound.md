# TASK-20260806-4810e2 -- C1: the attainable dbeta bound, stated separately per deployment lane

Executor deliverable. Observations only; no hypothesis, heuristic, or ML-KEM
security claim is declared supported, rejected, or closed. AGENTS.md rule 12
is UNMET and UNWAIVED, inherited. No status change to any `EV-MLKEM-*` record
or `KN-*` entry is made or proposed by this file.

ZERO NEW BKZ REDUCTIONS AND ZERO NEW ESTIMATOR SEARCH beyond what
`BATCH-a51f91/TASK-20260805-9672b3` already validated. Every number below
either (a) is a convexity fact requiring no estimator call, or (b) is quoted
directly from `TASK-20260805-9672b3/receipt.json` (`headline_observations_NO_INTERPRETATION`)
or `TASK-20260805-9672b3/results.json`, both already committed at
`BATCH-a51f91`'s snapshot. No fresh `(d, beta)` estimator call was made by
this task; see `receipt.json` in this directory for the "reused, not
freshly run" record.

## The mechanism scope, restated (binding on every number below)

The mechanism under study is best-of-`M` ciphertext selection for **session
recovery**, not key recovery. No number in this file is subtracted from the
in-repo `primal_bdd` margins of 2.80 / 6.04 / 1.28 bits (Kyber512 / 768 /
1024). Nothing here asserts an attack, a break, or a security claim in
either direction.

## The governing convexity bound (unchanged, quoted from the goal record)

`ledger/goals/GOAL-MLKEM-005.yaml`, `ceiling_known_in_advance` (verbatim):

> "the single-target optimiser sets f''(beta_1) = -0.292, so log2 M =
> f(beta_M) >= f(beta_1) + f''(beta_1)(beta_M - beta_1) = G"

i.e. **G <= log2(M) unconditionally**, and

> "dbeta/beta ~ 0.29*sqrt((1-rho)*ln M / beta)"

is the companion curvature-dependent formula for the fractional block
reduction, with `M` as the sole free parameter this campaign does not
control and `rho` a correlation parameter this task does not estimate (not
attempted; no source for it is cited anywhere in this campaign's committed
artifacts).

## The census this bound is stated against (BATCH-a51f91 TASK-20260805-e6a153, `census.json`)

24 sourced rows. Per the corrected classification in `EV-MLKEM-d146a5.yaml`
`corrections_to_this_batch` CX-1 -- which this task treats as authoritative
over the census's own uncorrected one-sentence summary -- the M=1 bucket
splits into 2 firm normative single-use rows, 2 caveated single-use rows,
2 "one per handshake under a reuse-permitting clause" rows, and 8
count-unstated rows. This task's two lanes are drawn from that corrected
split, exactly as the handoff specifies.

---

## Lane (a): THE NORMATIVE SINGLE-USE LANE -- R20 (SSH), R21 (IKEv2)

**R20** -- `draft-ietf-sshm-mlkem-hybrid-kex-10`, Sec. 6: "generating an
ephemeral key exchange keypair for ECDH and ML-KEM per connection is
REQUIRED by this specification." (`census.json` row R20)

**R21** -- `draft-ietf-ipsecme-ikev2-mlkem-09`, Sec. 3: "Generating an
ephemeral keypair and ciphertext for each ML-KEM key exchange is REQUIRED
by this specification." (`census.json` row R21)

Both rows carry a normative, ML-KEM-specific, per-key `REQUIRED` freshness
rule. One keypair issues exactly one ciphertext in each protocol, so
**M = 1** in this lane by the census's own `m_derivation` field for both
rows, with no time bound, no rate, and no estimator call required to reach
it.

### C1 statement, lane (a)

> **The attainable reduction is <= 0 bits, because G <= log2(M) = log2(1) =
> 0 by the goal record's own convexity bound; the mechanism has no room to
> operate in this lane regardless of cost model.**

- `X = 0` bits. `Y = 0` bits are model assumption -- this is not a modelled
  quantity at all. It is the convexity inequality `G <= log2 M` evaluated at
  `M = 1`, which needs no cost model, no BKZ-profile curvature `f''`, and no
  estimator call: `log2(1) = 0` is arithmetic, not a readout.
- No RC.MATZOV call, no finite-difference table, and no `f''` sensitivity
  table attaches to this lane's figure, because the figure is not
  curvature-dependent -- it is a ceiling of zero regardless of what the
  BKZ-profile curvature is. This satisfies the completion gate's requirement
  that "the normative lane's bound is exactly 0 by convexity, not estimated."
- Named explicitly, as the handoff requires: **R20 and R21**.

---

## Lane (b): THE COUNT-UNSTATED LANE -- 8 deployment modes

Per `census.json` and `EV-MLKEM-d146a5.yaml` `what_is_NOT_established`, the
eight rows carrying `m_class: count_unstated` are:

| row | spec | key role |
|---|---|---|
| R06 | RFC 9180 (HPKE), recipient key reuse | static |
| R10 | RFC 9420 (MLS) + draft-ietf-mls-extensions-10, last-resort KeyPackage | static / semi-static |
| R15 | draft-ietf-tls-esni-25, ECHConfig HPKE key | static |
| R16 | draft-connolly-cfrg-xwing-kem-10, X-Wing | unrestricted |
| R17 | draft-ietf-lamps-kyber-certificates-11, ML-KEM in X.509 | static (certified) |
| R18 | RFC 9629 + draft-ietf-lamps-cms-kyber-13, CMS KEMRecipientInfo | static |
| R19 | OASIS PKCS#11 v3.2, ML-KEM token object | static (token) |
| R23 | Signal PQXDH, last-resort prekey | static / semi-static |

Each row's own `m_derivation` (`census.json`) confirms no numeric M, in
either direction, is stated by the retrieved specification text. The
normative delegation chain that could in principle have supplied one --
`draft-ietf-tls-hybrid-design-16` Sec. 2's "any bounds in the specification
of the KEM or subsequent security analyses" -- terminates without a value at
both limbs: FIPS 203 states none (`census.json` R01;
`EV-MLKEM-d146a5.yaml` `what_is_established` item 3, independently
re-verified by the validator's negative full-text search), and the
"subsequent security analyses" limb lands at
`draft-sfluhrer-cfrg-ml-kem-security-considerations-05` Sec. 4
(`census.json` R24), which endorses reuse "for multiple incoming
ciphertexts" and likewise states no count.

### C1 statement, lane (b)

**No bound is sourceable here from either mathematics or the standards
stack.** This is not a gap this task can close at zero new compute; it is
the finding `EV-MLKEM-d146a5.yaml` already recorded under
`what_is_NOT_established`: "NO CEILING ON M... The absence is an absence of
a stated number in both directions; it is not a sourced ceiling and must
not be read as one" (`census.json`,
`does_any_standardised_mode_state_M_above_2_20`).

Any `G > 0` figure for this lane is therefore **not a mathematical result**.
It would be a deployment-policy assumption about `M`, dressed as a
computation, using the formula

```
dbeta/beta ~ 0.29 * sqrt((1 - rho) * ln M / beta)
```

with `M` chosen by the reporter rather than sourced.

### This task's choice: OMIT the illustrative figure

The handoff explicitly names omission as an acceptable, arguably
preferable, outcome, and this task takes it: **no numeric M is chosen and
no illustrative G-bits figure is printed for lane (b).**

Reasons, stated plainly rather than hedged:

1. **No principled M exists to plug in.** The census's own
   `does_any_standardised_mode_state_M_above_2_20` finding is symmetric: the
   absence of a stated ceiling is not evidence for any particular scale,
   small or large. Any of 2^10, 2^20, 2^40, or 2^60 ciphertexts is equally
   "illustrative" and equally unsourced; picking one manufactures a
   specific-looking number the standards stack does not supply, which is
   exactly the overclaim risk `docs/inventor-protocol.md` warns against.
2. **Even a chosen M would not resolve to a stable figure at this
   precision**, per `fpp_sensitivity.json` (this task's own companion
   deliverable, reusing `TASK-20260805-9672b3`'s already-measured data at
   zero new compute): the beta-optimiser's own integer staircase and the
   linearisation-vs-finite-difference gap already move the curvature-
   dependent readout by single-digit-percent amounts to several blocks at
   FIXED M, before any uncertainty in M itself is even introduced. Compounding
   an unsourced `M` with an already-noisy curvature readout would present two
   stacked assumptions as one clean number.
3. Choosing not to print a number is the literal completion-gate branch this
   handoff offers ("If lane (b)'s illustrative figure is omitted entirely
   because any M choice would be indefensible, that is an ACCEPTABLE and
   arguably preferable outcome").

**What lane (b) is left as:** an open free parameter. If a future
Coordinator or a future task supplies a sourced or explicitly stipulated `M`
for one specific deployment mode (e.g. from an operational telemetry figure
for a particular HPKE recipient population, if such a source is ever
obtained), the formula above and the `fpp_sensitivity.json` table are
already staged to convert it -- but that conversion is not performed here,
and no number stands in for it.

---

## The CM-2 objection: multi-ciphertext attack cost is not priced end to end

`VAL-20260806-bb0559` and `RT-20260806-d008e0` (cited in
`EV-MLKEM-d146a5.yaml` and echoed in `DEC-20260805-4823db.yaml`) both note
that pricing only BKZ-reduction blocks does not price a multi-ciphertext
attack end to end. This task addresses it explicitly rather than dropping it
silently, per the handoff's instruction.

**The bound above (lane (a)'s `<= 0` bits, and lane (b)'s "no bound
sourceable") is a statement about the LATTICE-REDUCTION TERM ALONE** -- the
`primal_bdd` / `cost_zeta` block-size optimisation under RC.MATZOV that
`TASK-20260805-9672b3` exercised. It is, at most, a **lower bound on total
attacker cost**, not a complete multi-target cost model. This task does not
attempt to complete that model. The additional cost terms a complete
accounting would need, named as unquantified line items rather than priced:

- **Query/collection cost**: obtaining `M` ciphertexts under one static
  encapsulation key in the first place -- e.g. `M` legitimate protocol runs
  observed or induced, at whatever rate the deployment context (lane (b))
  permits. No retrieved specification bounds this rate either (same census
  rows), so this term inherits lane (b)'s own unsourced-`M` problem rather
  than resolving it.
- **Storage cost for `M` candidates**: best-of-`M` selection requires
  holding state (reduced bases, partial reductions, or per-ciphertext
  target vectors) for up to `M` candidates simultaneously or across a
  bounded window; this is not represented anywhere in the `primal_bdd`
  RC.MATZOV cost, which prices one reduction against one target.
- **The selection step itself**: comparing or ranking `M` candidates to
  identify the most favourable one adds a term that scales with `M` (at
  minimum `O(M)`, more if per-candidate work beyond a single comparison is
  needed); RC.MATZOV's reported `rop` figure contains no such term.

None of these three terms is quantified by this task, by
`TASK-20260805-9672b3`, or by any other artifact in this campaign's
committed record. **The bound stated above is therefore explicitly scoped
as a lower bound on attacker cost from the lattice-reduction term alone.**

---

## Completion-gate self-check

- Both lanes stated separately, never blended into one number. YES (lane
  (a) and lane (b) above, distinct sections).
- The normative lane's bound is exactly 0 by convexity, not estimated. YES
  (`log2(1) = 0`; no estimator call).
- The count-unstated lane either states no bound is sourceable, or clearly
  labels any illustrative figure and pairs it with the `f''` table. YES --
  this task took the "no bound sourceable, illustrative figure omitted"
  branch, with reasons stated.
- The CM-2 objection is addressed explicitly, not silently dropped. YES
  (section above, three named unquantified cost terms).

## What this file does NOT establish

- No numeric dbeta, no numeric G, and no bit figure for any lane except the
  `<= 0` convexity result for lane (a).
- No claim about M's true value in any of the eight lane-(b) modes.
- No completion of a multi-target cost model; the three named terms remain
  unquantified line items, not estimates.
- Nothing here changes any `EV-MLKEM-*` or `KN-*` record's status, and no
  hypothesis or heuristic is declared supported, refuted, or closed.
