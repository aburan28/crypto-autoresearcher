from pathlib import Path
import hashlib,json,re,yaml
BASE=Path('/workspace/review-lean-evidence')
ROOT=BASE/'research/lean_review_evidence_20261018/reports/TASK-20261018-a5dcec'
ART=ROOT/'artifacts'
FROZEN=Path('/workspace/lean-review-inputs/crypto-autoresearcher')
CACHE=Path('/workspace/crypto-autoresearcher/formal')
MATH=CACHE/'.lake/packages/mathlib'
reads={}
def add(path,mode):
 p=str(path)
 if p not in reads: reads[p]={'path':p,'modes':[]}
 if mode not in reads[p]['modes']:reads[p]['modes'].append(mode)
for name in ['AGENTS.md','ledger/handoffs/TASK-20261018-a5dcec.yaml','research/lean_review_evidence_20261018/inputs.json','research/lean_review_evidence_20261018/review-plan.yaml','.agents/skills/route/SKILL.md','.claude/skills/route/SKILL.md','.claude/skills/research-visuals/SKILL.md','agents/validator.md','docs/skill-routing.md','docs/skill-catalog.json','.claude/skills/review-evidence/SKILL.md','.claude/skills/review-evidence/references/lean-review.md','.claude/skills/formal/SKILL.md']:
 add(BASE/name,'content_or_metadata_read')
add('skill://plugin_connector_1p_c5b7d5df5d7081918f2c4be5a633ed5d/cloud-environment-runtime/SKILL.md','content_read')
for row in json.loads((ART/'frozen-hashes.json').read_text()):add(row['path'],'sha256_only_unless_other_mode_listed')
for name in ['research/lean_retrospective_20261018/proof-map.json','formal/CryptoResearch/Semaev/Certificate.lean','formal/CryptoResearch/NCP/AffineNormalForm.lean','formal/CryptoResearch/NCP/CommutatorIdeal.lean','formal/targets/semaev-decomposition-certificate.yaml','formal/targets/ncp-affine-normal-form.yaml','formal/targets/ncp-commutator-ideal-refutation.yaml','research/THM_SEMAEV_FALL1.md','research/THM_COMMUTATOR_KERNEL1.md','formal/lean-toolchain','formal/lakefile.toml','formal/lake-manifest.json','formal/README.md','research/lean_retrospective_20261018/README.md','formal/RetrospectiveAxiomAudit.lean','research/lean_retrospective_20261018/axioms.log']:
 add(FROZEN/name,'semantic_content_read')
for name in ['CryptoResearch/Semaev/Certificate.lean','CryptoResearch/NCP/AffineNormalForm.lean','CryptoResearch/NCP/CommutatorIdeal.lean','lean-toolchain','lakefile.toml','lake-manifest.json']:
 add(CACHE/name,'sha256_cache_binding')
for name in ['Mathlib/AlgebraicGeometry/EllipticCurve/Affine/Basic.lean','Mathlib/AlgebraicGeometry/EllipticCurve/Affine/Point.lean','Mathlib/AlgebraicGeometry/EllipticCurve/Affine/Formula.lean','Mathlib/Algebra/FreeAlgebra.lean','Mathlib/Algebra/MonoidAlgebra/Basic.lean','Mathlib/Algebra/MonoidAlgebra/Defs.lean','Mathlib/Algebra/Group/Commute/Defs.lean','Mathlib/Algebra/Ring/Commute.lean','Mathlib/Data/ZMod/Basic.lean','Mathlib/Algebra/Field/ZMod.lean']:
 add(MATH/name,'selected_source_sections_read')
for p in (MATH/'Mathlib/Algebra/MonoidAlgebra').glob('*.lean'):add(p,'rg_content_search')
for name in ['BoundaryControls.lean','EvenModulusBoundary.lean','ProducerAxiomAudit.lean','TypeAudit.lean','run_lean.py','render_report.py','review-boundary.dot','finalize_packet.py']:
 add(ART/name,'own_generated_source_written_and_read')
add(ROOT/'report.md','own_generated_source_rendered_and_inspected')
add(ROOT/'claims.json','own_generated_claim_table')
for p,row in reads.items():
 if Path(p).is_file():row['sha256']=hashlib.sha256(Path(p).read_bytes()).hexdigest()
source_inventory={'task_id':'TASK-20261018-a5dcec','entries':list(reads.values()),'notes':['All 198 frozen autoresearcher input files were read for SHA256 validation. Only entries marked semantic_content_read were read as substantive producer evidence.','Additional dependency source reads and source searches are enumerated. Lean also loaded compiled imported dependencies from the LEAN_PATH pinned by lean-env.json and run_lean.py; no independent rebuild of Mathlib or per-import binary provenance audit is claimed.','Own generated logs, PDF page images, diagram and JSON/YAML outputs were read for verification; these are review artifacts, not additional producer sources.','No sibling reviewer report, message, or verdict was read.']}
(ART/'sources-read.json').write_text(json.dumps(source_inventory,indent=2)+'\n')
att={'task_id':'TASK-20261018-a5dcec','reviewer_id':'independent-reviewer-TASK-20261018-a5dcec','joints_owned':['J2-certificate-affine-kernel-fidelity'],'sources_read':list(reads),'sources_read_manifest':'artifacts/sources-read.json','read_sibling_reports':False,'received_sibling_messages':False,'verdict':'holds','verdict_scope':'The ten explicit producer proof-map claims, with the stated typed-input/scalar-model/single-witness limitations.','joint_verdicts':{'J2-certificate-affine-kernel-fidelity':'holds'},'mathematical_validity':'holds','narrow_claim_fidelity':'faithful_scoped','full_target_coverage':'partial','full_historical_source_coverage':'partial; literal any-n extension of full kernel presentation fails at n=2','blind_rederivation_required_for_this_task':False,'mutual_blindness_respected':True,'blind_from_respected':True,'blind_from_note':'Only mutual sibling-report blindness applies to this task. This is not the separately assigned blind rederivation, and producer sources were intentionally read.','procedure_deviations':[],'machine_checks':{'fresh_frozen_module_compilations':3,'named_declaration_type_and_axiom_audits':10,'kernel_checked_control_theorems':26,'unapproved_axioms_in_final_proofs':[],'native_decide_used':False,'external_lean4checker_fresh':False,'repository_wide_target_runner_rerun':False},'limitations':['Only J2 is assessed; no conclusion on sibling joints or entire retrospective.','Compiler #eval retained as smoke output only.','Imported Mathlib cache used read-only on exact checked source/toolchain/manifest bindings.','Raw serialized parser, run integration, concrete curve equivariance, composition bridge, surjectivity and companion/full kernel coverage are not supplied by producer declarations.'],'writes_confined_to_task_directory_and_own_tmp':True,'producer_sources_and_receipts_unchanged':True,'committed':False,'pdf_inspection':{'pages':4,'all_pages_rendered_and_visually_inspected':True,'diagram_legible':True,'pdf':'report.pdf'},'archival_task':'TASK-20261018-95bdb1'}
(ROOT/'review_attestation.yaml').write_text(yaml.safe_dump({'review_attestation':att},sort_keys=False,allow_unicode=True,width=110))
# Validate final source scans and logs; failed construction attempts remain separate.
proofs=[FROZEN/'formal/CryptoResearch'/name for name in ['Semaev/Certificate.lean','NCP/AffineNormalForm.lean','NCP/CommutatorIdeal.lean']]+[ART/'BoundaryControls.lean',ART/'EvenModulusBoundary.lean']
for p in proofs:
 assert not re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b',p.read_text()),p
logs=['ProducerAxiomAudit-attempt-01.log','BoundaryControls-attempt-07.log','EvenModulusBoundary-attempt-02.log']
for p in logs:assert 'sorryAx' not in (ART/p).read_text(),p
claims=json.loads((ROOT/'claims.json').read_text());assert len(claims['claims'])==10;assert len(claims['controls'])==26
actual=[]
for row in json.loads((ART/'frozen-hashes.json').read_text()):
 h=hashlib.sha256(Path(row['path']).read_bytes()).hexdigest();assert h==row['expected'],row['path'];actual.append(row['path'])
(ART/'final-validation.json').write_text(json.dumps({'task_id':'TASK-20261018-a5dcec','status':'passed','claim_rows':10,'control_theorems':26,'frozen_hashes_rechecked_unchanged':len(actual),'source_read_entries':len(reads),'final_source_scan':'no forbidden proof constructs','final_axiom_logs':'standard foundations only','pdf_pages_inspected':4,'siblings_read':False},indent=2)+'\n')
print({'sources_read_entries':len(reads),'frozen_unchanged':len(actual),'status':'passed'})
