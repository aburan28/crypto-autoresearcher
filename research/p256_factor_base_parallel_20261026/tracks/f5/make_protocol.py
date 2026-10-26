"""Prepare a draft exact-panel protocol. No experiment executes here."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
TRACK = HERE.name
TASK = {'f5': 'TASK-20261026-26de77', 'f7': 'TASK-20261026-59f4c9'}[TRACK]
SEED = {'f5': 2026102605, 'f7': 2026102607}[TRACK]
PRIOR = 'research/p256_factor_base_parallel_20261025/'


def draft():
    f5 = TRACK == 'f5'
    question = ('On eight fixed canonical P-256 points and six frozen queries, do all four certified isogenies preserve complete signed three-summand relation sets and exact membership under the subgroup-normalized dual inverse?'
                if f5 else 'Does balanced even-degree genus-two class arithmetic retain infinity information and satisfy exact principal/pullback identities, with its root-free norm agreeing with separate Fp2 support reconstruction on the fixed finite panel?')
    candidate = ('All four serialized maps, exact image membership, independent Jacobian pair-lookup extraction, finite subgroup inverse and coordinate-isomorphism control.'
                 if f5 else 'Balanced triples, Cantor composition/reduction/infinity balancing, class operations and root-free elliptic norm.')
    reference = ('Exhaustive affine source-group enumeration of every signed multiset triple in the same fixed source base; complete six-query solution sets.'
                 if f5 else 'Separate quadratic-extension support reconstruction and elliptic group summation, including multiplicities and rationality refusal controls. Norm equality is not a class-equality oracle.')
    positives = ('Three constructed source queries (distinct, repeated, cancellation) must have at least one complete-domain relation, and transported query sets must equal the source oracle.'
                 if f5 else 'Seven actual P-256 pullbacks must have norm [2]P, balanced pullback addition must agree with source addition, and explicit principal/infinity identities must hold.')
    negatives = ('Zero denominator in the actual parser and wrong subgroup inverse scalar must be refused or disagree. Identity/pole behavior is explicit; no rational nonidentity small torsion is invented.'
                 if f5 else 'Omitted Frobenius conjugate, corrupted repeated-point multiplicity without tangent correction, and invalid infinity balance must be refused; dropping n must not make the infinity difference the identity.')
    sources = ([PRIOR+'tracks/f1/checks-02/generic-k4.json', PRIOR+'tracks/f5/identities.json']
               +[PRIOR+f'tracks/f5/attempt02-kernel-screen-{ell}.json' for ell in [3,5,11]] if f5
               else [PRIOR+'tracks/f7/checks.json', PRIOR+'tracks/f7/elliptic-quotient-checks.json', PRIOR+'tracks/f5/identities.json'])
    instruments = {'repo': 'isogeny-labs/crypto-autoresearcher', 'commit': None, 'build': [],
                   'binary_sha256': None, 'flags': {}, 'env': {}, 'threads': 1}
    def metric(identity, definition):
        return {'id': identity, 'name': identity.replace('_',' '), 'unit': 'exact count', 'kind': 'exact',
                'definition': definition, 'source': 'rows.jsonl '+identity, 'aggregation': 'per_row',
                'resolution': '1', 'uncertainty': 'none_exact'}
    controls = {}
    return {
      'schema':'experiment.protocol/v1', 'protocol_id':'P256-pass2-'+TRACK.upper(), 'version':1,
      'created':'2026-10-26', 'repository':'crypto-autoresearcher',
      'study_dir':str(HERE.relative_to(REPO)), 'authors':['/root/pass2_geometry'],
      'links':{'task':TASK, 'prior_study':PRIOR.rstrip('/'), 'literature':'literature.md'},
      'question':question,
      'claims':[{'id':'C-exact','text':question,'class':'exact_computation','decided_by':['exact-agreement']},
                {'id':'C-out-of-scope','text':'No end-to-end ECDLP advantage, method clock, uniform success law, formal certificate or official scientific transition is claimed.','class':'out_of_scope','decided_by':[]}],
      'hypotheses':[],
      'arms':[{'id':'candidate','role':'candidate','description':candidate,'instrument':instruments.copy(),
               'parameters':{'track':TRACK,'execution_unit':'one complete frozen panel','shared_setup':'same process and fixed input construction'}},
              {'id':'reference','role':'reference','description':reference,'instrument':instruments.copy(),
               'same_instrument_as':'candidate','parameters':{'track':TRACK,'execution_unit':'one complete frozen panel','shared_setup':'same process and fixed input construction'}}],
      'controls':{
       'aa':{'present':False,'comparison':None,'not_applicable_reason':'Exact finite identities and integer counts; no noisy hardware metric, population inference or comparative method clock. Both actual arms are deterministic given the same seed.'},
       'positive':{'present':False,'arm':None,'expected_detection':None,'not_applicable_reason':'Embedded positive cases exercise the actual arithmetic path: '+positives+' No separate positive arm is exported.'},
       'negative':{'present':False,'arm':None,'null_population':None,'not_applicable_reason':'Embedded malformed-certificate/refusal controls exercise the real path: '+negatives+' No statistical null-population or rate inference is planned.'}},
      'variable_ledger':{
       'independent':[{'name':'implementation','levels':['candidate','reference']}],
       'factors':[{'name':'curve_and_fields','treatment':'fixed','value':'published P-256 p,a=-3,b,r; Fp2=i^2+1 when used','how':'literal source constants checked against prior certified parameter artifacts'},
                  {'name':'input_panel','treatment':'fixed','value':SEED,'how':'same prospectively specified panel; no endpoint resampling or favorable-seed selection'},
                  {'name':'instrument','treatment':'fixed','value':'stdlib Python source at root-pinned implementation commit','how':'entrypoint/module bytes verified against that committed object before gate; actual interpreter digest observed'},
                  {'name':'host','treatment':'measured','how':'CPU/kernel/memory/interpreter in metadata; shared host clocks diagnostic only'},
                  {'name':'threads','treatment':'fixed','value':1,'how':'pure single-threaded Python; one compute process per geometry worker'},
                  {'name':'order_and_warmup','treatment':'fixed','value':'frozen source order, zero warmups','how':'exact identities rather than timings; shared setup and arm work documented'},
                  {'name':'memory_and_environment','treatment':'measured','how':'two GiB address-space guard; no memory-performance claim; resource diagnostics retained'},
                  {'name':'analyst','treatment':'fixed','value':'frozen analysis.py, labels visible','how':'script fixed before data, raw finite identities and failure rows retained'}],
       'comparisons':[{'id':'exact-agreement','arms':['candidate','reference'],'differs_in':['implementation'],'design':'absolute','threshold':'zero failed declared exact-identity checks; every declared case completed, with separate validity controls'}],
       'aa_not_applicable':'No noise-based metric is claimed.', 'crosses_map':True},
      'randomization':{'arm_order':'fixed','arm_order_reason':'Two actual exact arithmetic arms share a guarded process and frozen case order. No timed comparison or order-sensitive performance criterion.',
        'seed_derivation':{'method':'explicit_list','seeds':[SEED],'nonce':None,'note':'The same fixed seed cycles over candidate/reference instance0 replicate0; case generation is domain-separated SHA256 as frozen in run.py.'},
        'instance_sampling':{'rule':'One complete frozen panel, identified as instance0, with case laws in extensions and run.py; generation shared independently of arm.','independent_of_arm':True},
        'blinding':{'analysis_labels_masked':False,'how':'Labels visible; no novelty/statistical judgment is made, and analysis.py only inventories recorded rows/checks.','unmasked_at':None}},
      'sample_size':{'instances':1,'replicates':1,'warmups':0,
        'power':{'method':'exact','alpha':0.05,'tests_in_family':1,'correction':'none','rank_test_n':None,'min_attainable_two_sided_p':None,'passes':True,
                 'note':'Finite exact-computation coverage, not a hypothesis test. No p-value or population-power claim; the two rows are two actual algorithms on the same single fixed panel.'},
        'preflight_runtime':{'fixed_seconds':None,'per_sample_seconds':None,'threads':1,'estimated_total_seconds':120,
                             'measured_on':'Not measured: prospective planning envelope equals the 120s infrastructure watchdog; no unapproved pilot was taken.'}},
      'metrics':{'primary':[metric('assertions_passed','Number of native exact checks passed by this actual arm; not a work/attack-cost proxy.')],
                 'secondary':[metric('checked_objects','Number of explicitly identified native panel objects inspected by this arm; arms perform different verification work.'),
                              metric('case_files','Number of raw case records emitted under this arm. Shared setup and object construction are explicit, not charged as a comparative cost.')]},
      'measurement':{'isolation_required':'none','warmups':0,'order':'sequential','clock':'none','counters':['all native exact object/check counters'],
                     'record':['cpu_model','kernel','memory_bytes','python','interpreter_sha256','source_files','runtime_head','pinned_implementation_commit','checkpoint_gate','isolation.blockers'],
                     'timed_primary_justification':None},
      'execution':{'backend':'local','queue':None,'placement':{'memory_gb':2,'worker_cpu_limit':1,'shared_host':True},'measurement_class':'search','timeout_seconds':120,
                   'checkpoint':{'policy':'none','interval_seconds':None,'grace_seconds':None,'restore_validation':'none','after_restore':{'wall_time':'invalid','counted_units':'valid'}},
                   'retries':{'infrastructure_only':True,'max_attempts':1}},
      'stopping_rules':[{'rule':'Execute the exact finite panel once per actual arm; all fixed cases, refusals and rejected draws retained. No optional seed/sample extension.','kind':'fixed_n','preregistered':True},
                        {'rule':'120s watchdog/2GiB guard protects the host. Any stop is unknown/not_completed, never an empty mathematical solution set.','kind':'budget','preregistered':True},
                        {'rule':'An exact mismatch records a failed active arm and retained partial artifacts; never retry the same output path or turn a failed control into a null result.','kind':'invalidation','preregistered':True}],
      'invalidation_rules':['A failed material correctness/refusal control invalidates dependent claims.','No isolated clocks are claimed; all process timing diagnostics have wall_valid=false.','No bare source run before an intact frozen protocol, explicit root release and real canonical S3 checkpoint gate.'],
      'decision_rule':{'text':'Report the finite exact identities only if every declared object/control completed and no declared exact check failed. Otherwise retain the precise mismatch, unknown or incomplete status. This is not a scientific state decision.',
                       'comparison_ids':['exact-agreement'],'threshold':'zero declared exact-check mismatches and complete fixed panel','statistic':'native exact-check outcomes and complete solution/class/norm records',
                       'interval':'none: exact finite computation, no population interval','multiple_comparison_correction':'none','effect_size_measure':'not applicable: exact identity defects, not comparative effect size',
                       'verdict_vocabulary':['completed_within_scope','failed_exact_check','not_completed','inconclusive']},
      'analysis_plan':{'script':{'path':'analysis.py','sha256':hashlib.sha256((HERE/'analysis.py').read_bytes()).hexdigest()},
                       'inputs':['runs/<fresh>/result.json','runs/<fresh>/checks.json','runs/<fresh>/rows.jsonl'],
                       'outputs':['runs/<fresh>/analysis.json'],'blinded':False,'frozen_before_data':True},
      'reporting':{'export_schema':'experiment.export/v1','review_schema':'experiment.review/v1','graphs':['typed correspondence and arithmetic pipeline; no fabricated quantitative data'],'report_dir':'.'},
      'inadmissible':['Changing case/seed laws or acceptance after seeing data without prospective amendment.','Treating a pole, timeout, parser error or unavailable case as empty mathematical evidence.','Reading fixed finite-domain exactness as attack-cost, general yield, novelty or a formal correctness certificate.','Copying a planned binary/source identity into an absent observed execution field.'],
      'literature':[{'ref':'literature.md','provenance':'internal','claim':'Actual prior/primary source review and explicit applicability limitations.','verified_by':'/root/pass2_geometry'},
                    {'ref':'https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/ell_curve_isogeny.html' if f5 else 'https://www.math.auckland.ac.nz/~sgal018/ANTS08.pdf',
                     'provenance':'retrieved','claim':'Map dual and differential normalization semantics.' if f5 else 'Balanced split-model divisor composition, reduction, infinity balancing and inversion, Algorithms1-5.','verified_by':'/root/pass2_geometry, 2026-10-26'}],
      'amendments':[],
      'freeze':{'status':'draft','protocol_sha256':None,'commit':None,'frozen_at':None,'filed_before_affected_data':None},
      'extensions':{'task':TASK,'fixed_seed':SEED,'execution_unit':'one fixed whole panel per actual arm, two arms in one guarded process','phase':'A engineering only; no observation rows collected',
                    'input_files':[{'path':path,'bytes':(REPO/path).stat().st_size,'sha256':hashlib.sha256((REPO/path).read_bytes()).hexdigest()} for path in sources],
                    'entrypoint':'run.py --out <fresh> --seed '+str(SEED)+' --release <root exact release.json>',
                    'checkpoint_scope':'Mandatory root S3 resume push/gate is separate from per-row application restart. No application resume or restored clock is claimed.',
                    'case_law':({'base':'first8 x-ordered y<=p/2 points of old F1 generic-k4 signed base; 16 signed labels',
                                 'queries':['P0+P1+P2','2P0+P1','P1 via cancellation','two SHA256 hash-to-point queries, cap1024 each','O'],
                                 'maps':[3,5,11,11],'arity':3,'source_oracle':'all multisets of3 signed labels; endpoint lookup preserves labels',
                                 'controls':'coordinate scaling u=2; wrong scalar and zero denominator; exact pole certificates, no extension kernel enumeration'} if f5 else
                                {'rational':'first16 distinct hash-z C(Fp) points, reject z=0,+-1 or w=0; cap4096, retain all draws; point-class n=i mod2',
                                 'quadratic':'first8 distinct u from hash a+bi with a,b!=0 and square sextic value in Fp2; cap512, retain all draws; v from Frobenius pair',
                                 'operations':'16 declared rational add/sub/double/cancel cases plus8 nonsplit additions and8 associativity checks',
                                 'pullbacks':[1,2,3,17,257,65537,'r-1'],'principal':'w-z^3, z-zP, both infinity classes and malformed controls',
                                 'reference':'reconstruct every native fixture support and compute elliptic image sum in Fp2; norm equality alone never proves class equality'})}
    }


if __name__ == '__main__':
    target = HERE/'protocol.draft.json'
    with target.open('x') as handle:
        handle.write(json.dumps(draft(), indent=2)+'\n')
    print(target)
