from pathlib import Path
import hashlib
import json
import re
from shutil import copy2

task = 'TASK-20261018-29a8c7'
joint = 'J4-blind-mathematical-boundary'
out = Path('/workspace/review-lean-evidence/research/lean_review_evidence_20261018/reports') / task
scratch = Path('/tmp/blind-j4-29a8c7')
source = (out / 'Controls.lean').read_text()
log = (out / 'controls.log').read_text()
report = (out / 'report.md').read_text()
assert 'exit_code: 0' in log
assert 'sorryAx' not in log
assert ': error' not in log and ': warning' not in log
expected = re.findall(r'^theorem (\w+)', source, re.M)
printed = re.findall(r"'BlindJ4\.(\w+)' depends on axioms: \[([^\]]*)\]", log)
assert set(expected) == {name for name, _ in printed}
axioms = sorted({a.strip() for _, items in printed for a in items.split(',') if a.strip()})
assert set(axioms) == {'propext', 'Classical.choice', 'Quot.sound'}
assert len(expected) == 34
lines = {name: source[:source.index('theorem ' + name)].count('\n') + 1 for name in expected}
groups = {
 'ordinary-collision': [n for n in expected if n.startswith('ordinary_')],
 'negated-collision': [n for n in expected if n.startswith('negated_')],
 'affine-word': [n for n in expected if n.startswith('affine_')],
 'transport-control': [n for n in expected if n.startswith('transport_')],
 'certificate-boundary': [n for n in expected if not n.startswith(('ordinary_', 'negated_', 'affine_', 'transport_'))],
}
checks = {
 'schema': 'blind-mathematical-review.checks.v1', 'task_id': task,
 'joint': joint, 'verdict': 'holds', 'final_compile_exit_code': 0,
 'final_source_sha256': hashlib.sha256(source.encode()).hexdigest(),
 'theorem_count': len(expected), 'axiom_union': axioms,
 'claims': [{'input_id': key, 'status': 'checked', 'boundary_verdict': 'holds',
             'checks': [{'declaration': 'BlindJ4.' + name, 'source': 'Controls.lean',
                         'line': lines[name], 'status': 'kernel_checked',
                         'axioms': next(items.split(', ') for n, items in printed if n == name)}
                        for name in names]} for key, names in groups.items()],
 'written_only': [
     {'claim': 'Displayed finite-field inverse arithmetic and derivative values',
      'note': 'Written derivations; corresponding collision equivalences and nonsingularity are independently kernel checked.'},
     {'claim': 'Q=-P stated in prose',
      'note': 'The actual required P+Q=0 is kernel checked directly.'},
     {'claim': 'Singleton [P] rejects identity',
      'note': 'Follows immediately from checked singleton acceptance definition and P != 0; no separately named theorem.'},
 ],
 'final_log': 'controls.log', 'failed_attempts': [
    {'source': 'artifacts/Controls_01.lean', 'log': 'artifacts/controls_01.log', 'exit_code': 1},
    {'source': 'artifacts/Controls_02.lean', 'log': 'artifacts/controls_02.log', 'exit_code': 1},
    {'source': 'artifacts/Controls_03.lean', 'log': 'artifacts/controls_03.log', 'exit_code': 1},
    {'source': 'artifacts/Controls_04.lean', 'log': 'artifacts/controls_04.log', 'exit_code': 1},
 ],
 'successful_scratch_attempt': {'source': 'artifacts/Controls_05.lean', 'log': 'artifacts/controls_05.log', 'exit_code': 0},
 'infrastructure_attempt': {'log': 'artifacts/infrastructure_00.log', 'exit_code': 127},
}
(out / 'artifacts' / 'checks.json').write_text(json.dumps(checks, indent=2) + '\n')
sources = json.loads((out / 'artifacts' / 'source-digests.json').read_text())
own_reads = [str(scratch / ('Controls_%02d.lean' % i)) for i in range(1, 6)]
own_reads += [str(scratch / 'compile.py'), str(scratch / 'package_review.py'),
              str(out / 'Controls.lean'), str(out / 'controls.log'), str(out / 'report.md'),
              str(out / 'artifacts' / 'source-digests.json')]
attestation = {
 'schema': 'lean-review.attestation.v1',
 'task_id': task,
 'joints_owned': [joint],
 'verdict': 'holds',
 'verdict_scope': 'Independent derivations, finite examples, and controls for the supplied statement-only questions; no verdict on unseen producer artifacts.',
 'sources_read': [x['path'] for x in sources] + own_reads,
 'sources_read_note': 'Exact non-self-authored files are listed, including configuration and third-party source excerpts; those files were also byte-read for digests. Self-authored proof/driver/report reads are included. Own artifact copies and generated logs/checks are inventoried by artifact-digests.json. Directory/file-name enumeration and transitive compiler reads of pinned Lean/Mathlib compiled artifacts are distinguished below.',
 'source_digests': 'artifacts/source-digests.json',
 'read_sibling_reports': False,
 'read_sibling_messages': False,
 'blind_from_respected': True,
 'blind_from': ['producer repositories and proof text', 'producer reports and outputs',
                'review-plan.yaml', 'inputs.json and workflow-inputs.json',
                '/workspace/lean-review-inputs', 'git history',
                'sibling task reports and sibling messages'],
 'parent_messages_received': 'Task dispatch and one cache/tooling clarification only; no mathematical answer or sibling output was supplied.',
 'directory_discovery': ['AGENTS.md path discovery under the assigned review repository, isolated workspace, and /workspace/.agents',
                         'Isolated workspace top-level filenames',
                         'Third-party Mathlib source/cache filenames under the isolated workspace'],
 'direct_imports': re.findall(r'^import (.+)$', source, re.M),
 'compiler_dependency_reads': 'Supplied compiled .olean artifacts from the isolated Lean/Mathlib dependency closure. No dependency source/cache build or mutation.',
 'lean_version': '4.35.0',
 'mathlib_revision_from_isolated_manifest': 'cfc55fc58714a59dc06e6e79edc6d1d95140d3c2',
 'producer_commit_binding_independently_checked': False,
 'final_source_sha256': checks['final_source_sha256'],
 'final_compile_exit_code': 0,
 'checked_theorems': 34,
 'checked_claims': list(groups),
 'written_only_results': checks['written_only'],
 'axioms_observed': axioms,
 'custom_axioms_used': False,
 'native_decide_used': False,
 'sorry_used_in_accepted_controls': False,
 'failed_attempt_error_recovery_sorryAx': 'Present only in retained failed elaboration outputs 02-04, never accepted as evidence.',
 'procedure_deviations': [],
 'write_scope': [str(out), str(scratch)],
 'git_history_read': False,
 'producer_sources_changed': False,
 'task_or_plan_changed': False,
 'official_status_changed': False,
 'checks': 'artifacts/checks.json',
 'final_log': 'controls.log',
 'visuals': ['artifacts/boundary-diagram.mmd', 'artifacts/review-summary.pdf'],
 'remaining_limits': ['No comparison with producer theorem statements, proof terms, code, or reports.',
                      'No independent audit/rebuild of supplied third-party dependency binaries.',
                      'No research promotion, performance result, or ECDLP transfer is inferred.'],
}
# JSON is a strict subset of YAML 1.2 and preserves exact strings without a YAML dependency.
(out / 'review_attestation.yaml').write_text(json.dumps(attestation, indent=2) + '\n')
(out / 'artifacts' / 'boundary-diagram.mmd').write_text(re.search(r'```mermaid\n(.*?)\n```', report, re.S).group(1) + '\n')

# Self-contained vector PDF; no additional source, rendering service, or package needed.
def esc(s):
    return s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
ops = []
def text(x, y, s, size=10):
    ops.append(f'BT /F1 {size} Tf {x} {y} Td ({esc(s)}) Tj ET')
def box(x,y,w,h,label):
    ops.append(f'0.94 0.96 0.99 rg {x} {y} {w} {h} re f 0.15 0.25 0.4 RG {x} {y} {w} {h} re S 0 0 0 rg')
    text(x+7,y+h/2-3,label,9)
def arrow(x1,y1,x2,y2):
    ops.append(f'0.15 0.25 0.4 RG {x1} {y1} m {x2} {y2} l S {x2-4} {y2+3} m {x2} {y2} l {x2-4} {y2-3} l S')
text(40,800,'Blind mathematical boundary review',18)
text(40,777,task+' / '+joint,10)
text(40,756,'Verdict: holds within the supplied statement-only boundary.',11)
text(40,734,'34 kernel-checked theorems; final Lean exit 0; no warnings.',11)
text(40,716,'Axioms: propext, Classical.choice, Quot.sound. No producer source read.',10)
rows=[('Collision equation','Nonzero denominator','Unique scalar x'),
      ('Left-to-right word','Suffix negation signs','Affine action'),
      ('Transport composition','Coprime degree / size','Injective f'),
      ('Noncoprime degree 7','Zero f and back','Not injective'),
      ('Raw coordinates','Equation + nonsingular','Typed affine point'),
      ('Typed entries','Span + target sum','Certificate accepted')]
for i,row in enumerate(rows):
    y=655-i*70
    for j,label in enumerate(row):
        box(40+j*176,y,164,36,label)
        if j<2: arrow(204+j*176,y+18,216+j*176,y+18)
text(40,203,'Requested examples over F7: ordinary x=4; negated x=4; word result=4.',10)
text(40,184,'P=(0,1), Q=(0,6): valid, empty-span x values, P+Q=identity.',10)
text(40,165,'Empty tuple accepts identity only. Raw (0,0) is invalid.',10)
text(40,133,'Scope limit: unseen producer correctness and commit binding are unassessed.',10)
text(40,114,'Full derivations: report.md. Proofs: Controls.lean. Raw check: controls.log.',10)
text(40,95,'All failed control sources and logs are retained under artifacts/.',10)
stream='\n'.join(ops).encode('ascii')
objs=[b'<< /Type /Catalog /Pages 2 0 R >>',
      b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
      b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
      b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
      b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'\nendstream']
pdf=b'%PDF-1.4\n'
offsets=[0]
for i,obj in enumerate(objs,1):
    offsets.append(len(pdf))
    pdf += str(i).encode()+b' 0 obj\n'+obj+b'\nendobj\n'
xref=len(pdf)
pdf += b'xref\n0 '+str(len(objs)+1).encode()+b'\n0000000000 65535 f \n'
for offset in offsets[1:]:
    pdf += f'{offset:010d} 00000 n \n'.encode()
pdf += b'trailer\n<< /Size '+str(len(objs)+1).encode()+b' /Root 1 0 R >>\nstartxref\n'+str(xref).encode()+b'\n%%EOF\n'
(out / 'artifacts' / 'review-summary.pdf').write_bytes(pdf)
copy2(scratch/'package_review.py',out/'artifacts'/'package_review.py')
audit = {'task_id':task,'theorems_expected':len(expected),'axiom_lists_observed':len(printed),
         'axiom_union':axioms,'all_theorems_covered':True,'final_exit_code':0,
         'warnings_or_errors_in_final_log':False,'accepted_sorryAx':False}
(out/'artifacts'/'control-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
inventory=[{'path':str(p.relative_to(out)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
           for p in sorted(out.rglob('*')) if p.is_file() and p.name!='artifact-digests.json']
(out/'artifacts'/'artifact-digests.json').write_text(json.dumps(inventory,indent=2)+'\n')
print(json.dumps(audit,indent=2))
print('deliverables:',', '.join(p.name for p in out.iterdir()))
