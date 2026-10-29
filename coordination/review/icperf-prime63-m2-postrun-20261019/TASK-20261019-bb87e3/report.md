# Blind Validator report: TASK-20261019-bb87e3

Review plan `REVIEW-ICPERF-PRIME63-M2-POSTRUN-20261019`; joints P1 and P2, both proves-too-much controls, and blind rederivation. This report concerns the historical `RUN-ICPERF-eb0d88` raw archive and frozen public inputs. It does not compare a candidate custody bundle with those inputs. Verdict: **P1 independently inventoried; P2's bounded facts verified; both known-false control conclusions rejected.** The frozen supervisor output contract was not satisfied. No solver certificate, successful relation extraction, base ranking, total IC cost, or rho comparison follows.

## Admission and blind scope

The detached checkout was `43cacc778f7f04cc426065d79de20ab7b2a81827`, with a clean worktree before writing. The active `CODEX_SESSION_ID` was `01a15726-e967-7983-a7d5-fc8f08bae009`. A read-only lookup of that exact ID in `/Users/adamburan/.codex/state_5.sqlite` returned `gpt-6-sol`, `xhigh`, provider `openai`, this checkout as cwd, and CLI `0.155.1`; the admitted Validator runtime receipt reported `review-adversarial`, exact-session verification, no fallback, and no degradation. Its global backend verification field is false, which does not expand the exact-session scope. The existing branch-backed goal-lane claim `TASK-20261019-bb87e3.1.claim.json` names this session, owner `validator-icperf-prime63-blind-20261019`, epoch 1, and precisely the two review file paths. No goal-lane claim was made here.

`CONDUCTOR_SESSION_ID=4ec9fd5c-69c0-41a2-a879-7e15286e5e83` was present before any edit. `conductor task claim T-4458 --project conductor -json` returned that same lease session ID, task UUID `d71d73a5-7dcd-41e1-bdfd-1a435d2c3fc1`, attempt `2f334c88-6478-4d2a-972a-374f9b4d4dd4`, lease `62dc44bb-baa1-410f-8a8b-4af0dc96255c`, fence epoch 1, and only the report and attestation path scopes. The two peer files under `TASK-20261019-02a5c2/` were absent when checked.

The admitted runtime receipt, binding overlay, and runtime custody manifest under `coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/reviewer-runtime/TASK-20261019-bb87e3/` were used only for session admission. They supplied no P1/P2 count, digest, equation, or outcome. I did not read the six `blind_from` sources listed in the review plan, the candidate bundle, or either peer review file. I checked only existence, not contents, of the two required run-root outputs. Scientific calculations below use the five original input files listed next.

## Permitted inputs and SHA-256

Sizes and SHA-256 values were recomputed from file bytes with Python `hashlib.sha256`, before interpreting JSON or tar members. Paths are relative to the checkout.

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| `experiments/EXP-ICPERF-515ae3/runs/RUN-ICPERF-eb0d88/diagnostic/raw.tar.gz` | 271137 | `f7e99a48012bccd39463b99635a511f747c86db7b7fd714c0a9d35a3ad0cfa7f` |
| `experiments/EXP-ICPERF-515ae3/trial-plan.json` | 4438 | `08f32f02a191dfd16f5342540716a327da73f5091528bac07cf5ee77cdb7cbc9` |
| `research/icperf_prime63_pilot_launcher_20261017/planted_public.json.gz` | 131282 | `0e86d86ff133870829c5432e58d08c0907e5e8940c149799b68299c65cfb7309` |
| `research/icperf_prime_475_target_systems_20261017/systems.json.gz` | 195642 | `4bb75b65b843a4b7ce8c0b7d8521d80a95b958f061e0ddf516639296a15fb589` |
| `research/icperf_prime63_pilot_launcher_20261017/planted_witnesses.json` | 18146 | `c9049b0c4fac1c83ca057d6da27e0c4a2cbfe52272aeab113beb419e068a2c0c` |

The field is `p=9223372021248595841`; the curve is `y²=x³+2901713853138158932x+545651861447567430 (mod p)`, with declared group order `r=9223372018953067627`. The request factor bases each contain 475 points with 475 distinct x coordinates. The common-target `systems.json.gz` is a separate public input with 21 systems and seven targets; its m=2 common target is `(8145669188327579032, 2241448525239296812)`, distinct from the three planted pilot targets below. I did not substitute it for a pilot request.

## P1: original raw archive inventory

I enumerated `raw.tar.gz` with Python `tarfile.open(..., 'r:gz')`, read each regular member's exact bytes through `extractfile`, checked `len(bytes)==TarInfo.size`, and computed SHA-256 over those uncompressed member bytes. There are exactly 15 regular members, 15 unique paths, no duplicate path, and no non-file member. The archive has no monitor request member or worker response member. I cannot conclude from the archive alone whether any other historical run file was omitted from it; run-tree reads were outside this blind scope.

| Member path | Bytes | SHA-256 |
| --- | ---: | --- |
| `coset-m2/call/phase.jsonl` | 1212959 | `d70756154d4bbb3d2a8d6846fbe1db3094d00f55107b7adada3351257b11fa6e` |
| `coset-m2/call/stderr.raw` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `coset-m2/call/stdout.raw` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `coset-m2/request.json` | 28397 | `9a172c65375c2d2dc2d73f6232fa52fa281afade4fcb76e00fbbbf32f35ecb91` |
| `monitor-null/call/phase.jsonl` | 1932 | `a2aebe6933efbd48a4463f2722cfabaa79410cf55c6172b04e91a1c9dd61134b` |
| `monitor-null/call/stderr.raw` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `monitor-null/call/stdout.raw` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `random-m2/call/phase.jsonl` | 1208903 | `43be41fbe821bcafee93963a49a4f75e6de779bb59536827507cd0b395992dc4` |
| `random-m2/call/stderr.raw` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `random-m2/call/stdout.raw` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `random-m2/request.json` | 127539 | `04e7668f12afb5769ce9f6c8b2e25eb052854c28a846e5e92ab4d19c39291c01` |
| `small_x-m2/call/phase.jsonl` | 1091332 | `263df5efa6992d3c926e24e8fabe3fb239458e65436ee04a2615348837832f73` |
| `small_x-m2/call/stderr.raw` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `small_x-m2/call/stdout.raw` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `small_x-m2/request.json` | 119619 | `88258142099602ebfe156af11f9843e25411b49b6db5675950c4192de27347ee` |

Each of the three parsed request objects equals, as a full JSON object, the matching `cell` in `planted_public.json.gz`. The request identities are:

| Cell | Arm / encoder | Request target `(x,y)` | Declared base-point SHA-256 | Equations / variables / maximum total degree | Base parameters |
| --- | --- | --- | --- | --- | --- |
| `coset-m2` | coset / quadratic_lift | `(4868894110195109235,2771984488349812754)` | `0f1edd54aa376536285df80564a6240f0cd4c69e6974e000b1c5346f44b7497c` | 26 / 25 / 4 | `coset=8467538000874705577`, `d=896`, `root_draws=2`, `seed=20261027`, `target_size=441`, `zeta=1879108966579984846`, `divisor_source=explicit` |
| `random-m2` | random / direct | `(7734344144040749472,4422301028978569862)` | `cac711d920977bec8bf8e3c0e8e6b738bde546372f64c7b51332cc7c941b4fc1` | 4 / 3 / 475 | `seed=20261017` |
| `small_x-m2` | small_x / direct | `(1573924939561700324,6475439617498684372)` | `5d8f2b3254b75858ecf65ba62ad3db08651483843e15c6e3511e89c6957cdfc3` | 4 / 3 / 475 | `bound=923` |

The base-point SHA-256 column is the request's **declared field**, not a hash I reconstructed from an unspecified serialization. The member SHA-256 values above are independently recomputed.

I parsed each `phase.jsonl` line as JSON, selected supervisor `start`, `terminate`, and `terminal` events, and used their raw UTC nanosecond timestamps. The order and terminal classes were:

| Cell | Start UTC | Terminal UTC | Per-call cap | Trace lines | Observed terminal class |
| --- | --- | --- | ---: | ---: | --- |
| `monitor-null` | 2026-10-19 21:13:45.878026 | 2026-10-19 21:13:45.882026 | 15 s | 5 | `infrastructure_monitor_error`, exit `-15`; `unreadable_live_root`, `prospective_null_injected` |
| `coset-m2` | 2026-10-19 21:13:45.892290 | 2026-10-19 21:23:46.034499 | 600 s | 2729 | `timeout_censored`, exit `-15` |
| `random-m2` | 2026-10-19 21:23:46.049525 | 2026-10-19 21:33:46.070140 | 600 s | 2549 | `timeout_censored`, exit `-15` |
| `small_x-m2` | 2026-10-19 21:33:46.109162 | 2026-10-19 21:43:46.150442 | 600 s | 2312 | `timeout_censored`, exit `-15` |

The traces' own `start` events state 8 GiB RSS and scratch caps for all four calls. The frozen trial plan has one trial, `prime63-m2-three-arm-diagnostic`, required artifacts `manifest.yaml` and `raw-result.json`, a 2160 s trial watchdog, and 8192 MiB trial memory cap. These limits and stop classes are observations and controls, not solver completion or measured attack cost. The raw trace phases show a final `groebner` begin for coset and `root_enumeration` begins for random and small_x, without terminal solver certificates.

## P2: frozen outputs, witness equations, and controls

For the first proves-too-much object, I used the frozen `trials[0].artifacts` list to identify exact required run-root paths. `test -e` returned false for both `experiments/EXP-ICPERF-515ae3/runs/RUN-ICPERF-eb0d88/manifest.yaml` and `experiments/EXP-ICPERF-515ae3/runs/RUN-ICPERF-eb0d88/raw-result.json`. I did not open either path. **Failure signature observed:** the historical run did not satisfy the frozen supervisor output contract. The archive's raw traces cannot replace those required outputs.

For direct witness evaluation, I matched each archived request to its planted public system by exact parsed-object equality, then matched the witness by `cell` and identical `target_point`. For every equation, each term was evaluated as `coefficient * product(root[variables[index]] ** exponent) mod p`; term values were summed modulo `p`. All root values were in `[0,p)`. The nonzero-residue index list was empty for all 26 coset equations and all four equations in each direct system. No scientific solver was invoked.

For the signed group equations, I checked each selected point and signed point lies on the stated curve, confirmed `signed_y = y` for sign `+1` and `signed_y = -y mod p` for sign `-1`, and found each selected unsigned point in its request's 475-point base. Here `selected.index` labels a factor slot; the separate zero-based base-list positions are shown below. I added the two signed points with the affine chord formula `lambda=(y2-y1)/(x2-x1) mod p`, `x3=lambda²-x1-x2 mod p`, `y3=lambda(x1-x3)-y1 mod p`.

| Cell | Signed points | Base-list positions | `lambda` | Computed sum = request target |
| --- | --- | --- | ---: | --- |
| `coset-m2` | `(4670656453157957121,4271105246429816532) + (5363246267916796448,8360682834016374166)` | 333, 234 | 7867776828857647281 | `(4868894110195109235,2771984488349812754)` |
| `random-m2` | `(2334714447473360411,4360512794719107210) + (7296815669183706672,7236604307851947416)` | 224, 268 | 5690943151890896023 | `(7734344144040749472,4422301028978569862)` |
| `small_x-m2` | `(610,5159613896899238608) + (473,6798473076674193280)` | 306, 243 | 7191693044480472995 | `(1573924939561700324,6475439617498684372)` |

For the second proves-too-much object, the exact `random-m2` root is `x1=2334714447473360411`, `x2=7296815669183706672`, `z=6822886193318937591`. Direct substitution gives residue vector `(0,0,0,0)` modulo `p`, and its two signed factors sum to the identical request target above. Thus a `certified_no_solution` assertion for this exact system would be contradicted by a concrete satisfying witness and must be rejected. **Failure signature observed:** that assertion fails the witness check. No actual `certified_no_solution` response occurs in the permitted raw archive; its actual `random-m2` stop is `timeout_censored`. I did not manufacture a response or treat the timeout as a certificate.

The named breaking artifacts for the two false conclusions are the absent required run-root paths `manifest.yaml` and `raw-result.json`, and the `random-m2` request member plus its matching satisfying root in `planted_witnesses.json`. I found no contradictory archive-member digest or duplicate path for P1. These artifacts break the false output-complete and no-solution conclusions; they do not establish or refute candidate copy custody, which is assigned elsewhere.

## Command and inference details; limits

Read-only commands used: `git rev-parse HEAD`, `git status --short`, exact `test -e` checks for the two required outputs and two peer paths; `python3` standard-library `hashlib`, `gzip`, `json`, `tarfile`, `collections`, and `datetime` scripts over the five listed original files; and a read-only `sqlite3` exact-session row lookup for admission. The archive script iterated members in tar order, compared tar-declared size with extracted byte length, and counted names. The trace script parsed each JSONL line and selected its explicit terminal fields. The equation script used Python integer modular arithmetic and `pow(denominator, -1, p)` for affine addition. No solver, experiment, producer checker, or independent replay trial was run.

P1 verifies only the original archive's internal inventory and original public request match. It cannot verify candidate copy custody, Git anchors, or absence of other files in the historical run tree. P2 verifies the witnessed planted systems and the two required-path absence checks; it does not prove natural relation yield, useful rank, solver termination, success probability, cold setup, online work, linear algebra, extraction, or a matched-rho gap. Those cost terms are null or unmeasured here. The three positive timeouts remain censored; the monitor error remains infrastructure, not mathematical evidence.

Procedure deviations from the frozen blind scientific method: **none**. For administrative transparency, a later read-only `conductor check` reported overlap with the already claimed task T-4458 itself, and a redundant `conductor task claim` returned `task already claimed`; neither changed the original session-bound fence or supplied a scientific value. The review plan's requested matching completed release is outside this handoff's explicit instruction: no release, commit, or push was created here. Coordinator sealing and cross-review comparison remain outstanding.
