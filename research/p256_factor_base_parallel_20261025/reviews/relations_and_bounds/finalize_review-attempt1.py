#!/usr/bin/env python3
"""Seal local review metadata; no Git writes, publication or state transition."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET

H=Path(__file__).resolve().parent
STUDY=H.parents[1]
REPO=STUDY.parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_once(path,data):
    with path.open('x') as stream:
        stream.write(json.dumps(data,indent=2,sort_keys=True)+'\n')


ind=json.loads((H/'independent-results.json').read_text())
adv=json.loads((H/'adversarial-results.json').read_text())
assert ind['status']==adv['status']=='passed'
assert all((H/name).stat().st_size==0 for name in ['independent-checks.stderr','adversarial-checks.stderr'])
for name in ['review-controls.svg','scope-diagram.svg']:
    ET.parse(H/name)
custody=json.loads((STUDY/'reviews'/'local-custody-exception.json').read_text())
zip_path=Path(custody['custody']['local_delta_zip'])
zip_digest=digest(zip_path.read_bytes())
assert zip_digest==custody['custody']['zip_sha256']

sources=['f3/labelled.py','f3/validate.py','f3/verify_sage.py','f3/build_result.py',
    'f4/divisor.py','f4/validate.py','f4/theory.py','f4/independent_check.py','f4/adversarial_check.py',
    'f6/check_bounds.py','f6/verify_artifacts.py','f8/orbit_matrix.py','f8/verify_artifacts.py']
requested=set(ind['input_sha256'])
requested.update('tracks/'+n for n in sources)
requested.update('tracks/'+track+'/'+name for track in ['f3','f4','f6','f8'] for name in ['report.md','result.json'])
requested.update(['baseline/parameters.py','handoffs/TASK-20261025-6d88b2.json'])
rows={}
with zipfile.ZipFile(zip_path) as archive:
    for rel in sorted(requested):
        local=STUDY/rel
        raw=local.read_bytes()
        member=str(local.relative_to(REPO))
        archived=archive.read(member)
        assert raw==archived, 'sealed input differs: '+rel
        rows[rel]={'sha256':digest(raw),'size_bytes':len(raw),'sealed_zip_member':member,'sealed_zip_bytes_equal':True}
manifest={'schema':'local-review-inputs/v1','task':'TASK-20261025-6d88b2',
    'sealed_zip':str(zip_path),'sealed_zip_sha256':zip_digest,'all_listed_inputs_byte_equal_to_sealed_zip':True,
    'files':rows,'custody_exception_sha256':digest((STUDY/'reviews'/'local-custody-exception.json').read_bytes()),
    'note':'Hash manifest includes comparison inputs; hashes alone do not imply every source line was adversarially exercised.'}
write_once(H/'review-inputs.json',manifest)

local_artifacts={p.name:{'sha256':digest(p.read_bytes()),'size_bytes':p.stat().st_size}
    for p in sorted(H.iterdir()) if p.is_file() and p.name not in ['result.json','finalize.stdout','finalize.stderr']}
assert all(v['size_bytes']<65536 for n,v in local_artifacts.items() if n.endswith(('.json','.stdout','.stderr','.py','.md')))
actual_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
record={'schema':'local-adversarial-relations-bounds-review/v1','task':'TASK-20261025-6d88b2',
    'date_utc':datetime.now(timezone.utc).isoformat(),'status':'completed_with_scoped_wording_issue_and_procedure_deviations',
    'official_scientific_review_gate_discharged':False,'official_state_transition':False,
    'performance_or_attack_claim_promoted':False,'publication_authorized_by_this_review':False,
    'producer_imports_in_independent_calculation':False,'published_P256_and_secp256k1_inputs_only':True,
    'inference':{'requested_policy':'review-adversarial','runtime':'native Codex child session','binding_probed':False,
                 'resolved_model_attestation':None},
    'findings':[{'id':'F3-001','severity':'medium','type':'missing_modular_nonzero_qualification',
        'location':'tracks/f3/report.md:78 and :106-114',
        'claim':'Any nonzero relation vector chosen from points alone has uniform target coefficient B.',
        'defect':'Integer multiplicities are allowed, so c=(r,0,...) is a nonzero integer relation but forces A=B=0.',
        'required_hypothesis':'c is nonzero in F_r^n, with point-only selection and independent uniform label pairs.',
        'context_check':'F_r^2 is specified for label pairs; the report does not explicitly specify F_r^n or nonzero modulo r for c.',
        'implementation_impact':'No effect to the distinct-point three-entry +/-1 search or retained certificates.',
        'reproduction':'independent_checks.py: f3_checks; independent-results.json: F3 integer multiplicity counterexample',
        'suggested_resolution':'Dated additive qualification; preserve the sealed input report.'}],
    'coverage':{'F3':{'status':'exact_final_certificates_passed','labelled_points':72,'membership_polynomials':9,
        'coordinate_triples':1536,'sign_combinations_per_triple':4,'natural_relations':0,'arranged_zero_Q_relations':1,
        'known_witness_useful_relations':1,'conditional_law_small_prime_panels':3},
        'F4':{'status':'exact_final_certificates_passed','divisors':29,'fully_rational':24,'unresolved':5,
            'irreducible_norm_factors':100,'positive_rational_local_branches':98,'graph_kernels_and_rank_identities':4,
            'sampler_anchor_evaluation_ranks':6,'exact_P256_probability_fractions':7,'small_cyclic_counting_cases':20},
        'F6':{'status':'exact_polynomial_bound_lattice_certificates_passed','summation_polynomials':2,'rectangular_cases':28,
            'digit_cases':9,'lattice_rows':9,'norm_qualified_integer_zero_rows':8,'integral_unimodular_transform_verified':True,
            'constructed_Groebner_basis':['x - 1','y - 1'],'ordinary_target_extraction_demonstrated':False},
        'F8':{'status':'exact_map_and_matrix_certificates_passed','points':48,'relation_rows':96,
            'ranks':{'full':42,'symmetry':40,'stacked':47,'compressed':7},'baseline_symmetry_fairness_required':True}},
    'negative_controls':{'all_12_supplemental_invalid_controls_rejected':len(adv['rejected_invalid_controls'])==12,
        'zero_Q_dependency_useful':False,'inverse_only_row_informative':False,'unbalanced_unsigned_triangle_cancels':False,
        'one_lifted_polynomial_proves_finite_extraction':False,'known_root_offsets_prove_ordinary_target_solve':False,
        'false_compressed_rank_eight_row_valid':False,'unequal_symmetry_access_valid_comparison':False},
    'custody':{'actual_checkout_head':actual_head,'exception_payload_base_commit':custody['custody']['base_commit'],
        'sealed_zip_sha256':zip_digest,'all_manifest_inputs_byte_equal_to_zip':True,
        'normal_committed_and_pushed_input_precondition_met':False},
    'procedure_deviations':[
        'Local sealed inputs used under explicit exception; normal committed-and-pushed prerequisite is not met.',
        'Pre-derivation statement extraction exposed adjacent producer result prose; not a fully blind derivation.',
        'Named review-adversarial skill path absent; available review-evidence and research-visuals instructions read.',
        'Actual checkout HEAD differs from the custody exception payload base; both values recorded.',
        'Write-once review prose had count/base transcription issues; explicit review-correction-01.md preserves correction history.',
        'Fixed Python path absent; supplied CPython3.12.14/SymPy1.14.0/python-flint0.8.0 environment used.',
        'SVG render cache/font warnings retained; scientific checker stderr empty; coordinator owns PDF rendering/inspection.'
    ],
    'coverage_limits':['Published primality, total group orders and cofactors not independently reproved.',
        'No replay of older producer attempts, external literature verification, PRNG byte-stream replication, or general field-domain root search.',
        'No ordinary-target rate/cost trial, sparse graph scalability test, general multivariate extraction proof, end-to-end comparison or scientific-state transition.',
        'Local standalone child session is not represented as repository model-policy attestation or official review quorum.'],
    'reports':['review.md','review-correction-01.md','blind-derivation.md'],
    'artifacts':local_artifacts,'finalization_command':[sys.executable,*sys.argv]}
write_once(H/'result.json',record)
print(json.dumps({'status':record['status'],'sealed_inputs_checked':len(rows),'supplemental_invalid_controls_rejected':12,
                  'small_cyclic_counting_cases':20,'artifact':'result.json'}))
