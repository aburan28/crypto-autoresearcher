**Independent software review — TASK-20261031-60575a**

The reviewed builders preserve the prescribed symbolic rationality equations and signed outputs on the fixed controls. One independent suite invocation produced **73 passing rows and one failing row**. Every prescribed chart, guard, nilpotent fixture and mandatory mutation passed. The failure is an additional deterministic test of outer chart arity: the guarded candidate checker accepts a self-inconsistent `k` tag when both copies of the outer tag are changed together. That finding limits the standalone chart checker; it does not change the checked field equations or F1 multiplicities.

The review is against commit `4a74af1ffe4621cb21fb889001bd19e6250af4c4`. The thirteen scientific input paths have exact UTF-8 snapshots and SHA-256 hashes in `independent-results.json`. All thirteen hashes were identical before and after the suite, and the scoped tracked Git status was empty. The producer modules were not edited.

| Joint | Judgment | Concrete evidence and scope |
| --- | --- | --- |
| `symbolic_circuit` | **holds** | Reviewer coefficient algebra compared every equation, ordered input/auxiliary list and label of the exported fixed blocks to a separately expanded symbolic identity. All coefficients of U, A and B remain variables. Nilpotent k=0..5 counts are 0,3,9,15,21,36; guard is 10 auxiliaries/12 equations; slack is 9/8. Total field-polynomial degree is at most two. |
| `rationality_predicates` | **holds** | All eight literal nilpotent fixtures and all eight literal guard fixtures agree with independent polynomial arithmetic; the eight corresponding fixed slack assignments also agree with their own slack equation. The repeated-branch control distinguishes nonzero C²−f from its zero nilpotent power. Splitting is checked separately through the interval witness, including an explicitly rejected corrupted witness. |
| `signed_fidelity` | **holds** | Thirteen valid original chart fixtures pass each of the three candidate arms and the separate Euler reference; the two impossible original fixtures explicitly reject construction. Reviewer-authored local series and independently factored A/B give the expected signed multiplicities. Both F1 beta values 1 and 4 recover 4(0,1)+(0,4); swapped and balanced substitutions reject. |
| `strict_assignment` | **breaks** | Every prescribed malformed assignment, coefficient, projection, field and stratum mutation rejects. Additional row `mutation/inconsistent_outer_k` shows that a linear-B guarded chart with degree-4 U and four recovered points accepts outer k=3 when w.k and candidate.chart.k are changed together. A caller that first validates w with the frozen reference excludes this input; the candidate checker alone does not enforce that invariant. |
| `fixed_execution` | **holds** | The full reviewer-authored fixed suite ran once after a successful checkpoint gate, under a 240-second watchdog and 2 GiB address-space limit. All rows, the failing assertion, full stdout/stderr, exact command, source snapshots and hashes are retained. This judgment concerns execution completeness and custody, not a claim that every assertion passed. |
| `claim_boundary` | **holds** | The reviewed source constructs witnesses from supplied relations and known points. It does not search for an unknown relation. The degree result is a field-generator degree, not Boolean encoding degree, solving degree or regularity. These finite controls do not establish complete projected SAT coverage, performance, novelty or universal chart completeness. |

The per-joint judgments are inputs to the Coordinator. They do not preaccept a native review gate or change an official scientific status.

**The arity counterexample.** Start with the frozen `finite_four` fixture over F5 on y²=x³+1, target (0,1), interval t=0,s=1, and four copies of (0,1). Its normalized chart is A=−X, B=X, U=X⁴, k=4. Construct the guarded candidate from this supplied valid chart, then change only `w['k']` and `candidate['chart']['k']` to 3. The candidate block still has its original six inputs, ten auxiliaries and twelve equations. `check_candidate_chart` returns `status: valid` and `[[0,1],[0,1],[0,1],[0,1],null]`.

The source cause is concrete: `checker.py:125` validates shape using U, `checker.py:126-127` compares the two outer identity records, and `checker.py:137` sets the local guard/slack degree to `None`. The function does not require the outer k to be an integer equal to `len(U['coeffs'])-1`. The frozen reference has that degree check at `check_chart.py:72`; its rejection of this mutated case was not separately executed, and no such runtime result is claimed here. The required repair is to check outer k against U before choosing a stratum, with the same type/range discipline as the reference. Keep the failing fixture for a fresh review of that change. This test changes the purported source chart as well as its binding, so it demonstrates a missing standalone shape check, not a failure to compare an otherwise trusted external chart to a candidate.

**Independent derivation and arithmetic.** `test_independent.py` does not use the producer's arithmetic to determine expected polynomial coefficients, nilpotence, local orders or signed multiplicities. Its `Symbolic` coefficient algebra, `independent_ir` evaluator, modular polynomial functions and local-series routine were authored for this review. The driver imports the reviewed modules only to obtain their outputs and acceptance decisions. The producer's own tests, results, README, snapshot receipt, previous theory reports, resume drafts and sibling reviews were not read.

For a modular multiplication at degree k, the reviewer expands coefficient d of

    L R − P − U Q = 0,       0 <= d <= 2k−2.

There are 2k−1 coefficient equations, k remainder variables except in a final-zero product, and k−1 quotient variables. The terms U_i Q_j remain symbolic even when a fixed assignment gives U_i=0. Each coefficient comparison checks the full polynomial, including those terms, rather than only its value on a fixture. A fixture-specialized copy is rejected by the reviewer comparison with `full coefficient expansion differs`.

The low-degree reductions are separate obligations. At k=1 the auxiliaries C0,v,F satisfy v=u0², F=−u0v−a u0+b, and C0²=F. At k=2, division of f by monic U introduces q,F1,F0 and the three equations q+u1=0, F1+u0+u1q−a=0, F0+u0q−b=0. Together with C, the square product and final-zero product, this gives nine auxiliaries and nine equations. For k=3,4,5 the preserved multiplication chains have three, three and four modular products respectively, giving r(2k−1)=15,21,36 auxiliaries and equations. The k=0 block is empty. These are structural counts from the unspecialized equations.

The literal repeated-branch control has p=5, a=1, b=0, U=X² and C=0. Here C²−f is −X modulo U, not zero, while its square is zero. Both the independent evaluator and candidate accept the nilpotent condition. The guard control with c=2,F=3 has e=0,u=3,beta=0 and accepts even though F is a nonsquare; when c=0 the guard forces e=1,u=0 and beta²=F. Slack fixtures are evaluated under beta²=F+cu with their actual deterministic slack assignments; guard validity flags are not reused as slack expectations.

Expected A/B coefficients for the thirteen valid original charts were factored independently in `EXPECTED_AB`. Expected signed multisets come from the literal supplied points, while a separate local-series computation verifies their multiplicities in A+B y, including the negative target point. This covers B=0, repeated ordinary roots, branch roots, characteristic-five multiplicity, wrapped support, target overlap and the target outside the interval. It does not enumerate roots or relations.

For F1, at (0,1), y−1 has order 3 in x and X(y−1) has order 4. At (0,4), the same function has order 1. The independently recovered expectation is therefore four copies of (0,1) and one of (0,4). Both explicit guard beta assignments satisfy the field equations and have the same normalized outer chart. The signed recovery uses the residual ratio for the positive excess, so neither auxiliary beta determines that excess sign.

**IR trust boundary.** `check_assignment` is a parser and evaluator of the equations it receives. It checks canonical values, names, counts, metadata, degrees and residuals, but does not itself compare the supplied equations to the canonical polynomial for `kind`. In the fixed specialization control it accepts the specialized equations, while the independent exact-symbolic comparator rejects them. The original builder output passes that comparator. Thus the frozen builder/output hash and the independent coefficient audit matter; successful evaluation of arbitrary supplied IR is not proof that it encodes the named rationality block. This is a documented boundary, not a claim of additional measured solver behavior.

**Execution and retained attempts.** The first invocation of the review recording wrapper was `python3 -B research/prime_sat_rationality_software_20261031/TASK-20261031-60575a/test_independent.py --record`. Its checkpoint operation started at 08:43:24 UTC and reached the wrapper's 60-second infrastructure watchdog at 08:44:24 UTC with no stdout/stderr and no terminal gate result. No suite launched. The wrapper's printed key `checkpoint_refused` describes that wrapper stop; it was not an actual policy refusal by the gate. The result record preserves that distinction.

The Coordinator reconciled process state and authorized one fresh gate attempt with an 1800-second gate-only watchdog because the initial Git scan takes minutes in this worktree. The exact infrastructure message and original wrapper source are retained. Only the two gate timeout literals changed; scientific assertions and the 240-second/2 GiB suite limits did not change. The second gate ran from 08:45:56 to 08:57:55 UTC and returned zero, with stdout naming:

    s3://setec-astronomy-artifacts/checkpoints/crypto-autoresearcher/codex__prime-active-support-implementation-20261030/20261031T085008Z-4a74af1ffe46/

That is the gate's recorded output; this reviewer did not independently read back the remote checkpoint. No gate refusal was bypassed.

The suite command was:

    /usr/bin/python3 -B /home/ec2-user/crypto-prime-sat-ideas-20261029/research/prime_sat_rationality_software_20261031/TASK-20261031-60575a/test_independent.py --suite

The recording envelope began at 08:57:55.934633 UTC and ended at 08:58:03.653364 UTC, including Git metadata collection. The measured child-process duration was 0.217421699 seconds and peak resident set was 22,692 KiB under Python 3.9.25 on Linux x86_64. These values document the watchdog/resource envelope; they are not a timing comparison or performance claim. The process returned 1 because the added outer-k rejection assertion failed. It was not rerun.

| Fixed evidence group | Rows | Outcome |
| --- | ---: | --- |
| Literal nilpotent fixtures | 8 | 8 pass, including declared invalid fixtures explicitly rejected |
| Symbolic nilpotent degrees k=0..5 | 6 | 6 pass |
| Literal guard fixtures | 8 | 8 pass |
| Fixed slack assignments using the prescribed c,F,beta values | 8 | 8 pass |
| Original chart fixtures | 15 | 13 valid across three candidate arms; 2 explicit construction rejections |
| F1 both-root regression | 1 | Both beta assignments and independent signed expectations pass |
| Block mutation controls | 19 | 19 explicit rejections |
| Chart mutation controls | 7 | 6 explicit rejections; additional inconsistent outer k accepted |
| Fixture-specialization negative control | 1 | Reviewer symbolic comparator rejects |
| Source custody | 1 | All thirteen input hashes unchanged |

There were 41 candidate chart assignments: 39 for the original valid charts and two F1 guard assignments. The checker recorded 42 `candidate_chart_check` events because the malformed outer-k example was also accepted. The 15 `full_reference_chart_check` events are retained separately. All event names and counts are stored by module without adding unlike event units together. Scientific runs, solver instances, coefficient/field censuses, benchmarks and remote research jobs are zero.

The review's scientific read scope is precisely the frozen handoff's thirteen inputs. Governance reads, the actual initial prompt, literal paths and hashes, all attempt records and runtime unknowns are listed in `attestation.yaml` and `independent-results.json`. The supplied API and contract are the source review for this software-fidelity task; excluded earlier reports were not used as authority, and no novelty or literature-completeness claim is made.

Actual model, provider, tier, effective effort and context/output capacity are unauthenticated under the prospective inference amendment. Requested `review-adversarial`/`xhigh` is recorded as a request, not a verified runtime fact. Root retains Git, queue, claims, report rendering, archival and official decision authority. The four assigned outputs are sealed for that archive; this report does not declare an archival commit or an accepted native review gate.
