# Drafting brief: PQC idea + experiment drafts (JSON only)

You are an elite lattice/code/hash-based cryptanalyst drafting research proposals for the
crypto-autoresearcher repo (/home/user/crypto-autoresearcher). You write ONE JSON file and nothing else.
Do not edit the repo. Do not run experiments.

## Inputs to read first
- Existing proposals to AVOID duplicating: <scratchpad>/existing_titles.txt (id|RQ|title) and
  <scratchpad>/existing_pqc.txt (titles + claims). A new idea must differ in tracked object or mechanism,
  not just wording. If close to an existing one, either pick a different idea or cite it under
  `related_internal` with a clear delta.
- Literature corpus list: <scratchpad>/kn_pqc.txt (KN-LIT ids). You may cite a KN-LIT id in
  `nearest_prior_art[].ref` ONLY after opening knowledge/literature/<ID>.md and confirming its topic;
  those get provenance "kb". Anything from memory gets ref null, provenance "recalled", and a
  `citation_text` (authors, title, venue/year, hedged). Never invent a KN id.
- The research question records in ledger/questions/<RQ>.yaml for your lane (read them).
- Rules of the house: AGENTS.md "Core rules"; agents/idea-generator.md (schema intent).

## What makes a good idea here
- Falsifiable, with a discriminating minimal test that is RUNNABLE AT REDUCED SCALE on a laptop/
  single node (toy/medium dimensions, reduced parameters) with an explicit transfer assumption.
- Every experiment has: a negative/null control (matched random object), a positive control where the
  effect must appear (planted structure), and an A/A comparison (same arm twice, differing only in a
  nuisance factor such as seed or run order) to set the noise floor.
- Exponent-first ambition where honest; otherwise say it is a constant/measurement/defensive result.
- No attack on deployed systems or real keys; reduced-parameter and self-generated instances only.
- Mix of classes: mechanism, algorithm, representation, measurement, composition, control, tooling.
- Be concrete: name dimensions, moduli, block sizes, sample counts, tools (fpylll, G6K, SageMath,
  lattice-estimator, PQClean/liboqs reference code, NumPy), exact statistics.

## Output: a JSON array of exactly N objects, written to <scratchpad>/drafts/<LANE>.json
Each object (all string fields plain text, no markdown; keep each string under ~900 chars):
{
 "question_id": "RQ-...",              // one of your lane's RQs
 "title": "<= 140 chars",
 "class": "mechanism|algorithm|representation|measurement|composition|control|tooling",
 "claim": "falsifiable statement, 2-5 sentences",
 "mechanism": "why it would work, 3-6 sentences",
 "tracked_object": "the exact object measured",
 "predictions": [ {"id":"P1","metric":"name","direction":"higher|lower|different",
                   "minimum_effect":"quantitative threshold","falsified_by":"observation"} ],   // 2-3
 "minimal_test": {"design":"...","controls":["null/negative control","positive control","A/A"]},
 "falsification_conditions": ["..."],
 "confounders": ["..."],
 "interpretation_limits": ["... (must include the scale/transfer limit)"],
 "heuristic_assumptions": [ {"id":"H1","statement":"...","rigorous_support":"...","validation_plan":"..."} ],
 "target_complexity": {"time_exponent":"...","memory_exponent":"...","best_known":"...",
                       "hidden_overhead":"...","tradeoff_note":"..."},
 "nearest_prior_art": [ {"ref":"KN-LIT-xxx or null","provenance":"kb|recalled",
                         "citation_text":"...","relation":"same|special_case|generalizes|adjacent|orthogonal",
                         "delta":"what this adds"} ],     // >=1
 "related_internal": ["IDEA-... ids from existing_titles.txt this builds on or must be deduplicated against"],
 "estimated_cost": {"implementation":"low|medium|high","compute":"low|medium|high"},
 "recommended_priority": "low|medium|high",
 "experiment": {
   "title": "...",
   "objective": "what uncertainty one run reduces",
   "instrument": "language, libraries, harness",
   "parameters": "exact reduced-scale parameters and sample counts",
   "procedure": "numbered stages",
   "independent_variables": [ {"name":"snake_case","levels":["..."]} ],
   "nuisance_factors": [ {"name":"snake_case","treatment":"fixed|randomized|crossed|measured","value":"...","how":"..."} ],
   "comparisons": [ {"id":"C1","arms":["..",".."],"differs_in":["<one independent var name>"],"design":"one_factor"},
                    {"id":"C2","arms":["..."],"differs_in":[],"design":"absolute"},
                    {"id":"AA1","arms":["X seed-block A","X seed-block B"],"differs_in":["<one nuisance factor name>"],"design":"aa"} ],
   "primary_metrics": ["..."], "secondary_metrics": ["..."],
   "preregistered_prediction": {"quantity":"...","formula":"...","source":"..."},
   "scale_tier": "toy|medium|crypto", "scale_justification": "tested params + transfer assumption",
   "seeds_count": 3,
   "budget": {"wall_clock_seconds_per_run": 3600, "total_cpu_hours": 4, "maximum_memory_gb": 8, "maximum_runs": 12},
   "stopping_rules": ["..."], "invalidation_rules": ["timeout/crash is failed_infrastructure, never negative evidence", "..."],
   "success_criterion": "decidable, cites comparison ids (C1..) and prediction ids (P1..)",
   "falsification_criterion": "different text from success, cites ids",
   "decision_impact": {"on_positive":"...","on_negative":"... (must differ)"},
   "required_artifacts": ["manifest.yaml ...","raw-result.json ...","..."]
 }
}
HARD SCHEMA RULES for comparisons (a validator enforces them):
- every name in differs_in must be an independent_variables name or a nuisance_factors name;
- one_factor: exactly one name in differs_in; absolute: differs_in is []; factorial: >=2 names, each an
  independent variable or a nuisance factor with treatment "crossed"; aa: exactly ONE nuisance factor name
  (never an independent variable). Always include at least one aa comparison.
- success_criterion and falsification_criterion must cite only one_factor/factorial/absolute comparison
  ids (an aa id only as "noise floor"), and must not be the same text.
- decision_impact.on_positive != on_negative.
Validate your file with: python3 -c "import json;d=json.load(open('<path>'));print(len(d))"
Return to the caller only: the path, the count, and a one-line title list. No other prose.
