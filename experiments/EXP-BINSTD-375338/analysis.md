# Analysis: EXP-BINSTD-375338 (H-BINSTD-74b002)

Review plan: `experiments/EXP-BINSTD-375338/review/review-plan.yaml`
(`REVIEW-BINSTD-375338-20261001`), written before this analysis.
Producer: TASK-20261001-ff051b. Distinguishing outcome target:
`DO-1-equivariance-confirmed` → scoped `support` (HOLD-R confirmed;
source IDEA per-instance leaf-count alternative rejected at toy;
STRUCTURALLY_EMPTY census for ECC2K-130/K-163; live rows route to
FROB). No deployed-curve break; no leaf-ratio~1/mu claim; no exponent
claim. Stages 0–1 only.

## Observation

**Validity (J1).** Seven run directories under `runs/`. Execution report
lists six completed IDs and one invalid:

| run | arm | status | valid |
|-----|-----|--------|-------|
| RUN-BINSTD-66e032 | Stage 0 census/fixtures | completed_valid | true |
| RUN-BINSTD-822306 | K19 (a)(b)(c)(e) primary | completed_valid | true |
| RUN-BINSTD-8c9916 | K19 prior test-(e) variant | completed_valid | true |
| RUN-BINSTD-8d5245 | Z/l replica (5 seeds) | completed_valid | true |
| RUN-BINSTD-d89f6a | K17-STABLE | completed_valid | true |
| RUN-BINSTD-4150f4 | NULL-RC1 primary | completed_valid | true |
| RUN-BINSTD-5e64fc | NULL-RC1 over-strict probe | invalid_measurement | false |

Every run has `manifest.yaml`, `raw-result.json`, `environment.json`,
`stdout.log`, `command.txt`. Raw metrics agree with
`stage1/metrics-summary.json` and `stage1/controls-report.yaml` for
primary axes. Within `maximum_runs: 20` (7 used). Bedrock appears only
as prohibition text in the specification — not selected, configured,
probed, contacted, or used. No per-instance CNF-XOR leaf-count arms;
`unauthorized` list in metrics-summary includes leaf-ratio~1/mu and
Stage >1. Manifests record `dirty: true` at write time (pre-archive),
disclosed.

K19 primary `RUN-BINSTD-822306` carries `certificate.kind: decomposition`,
`verified: true`, `certificate_ok: 85`, `certificate_fail: 0`. Prior
test-(e) variant `8c9916` also verified (retained; tuple-orbit lex-min
correction on 822306 is the primary). Invalid RC1 `5e64fc` is
infrastructure / probe over-strictness (x=0 fixed points with B in F_2),
superseded by `4150f4` — not negative mathematical evidence.

**Stage 0 (J2).** Census RECOMPUTED: all listed `n` match frozen
`ord_n(2)` column. Reachability cells: ECC2K-130 (`n=131`,
`ord=130`) and K-163 (`n=163`, `ord=162`) `STRUCTURALLY_EMPTY`; live
rows K-233 / sect239k1 / K-283 / K-409 / K-571 marked LIVE with FROB
routing note. Koblitz A,B six-row fixture match; hexblob `(0xHEX)`
regex accepts; orbit-system restatement present. No scientific group
walks on deployed curves. No break. No leaf-ratio claim.

**Blind re-derivation (J2/J3).** From the multiplicative-order
definition alone (not producer Stage-0 code): `ord_n(2)` recovers
`{17:8, 19:18, 131:130, 163:162, 233:29, 239:119, 283:94, 409:204,
571:114}` — exact match. Trial division confirms `130873` prime and
`4*130873=523492` matches frozen / measured `#E` on BIN-TOY-K19.

**Stage 1 equivariance + unsoundness (J3).** BIN-TOY-K19 primary
(`RUN-BINSTD-822306`, 50 targets, 85 certified decompositions):

- (a) `same_instance_hits = 0` (predicted 0)
- (b) `conjugate_instance_hits = 1.0` (85/85); `shifted_legs_in_V_fraction = 0.0`
- (c) `leg_swap_hit_rate = 1.0`
- (e) `solutions_lost_under_canonical_constraint = 11` (>0);
  `solutions_lost_median_fraction = 0.0` **OUTSIDE** pre-registered
  band `[0.663…, 0.947…]`; worst fraction `2/3`. Producer note:
  `V={deg<10}` elements are preferentially orbit-lex-minimal
  (~92.5% of V), so tuple-orbit canonical constraint deletes far fewer
  than free-action `1−1/n`. Unexpected vs numeric band; recorded, not
  discarded. Qualitative unsoundness (`solutions_lost>0`) still holds;
  HEUR-H1 falsification (`solutions_lost=0` on every target with ≥1
  certified decomposition) does **not** fire.

Z/l scalar replica (`RUN-BINSTD-8d5245`, seeds
`{20261001…20261005}`): `same_instance_hits_total=0`;
`conjugate_instance_hits_mean=1.0` across five seeds.

**Controls (J4).** Leg-swap pass (above). BIN-TOY-K17-STABLE
(`RUN-BINSTD-d89f6a`): `shifted_legs_in_V_fraction=1.0`,
`n_targets=50`, `same=0`, `conj=1.0`, `tau_stable_pass=true`.
NULL-RC1 primary (`RUN-BINSTD-4150f4`):
`every_shifted_reports_not_on_curve=true` for x≠0 probes
(`tuple_probe_on_x_nonzero=0`); x=0 exception disclosed. Proves-too-much
polarity holds: RC1 fails as endomorphism; non-stable K19 in_V=0;
leg-swap sees genuine same-instance symmetry at 100%.

## Comparison

Matches `DO-1-equivariance-confirmed` and the frozen primary axes
(equivariance, unsoundness count >0, census empty/live, stable-V
control). Does not light DO-2 (Lemma A2 failure / same_instance_hit),
DO-3 (solutions_lost=0 / constraint surprisingly sound), or DO-4
(instrument invalid). Comparison-to-prediction block: A/B/D match;
C median band miss with `solutions_lost_count=11` retained. Blind
`ord_n(2)` and `l_order` primality agree with producer. Multi-arm
agreement on `(same=0, conj=1.0)` across K19, Z/l (5 seeds), and K17
is exact. No leaf-ratio~1/mu measurement claimed or authorized.

## Inference

Valid Stages 0–1 package supports H-BINSTD-74b002's scoped HOLD-R
restatement at strength `replicated` (K19 certified primary + five-seed
Z/l replica + K17 stable-V control + RC1/leg-swap polarity + Stage 0
census). Decision: `support` — absolute Frobenius is equivariance
between conjugate targets (not per-instance search-tree symmetry) at
the tested toys; a single-instance shift-canonical constraint is
unsound (`solutions_lost=11>0`); orbit-batched gain needs a
Frobenius-stable V (K17 in_V=1.0 vs K19 in_V=0.0); ECC2K-130 and
K-163 are STRUCTURALLY_EMPTY for this seam. Source IDEA-20260922-7ab503
per-instance leaf-count / leaf-ratio~1/mu alternative is rejected at
the toy boundary (claim text immutable/`proposed`; restatement lives on
this hypothesis). Hypothesis `approved → supported`. Experiment
`approved → analyzed`. Promote `KN-FIND-316d09`.

HEUR-H1's free-action median band is **not** confirmed at this cell
(median 0.0 outside band under V-orbit-lex-min bias). That is a
scoped limitation on the quantitative free-action model, not a
falsification of qualitative unsoundness and not an excuse to revive
per-instance leaf division by μ. No exponent move; no deployed break;
no Stage 2.

## Limitation

- Toy tier only: n∈{17,19}, m=2, polynomial-basis window V; no
  deployed attack run at n≥131.
- HEUR-H1 quantitative median band missed; free-action `1−1/n` model
  does not transfer to median lost-fraction under this V-orbit-min
  bias. Worst-case lost fraction still ≤2/3 < band lower edge.
- Coordinator-direct review without independent validator/red-team
  (PD-1); seed/arm replication within one implementation.
- Manifests dirty-at-write; prior RC1 invalid probe retained.
- Prior K19 test-(e) variant (per-coordinate orbit-min) retained;
  primary uses tuple-orbit lex-min.
- No leaf-ratio~1/mu claim; no normal-basis solving-degree result
  (deferred HOLD-I / RQ-FROB); no exponent claim.
- Transfer of equivariance/unsoundness or EMPTY census reading to
  deployed security claims is an explicit non-claim.
