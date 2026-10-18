// Run from the repository root after verification. This validates receipt
// identity/status; it does not replace Lean or independent semantic review.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const study = 'research/lean_retrospective_20261018';
const inventory = JSON.parse(fs.readFileSync(`${study}/inventory.json`));
const receiptPaths = fs.readdirSync(`${study}/receipts`).filter(p=>p.endsWith('.json')).sort();
const receipts = receiptPaths.map(p=>({path:`${study}/receipts/${p}`,
  data:JSON.parse(fs.readFileSync(`${study}/receipts/${p}`))}));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const targets = inventory.targets.map(t => {
  if (!fs.existsSync(t.theorem_file)) return {spec:t.spec,theorem:t.theorem_name,status:'undischarged'};
  const relevant = receipts.filter(r=>r.data.task?.theorem_name===t.theorem_name);
  const accepted = relevant.findLast(r=>{
    const d=r.data, p=d.provenance, task=d.task, v=d.verification;
    return d.schema==='crypto.autoresearch.formal_verification.v1' &&
      !d.infrastructure_failure && v?.status==='machine_verified' &&
      v.build_passed && v.axiom_audit_passed &&
      p?.theorem_sha256===sha(t.theorem_file) &&
      p.task_spec_sha256===sha(t.spec) &&
      p.lean_toolchain_sha256===sha(path.join(task.workspace,'lean-toolchain')) &&
      p.lake_manifest_sha256===sha(path.join(task.workspace,'lake-manifest.json'));
  });
  return {spec:t.spec,theorem:t.theorem_name,
    status:accepted?'machine_verified':'not_verified_for_current_inputs',
    receipt:accepted?.path??null,semantic_review:'pending',
    other_attempts:relevant.filter(r=>r!==accepted).map(r=>({receipt:r.path,
      status:r.data.verification?.status??'infrastructure_failure'}))};
});
const result = {schema:'lean-retrospective.verification-summary.v1',
  scope:'All frozen formal target specs in the starting Git tree. Proof-source and pin hashes must match current inputs; full prose-claim coverage and independent semantic review remain open.',
  baseline:inventory.revision, counts:{targets:targets.length,
    machine_verified:targets.filter(t=>t.status==='machine_verified').length,
    undischarged:targets.filter(t=>t.status==='undischarged').length,
    failed_current_inputs:targets.filter(t=>t.status==='not_verified_for_current_inputs').length},targets};
fs.writeFileSync(`${study}/verification-summary.json`,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result.counts));
if (result.counts.failed_current_inputs || result.counts.machine_verified < 65) process.exitCode=1;
