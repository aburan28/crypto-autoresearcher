"""Derive the delivery summary from preserved receipts, never rerun searches."""
from hashlib import sha256
import json
from pathlib import Path

root=Path(__file__).resolve().parent
producer=json.loads((root/'receipts/validation-02/checks.json').read_text())
sage=json.loads((root/'sage-independent.json').read_text())
source_manifest=json.loads((root/'sources/aps2018.pdf.manifest.json').read_text())
assert producer['status']==sage['status']=='passed'
sources=[dict(id='APS2018',provenance='retrieved',
    url='https://pure.tue.nl/ws/files/91158650/609.pdf',
    read_scope='section 3 and adjacent summation-polynomial definition',
    verified_by='/root/labelled_relations',sha256=source_manifest['sha256'],
    source_manifest='sources/aps2018.pdf.manifest.json'),
    dict(id='Kudo2018',provenance='retrieved',
    url='https://link.springer.com/chapter/10.1007/978-3-030-00434-7_19',
    read_scope='primary publisher abstract, access notice and references only',
    full_text_retrieved=False,verified_by='/root/labelled_relations'),
    dict(id='P256-parameters',provenance='internal',
    path='../../baseline/parameters.py',sha256=producer['baseline_sha256'])]
result=dict(schema='p256-f3-implementation-result/v1',task='TASK-20261025-1f3375',
    status='implementation_validation_complete_theory_obligations_open',
    scientific_performance_trial=False,official_state_transition=False,
    performance_advantage_claim=False,curve='P-256',
    checks=dict(python_passed=producer['passed_checks'],python_total=producer['check_count'],
      sage_passed=sage['checks'],sage_total=sage['checks'],
      labelled_points=72,membership_polynomials=9,
      coordinate_domain_triples=1536,independent_signed_point_sums=6144),
    exact_cases=producer['cases'],
    construction=dict(initial_label_points_per_case=24,
      scalar_multiplications_per_initial_base=48,addition_calls_per_initial_base=24,
      rejected_attempts_per_case=0,arranged_replacements_per_arranged_case=1,
      extra_scalar_multiplications_per_replacement=2,
      extra_addition_calls_per_replacement=1,
      scope='base construction counters only; target generation/validation/search/recovery separately charged'),
    observations=[
      'Natural unknown-log hash-to-point target: zero dependencies in the declared domains.',
      'Arranged distinct-coordinate label-vector dependency: exactly one, A=B=0.',
      'Known-witness useful fixture: exactly one, nonzero B, candidate point verified.',
      'Inverse-pair and repeated-index cancellations rejected as useful information.',
      'Forged label, off-curve point/target, malformed partition and wrong-sign controls pass.',
      'Hybrid complete-domain result matches separate group enumeration and independent Sage.'],
    limitations=[
      'One natural deterministic case is correctness evidence, not a sampled yield or performance panel.',
      'Useful fixture intentionally uses known target witness in generation; search accepts points only.',
      'Only m=3 finite-domain hybrid is implemented; no general Groebner solver or large-base trial.',
      'Randomness/success laws in report are derived conditional models, not measured probabilities.',
      'Adaptive/dependent labels invalidate the independent-uniform conditional-B lemma.',
      'Full Kudo chapter inaccessible; exact published limitation theorem not claimed reproduced.',
      'No comparative speed result, general impossibility result or official scientific transition.',
      'Natural useful-dependency solver/cost gap remains; problem draft awaits root integration.'],
    next_decisive_step='Derive an exact partition-compatible m>=4 solver with fully charged label construction, residual solving, rational signs, zero-Q outputs and memory; supply a natural-instance success/cost law and independent certificates before any separately admitted performance trial.',
    source_provenance=sources,
    protocol_deviations=[
      'AGENTS fixed /usr/local/bin/python3 path absent; preserved failed launch, used CPython3.12.14 at actual python3 path.',
      'Sandboxed curl and Docker inspection failed; reviewed escalations enabled source retrieval and offline cached Sage.',
      'No search_knowledge tool exposed; primary-source retrieval used; no absence inference.',
      'Root owns problems/index and PDF integration; scoped problem-record draft and editable SVGs supplied.'],
    artifacts=dict(report='report.md',diagram='diagram.svg',counts='counts.svg',
      producer='receipts/validation-02/checks.json',independent='sage-independent.json',
      commands='commands.md',problem_draft='problem-record.md'),
    source_sha256={name:sha256((root/name).read_bytes()).hexdigest()
      for name in ('labelled.py','validate.py','verify_sage.py')})
(root/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(status=result['status'],checks=result['checks']),indent=2))
