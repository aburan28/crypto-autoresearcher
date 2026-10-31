import json
inst = lambda extra=None: {"repo":"crypto-autoresearcher","commit":None,"build":[["cargo","build","--release","--bin","koblitz_analogue_rho"]],"binary_sha256":None,"flags":{},"env":{"RAYON_NUM_THREADS":"1"},"threads":1}
def arm(id,role,desc,params,same=None):
    a={"id":id,"role":role,"description":desc,"instrument":inst(),"parameters":params}
    if same: a["same_instrument_as"]=same
    return a
prov=lambda path,meas:{"written_at":"2026-10-31","data_seen":[{"path":path,"measured":meas}],"sample_status":"out_of_sample"}
probe="scratchpad designs/koblitz-analogue/probe/ (construction existence only, no cost data)"
P={
"schema":"experiment.protocol/v1","protocol_id":"DESIGN-koblitz-analogue-cm7-orbit-rho","version":1,"created":"2026-10-31",
"repository":"crypto-autoresearcher","study_dir":"research/koblitz_analogue_cm7_rho_<date>",
"authors":["design agent (unfrozen draft for Coordinator)"],
"links":{"lead":"LEAD-STR-small-cm-disc-nonunit-endo","related_leads":"LEAD-STR-glv-gls-isogeny-loop-scalar-mult; LEAD-RHO-non-automorphism-equivalence; LEAD-STR-automorphism-quotient-rho; LEAD-RHO-automorphism-class-walks; LEAD-RHO-matched-rho-calibration","known_results":"KR-RHO-482ed3; KR-RHO-fb88e6; KR-RHO-825bca; KR-RHO-0528e7","idea_record":"report Candidate 3 (family-B-module.md) and C2 (family-A-arithmetic.md)","note":"Design only, mathematical research on toy prime-field curves with planted logs; no secret scalar, no deployed key. Not frozen, not approved."},
"question":"On toy prime-field curves with CM by Z[(1+sqrt(-7))/2] whose degree-2 endomorphism alpha has multiplicative order h on the prime-order subgroup G (so rho can walk on classes {+-alpha^i P}), does the sqrt(h) iteration saving survive as a total counted-cost saving against matched negation-map rho once every orbit canonicalisation is charged, or is it a net loss?",
"claims":[
 {"id":"C1","text":"Each constructed curve satisfies #E=4*l (l prime=|G|), alpha^2-alpha+2=0 on G, and ord_l(lambda)=h exactly; every planted log is recovered and verified (exact computation).","class":"exact_computation","decided_by":[]},
 {"id":"C2","text":"Class walks on <+-alpha> cut walk iterations against matched negation rho by about sqrt(K/2), K=|<lambda,-1>| (heuristic estimate, calibration of the class mechanism).","class":"heuristic_estimate","decided_by":[]},
 {"id":"C3","text":"The total counted cost (canonicalisation charged) of the cheaper alpha-class arm exceeds matched negation rho on these curves, with the pooled ratio's 95% lower bound above 1.","class":"comparative","decided_by":["C-cost"],"if_supported":"measured closure of LEAD-STR-small-cm-disc-nonunit-endo's revisit_when for this construction: constants kappa and ratio-vs-h recorded; scope is prime-field CM-7 curves with 2^18<=l<2^34 only","if_not_supported":"if the pooled upper bound is below 1 the closure is falsified for this family and the lead reopens; otherwise the ratio is not separated from 1 and nothing is claimed"},
 {"id":"C4","text":"The j=0 automorphism-class positive control reproduces a net counted gain against negation rho through the same code path.","class":"comparative","decided_by":["C-pos"],"if_supported":"the class machinery and its charging can detect a real net gain","if_not_supported":"a null on the alpha-curves is invalid, not null"}],
"hypotheses":[{"id":"H1","statement":"H0: pooled geometric-mean total counted cost ratio (best alpha-class arm / matched negation rho) is >= 1 (net loss or no gain). H1: it is < 1 at some h, i.e. a canonicaliser costing o(h) exists in practice. Predicted outcome: H0, ratio about 1.2-2 times sqrt(h) (about 4-10 at h=19-23, larger at larger h).",
 "mechanism":"Iterations fall by sqrt(K/2) (KR-RHO-482ed3 mechanism with a degree-2 CM endomorphism). Each step must enumerate h-1 further alpha images (each a degree-2 map, about 6-9 field multiplications) to pick a class representative, against about 7 field-multiplication equivalents for the step itself; break-even needs alpha-evaluation cost below about 1/(sqrt(h)+1) of a step (about 1.2 M at h=19), which a degree-2 rational map cannot reach.",
 "predictions":[
  {"id":"P1","metric":"iter_ratio","direction":"lower","minimum_effect":"walk-step ratio (alpha-class over negation) within 15% of (K/2)^(-1/2) per curve, e.g. 0.23 at h=19; absent saving means a mis-implemented class walk (invalid run)","provenance":prov(probe,"existence of curves and orders only; no iteration or cost data"),"role":"calibration"},
  {"id":"P2","metric":"fme_total","direction":"higher","minimum_effect":"pooled ratio of total counted cost (best alpha-class arm over negation rho) > 1 with the 95% lower bound > 1; central prediction 4-10 at h=19-23, scaling about as sqrt(h)","provenance":prov(probe,"existence of curves and orders only; no iteration or cost data"),"role":"decisive"},
  {"id":"P3","metric":"fme_total","direction":"lower","minimum_effect":"j=0 order-6 class arm total cost ratio over negation rho between 0.50 and 0.85 (iteration ratio 0.577 plus about 5-15% canonicalisation)","provenance":prov("knowledge/frontiers/ecdlp/generic-rho/KR-RHO-0528e7.yaml","published factor 0.790*sqrt(6) vs plain on BN254; not data from this construction"),"role":"calibration"}]}],
"arms":[
 arm("rho-neg","reference","Matched negation-map rho: classes {+-P}, r-adding walk, same walk/DP/escape code as every arm, orbit list [id].",{"orbit":"neg","curves":"alpha-curves"}),
 arm("rho-neg-aa","control_aa","rho-neg repeated under a second arm label with an independent walk-seed stream: noise floor of the ratio statistic.",{"orbit":"neg","curves":"alpha-curves"},"rho-neg"),
 arm("rho-alpha-affine","baseline","alpha-class rho, naive canonicaliser: orbit {+-alpha^i X} by affine full-point alpha (one inversion per image, no batching), min-x representative.",{"orbit":"alpha","canon":"affine_full_point","curves":"alpha-curves"},"rho-neg"),
 arm("rho-alpha-batched","candidate","alpha-class rho, cheapest honest canonicaliser (a): x-only projective alpha chain with y tracked, one batch inversion per orbit to normalise, min-x representative.",{"orbit":"alpha","canon":"xonly_projective_batch_norm","curves":"alpha-curves"},"rho-neg"),
 arm("rho-alpha-crossmul","candidate","alpha-class rho, cheapest honest canonicaliser (b): same chain, min-x found by projective cross-multiplication (2 M per comparison, no normalisation inversion). Decision uses the cheaper of the two candidate arms per curve.",{"orbit":"alpha","canon":"xonly_projective_crossmul","curves":"alpha-curves"},"rho-neg"),
 arm("j0-aut6","control_positive","Positive control: matched-N j=0 prime-order curves, classes <+-1,zeta> of size 6 (x-> omega*x), same walk code; known net gain against negation rho.",{"orbit":"aut6","curves":"j0-controls"},"rho-neg"),
 arm("j0-neg","reference","Negation rho on the j=0 control curves (reference for the positive control).",{"orbit":"neg","curves":"j0-controls"},"rho-neg"),
 arm("generic-trivial","control_negative","Negative control: generic-discriminant matched-N prime-order curves, alpha-class code path configured with the orbit list [id] (no class structure exists), against negation rho on the same curves: ratio must be 1.",{"orbit":"id_via_alpha_code","curves":"generic-nulls"},"rho-neg"),
 arm("generic-neg","reference","Negation rho on the generic matched-N curves (also checks that CM-7 curves are not cheaper for plain negation rho than generic curves of the same N).",{"orbit":"neg","curves":"generic-nulls"},"rho-neg")],
"controls":{
 "aa":{"present":True,"comparison":"C-aa","not_applicable_reason":None},
 "positive":{"present":True,"arm":"j0-aut6","expected_detection":"total counted cost ratio j0-aut6/j0-neg in [0.50,0.85] with the 95% interval excluding 1 at each of 5 sizes","not_applicable_reason":None},
 "negative":{"present":True,"arm":"generic-trivial","null_population":{"description":"generic-discriminant prime-order curves with the same l bit length as each alpha-curve; no endomorphism is used and the alpha-class code path runs with orbit list [id], so the cost ratio against negation rho must be 1 within the A/A interval","generator":"setup-domain stream: random (a,b) over a prime p of the bit length of the matched alpha-curve's p, point count by PARI ellcard, keep the first with prime order l of the matched bit length","n":45,"why_n":"one matched curve per alpha-curve so the null ratio distribution has the same cluster structure as the decisive statistic","matched_on":["bit length of l","bit length of p","walk shape r, W, d rule","cost weights","binary and code path","200 planted targets per curve"]},"not_applicable_reason":None}},
"variable_ledger":{
 "independent":[{"name":"orbit/canonicaliser","levels":["neg","alpha_affine","alpha_xonly_batch","alpha_xonly_crossmul","aut6 (control)","id_via_alpha_code (null)"]}],
 "factors":[
  {"name":"curve (p,l,h,K,m)","treatment":"fixed","value":"45 alpha-curves from the frozen gp enumeration (probe_cofactor_wide.gp), one per (l,conjugate) with 2^18<=l<=2^34 and 16<=h<=110, first (m,mu,sign) in script order","how":"generator script hash recorded; curve list frozen with the protocol"},
  {"name":"targets","treatment":"randomized","how":"200 planted logs per curve from SHA-256(protocol_sha256||'target'||curve||index), independent of arm; every arm sees the same 200"},
  {"name":"walk_seed","treatment":"randomized","how":"SHA-256(protocol_sha256||'walk'||curve||target||arm_label); separate RNG domain from target and setup (as the m=51 rho.c)"},
  {"name":"walk shape","treatment":"fixed","value":"r=32 jumps u_j*P+v_j*Q, W=8 parallel walks, DP trailing zeros d=floor(log2(0.05*E_steps/W)), same cycle policy (look-ahead + 16-point window + doubling escape) in all arms","how":"one code path; only the orbit list differs"},
  {"name":"cost-unit weights","treatment":"fixed","value":"FME=M+S+20*I; adds and mod-l ops uncharged but recorded","how":"frozen; sensitivity w_I in {8,40}, add=0.2 M, mod-l mul=1 FME reported, decision must hold at all"},
  {"name":"class size K","treatment":"measured","how":"computed per curve (|<lambda,-1>|, h or 2h); enters the predictions, not a tuning knob"},
  {"name":"binary and build","treatment":"fixed","value":"one binary sha256 pinned","how":"single build for all arms"},
  {"name":"threads","treatment":"fixed","value":1,"how":"single-threaded rows; a 4-core host runs 4 rows concurrently, no clock is read"},
  {"name":"arm_order","treatment":"randomized","how":"rows interleaved; counts are order-independent, order is shuffled by seed anyway"},
  {"name":"host_load","treatment":"measured","how":"recorded per row, affects no counted metric"}],
 "comparisons":[
  {"id":"C-cost","arms":["rho-neg","rho-alpha-batched"],"differs_in":["orbit/canonicaliser"],"design":"one_factor"},
  {"id":"C-cost-xmul","arms":["rho-neg","rho-alpha-crossmul"],"differs_in":["orbit/canonicaliser"],"design":"one_factor"},
  {"id":"C-naive","arms":["rho-neg","rho-alpha-affine"],"differs_in":["orbit/canonicaliser"],"design":"one_factor"},
  {"id":"C-aa","arms":["rho-neg","rho-neg-aa"],"differs_in":[],"design":"aa"},
  {"id":"C-pos","arms":["j0-neg","j0-aut6"],"differs_in":["orbit/canonicaliser"],"design":"one_factor"},
  {"id":"C-null","arms":["generic-neg","generic-trivial"],"differs_in":["orbit/canonicaliser"],"design":"one_factor"}],
 "aa_not_applicable":None,"crosses_map":False},
"randomization":{"arm_order":"interleaved","arm_order_reason":None,
 "seed_derivation":{"method":"protocol_hash_sha256","seeds":[],"nonce":None,"note":"all seeds are SHA-256(protocol_sha256 || domain || curve_id || target_index [|| arm_label for the walk domain]); domains setup, target, walk are separate; the curve list and control-curve choice use the setup domain only"},
 "instance_sampling":{"rule":"alpha-curves: all curves from the frozen enumeration (no sampling); 200 targets per curve; j=0 and generic controls: for each of the 5 sizes {20,22,24,26,28} bits and for each alpha-curve bit length, first prime-order curve from the setup-domain stream","independent_of_arm":True},
 "blinding":{"analysis_labels_masked":False,"how":"not masked: arms differ by orbit code and are identifiable from counts; the analysis script and the decision rule are frozen before data","unmasked_at":None}},
"sample_size":{"instances":45,"replicates":1,"warmups":0,
 "power":{"method":"paired_bootstrap","alpha":0.05,"tests_in_family":3,"correction":"bonferroni","rank_test_n":9999,"min_attainable_two_sided_p":0.0002,
  "passes":True,
  "note":"B=9999 bootstrap/permutation resamples: min p 2/(9999+1)=2e-4 < alpha/m=0.05/3=0.0167. Three family tests: pooled C-cost, pooled C-pos, pooled C-null. Per curve 200 targets give a ratio-of-sums standard error of about 5% (Rayleigh-like cost, CV about 0.52, so SE about 3.7% per arm and about 5% for a paired ratio), against a predicted effect of ratio 4-10 versus a falsifying 0.9: separation of ratios near 1 from 0.9 needs about 5%, which 200 targets provide. 45 curves are clustered, not pooled as independent targets."},
 "preflight_runtime":{"fixed_seconds":60,"per_sample_seconds":0.02,"threads":1,"estimated_total_seconds":5400,"measured_on":"arithmetic estimate only, NOT measured: about 2e7 field operations per negation solve at l=2^26, about 4e8 for the affine arm; to be replaced by a one-call-per-arm timing before freeze"}},
"metrics":{"primary":[
 {"id":"fme_total","name":"total counted cost","unit":"FME (field-multiplication equivalents)","kind":"counted","definition":"from the first target-dependent operation (Q's doubling table, jump table, walk starts) through every walk step, look-ahead addition, canonicalisation (each alpha image, each normalisation or cross-multiplication, each y update), DP check, cycle escape, collision resolution and the final [k]P=Q verification: FME = M + S + 20*I, incurred by the instrumented field type, nothing uncharged except add/sub/negate and mod-l integer ops which are counted in counters","source":"rows.jsonl cost.fme_total","aggregation":"paired_ratio","resolution":"1 FME","uncertainty":"paired_bootstrap_ci95"},
 {"id":"iter_ratio","name":"walk-step ratio","unit":"steps","kind":"counted","definition":"walk steps (excluding look-ahead and escapes) until the collision that solves the target","source":"rows.jsonl counters.steps","aggregation":"paired_ratio","resolution":"1 step","uncertainty":"paired_bootstrap_ci95"}],
 "secondary":[
 {"id":"kappa_step","name":"canonicalisation share per step","unit":"FME per step","kind":"derived","formula":"kappa_step = canon_fme / steps","definition":"(canonicalisation FME) / steps, per arm and curve; with c_alpha and c_step the measured per-image and per-add FME","source":"rows.jsonl cost.canon_fme and counters.steps","aggregation":"median","resolution":"0.1 FME","uncertainty":"bootstrap_ci95"},
 {"id":"fme_walk_only","name":"walk-only cost","unit":"FME","kind":"counted","definition":"fme_total minus setup and starts, reported to separate finite-size setup dilution at small l","source":"rows.jsonl cost.walk_fme","aggregation":"paired_ratio","resolution":"1 FME","uncertainty":"paired_bootstrap_ci95"},
 {"id":"verified_fraction","name":"verified fraction","unit":"fraction","kind":"exact","definition":"rows whose recovered k satisfies [k]P=Q checked by the independent checker","source":"checker output","aggregation":"mean","resolution":"1/n","uncertainty":"clopper_pearson_ci95"}]},
"measurement":{"isolation_required":"none","warmups":0,"order":"randomized","clock":"counted",
 "counters":["steps","lookahead_adds","escape_doublings","alpha_images","normalisation_inversions","crossmul_compares","dp_checks","field_ops.muls","field_ops.sqrs","field_ops.invs","field_ops.adds_uncharged","mod_l_ops_uncharged","point_adds","point_doubles","scalar_mults"],
 "record":["binary_sha256","cpu_model","kernel_release","threads","curve_uid","p","l","h","K","m","setup_seed","target_seed","walk_seed"],
 "timed_primary_justification":None},
"execution":{"backend":"local","queue":"local 4-core host, one row per core","placement":{"instance_type":"any 4-core x86_64","cpus":4,"spot":False},"measurement_class":"throughput","timeout_seconds":1800,
 "checkpoint":{"policy":"none","interval_seconds":None,"grace_seconds":None,"restore_validation":"none","after_restore":{"wall_time":"invalid","counted_units":"valid"}},
 "retries":{"infrastructure_only":True,"max_attempts":1}},
"stopping_rules":[
 {"rule":"fixed design: 45 alpha-curves x 5 arms x 200 targets, plus 5 j=0 sizes x 2 arms x 200 and generic nulls (one per alpha-curve bit length) x 2 arms x 200, then stop; no targets added after a look","kind":"fixed_n","preregistered":True},
 {"rule":"a row hitting the step cap (20 x expected steps) or failing verification is recorded as not_completed / wrong_answer and kept; the cap is the same multiple for every arm","kind":"invalidation","preregistered":True}],
"invalidation_rules":["a curve failing C1 (#E=4l, alpha identity, exact ord_l(lambda)=h, canonicaliser equal to slow orbit enumeration on 1000 points) is dropped before any walk and reported","an arm whose iter_ratio is not within 15% of (K/2)^(-1/2) on a curve is a mis-implemented class walk: the curve's cost row is invalid, not evidence","a row below verification is excluded from cost ratios and counted in the CONSORT flow"],
"decision_rule":{
 "text":"Per curve, ratio = sum of fme_total over the 200 targets for the cheaper candidate arm (rho-alpha-batched or rho-alpha-crossmul) divided by that for rho-neg. Preconditions (C-aa is a precondition, not a decider): the A/A ratio interval contains 1; the null arm generic-trivial/generic-neg ratio interval contains 1; the positive control ratio lies in [0.50,0.85] with its interval excluding 1; P1 holds on at least 90% of curves. Given preconditions: (i) CLOSURE CONFIRMED (C3 supported) if the pooled geometric-mean ratio over the 45 curves has a 95% cluster-bootstrap lower bound > 1; (ii) LEAD REOPENED if that pooled upper bound < 1, or if any curve with h <= 24 has an upper bound < 0.9 that holds at all sensitivity settings (w_I 8/40, add 0.2 M, mod-l mul 1 FME); (iii) otherwise inconclusive. If any precondition fails the verdict is invalid_measurement, never a null.",
 "comparison_ids":["C-cost","C-cost-xmul","C-pos","C-null"],
 "threshold":"pooled lower bound > 1 (closure), pooled upper bound < 1 or h<=24 curve upper bound < 0.9 (reopen)",
 "statistic":"geometric mean over curves of per-curve ratio of summed fme_total (paired by target)",
 "interval":"two-level bootstrap, 95%, B=9999: resample curves, then targets within curve",
 "multiple_comparison_correction":"bonferroni",
 "effect_size_measure":"pooled ratio, ratio versus h (log-log slope with 95% interval, prediction about 0.5 plus), and measured kappa_step",
 "verdict_vocabulary":["supported_within_scope","falsified_reopen","within_control_distribution","invalid_measurement","inconclusive"]},
"analysis_plan":{"script":None,"inputs":["rows.jsonl","curves.json","checker_report.json"],"outputs":["per-curve ratios table","pooled ratio with CI","log ratio vs log h slope","kappa_step table","A/A, positive and null control intervals","sensitivity table"],"blinded":False,"frozen_before_data":False},
"reporting":{"export_schema":"experiment.export/v1","review_schema":"experiment.review/v1","graphs":["total-cost ratio versus h with the A/A band and the predicted curve","iteration ratio versus predicted (K/2)^(-1/2)","cost share by phase per arm"],"report_dir":"reports"},
"inadmissible":[
 "changing the curve list, targets, seeds, cost weights, step cap or canonicaliser after seeing any ratio",
 "leaving canonicalisation, normalisation, y tracking, cross-multiplication or look-ahead and escape work uncharged, or charging the candidate less than the matched negation arm pays for the same primitive",
 "amortising alpha images across walks or targets unless the same saving is charged to the reference",
 "reporting iteration counts, a stage ratio or walk-only cost as a speedup",
 "reading the result as a statement about deployed curves (|D_K| large, no norm-2 endomorphism) or as an exponent change",
 "dropping curves or targets because they are unfavourable; selecting the cheaper candidate arm per curve is the only pre-registered choice",
 "a clock read as a result"],
"literature":[
 {"ref":"knowledge/frontiers/ecdlp/generic-rho/KR-RHO-482ed3.yaml","provenance":"internal","claim":"signed-Frobenius classes give sqrt(m) in iterations against negation, canonicalisation still charged","verified_by":"claim text read 2026-10-31"},
 {"ref":"knowledge/frontiers/ecdlp/generic-rho/KR-RHO-0528e7.yaml; KR-RHO-825bca.yaml; KR-RHO-fb88e6.yaml","provenance":"internal","claim":"automorphism classes give sqrt(m); measured 0.790*sqrt(6) on BN254; negation fruitless cycles","verified_by":"claim text read 2026-10-31"},
 {"ref":"knowledge/leads/ecdlp/structure/LEAD-STR-small-cm-disc-nonunit-endo.yaml","provenance":"internal","claim":"h >= log N / log n and net factor <= sqrt(h)/kappa; revisit_when names this construction","verified_by":"lead file read 2026-10-31"},
 {"ref":"Duursma, Gaudry, Morain, ASIACRYPT 1999","provenance":"recalled","claim":"sqrt(m) rho speedup on classes of an order-m automorphism group","verified_by":"not re-read; abstract-level recall"},
 {"ref":"Velu 1971 (isogenies from a rational subgroup)","provenance":"recalled","claim":"degree-2 isogeny with rational 2-torsion kernel; probe uses PARI ellisogeny","verified_by":"probe_alpha.out: x(alpha P)=x([lambda]P) on 10/10 points for h=19,23"}],
"amendments":[],
"freeze":{"status":"draft","protocol_sha256":None,"commit":None,"frozen_at":None,"filed_before_affected_data":None}}
json.dump(P,open('protocol.json','w'),indent=2)
