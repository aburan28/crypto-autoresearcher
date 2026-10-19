// Receipt consistency only. Fresh Lean checks and independent semantic review remain required.
// The original four-hash summary/receipts are preserved in the frozen producer Git revision.
import {spawnSync} from 'node:child_process';
const study = 'research/lean_retrospective_20261018';
const args = ['-m', 'orchestration.formal.receipts',
  '--inventory', `${study}/inventory.json`,
  '--receipt-dir', `${study}/receipts-v2`,
  '--output', `${study}/verification-summary-v2.json`, ...process.argv.slice(2)];
const result = spawnSync(process.env.PYTHON || 'python3', args, {stdio: 'inherit'});
if (result.error) throw result.error;
process.exit(result.status ?? 1);
