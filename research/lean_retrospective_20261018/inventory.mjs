// Inventory the exact Git tree on stdin. This does not verify any theorem.
// Run from the repository root; tracked target specs must match that tree.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const [revision, output] = process.argv.slice(2);
if (!/^[0-9a-f]{40}$/.test(revision ?? '') || !output) {
  throw Error('usage: git ls-tree -r REV | node inventory.mjs FULL_SHA OUTPUT');
}
const entries = fs.readFileSync(0, 'utf8').trim().split('\n').filter(Boolean).map(line => {
  const m = /^(\d+) (blob|tree|commit) ([0-9a-f]{40})\t(.+)$/.exec(line);
  if (!m) throw Error(`unexpected Git tree entry: ${line}`);
  return {mode:m[1], type:m[2], blob:m[3], path:m[4]};
});
const tracked = new Set(entries.map(e => e.path));
const scalar = (text, key) => {
  const value = text.match(new RegExp(`^${key}:\\s*(.+)$`, 'm'))?.[1]?.trim();
  if (!value || /^[|>&*!{[]/.test(value)) throw Error(`unsupported ${key}`);
  if (value.startsWith('"')) return JSON.parse(value);
  if (value.startsWith("'")) return value.slice(1,-1).replaceAll("''", "'");
  // These frozen scalar fields are plain YAML strings. Ignore an inline
  // comment introduced after whitespace, as the repository YAML loader does.
  return value.replace(/\s+#.*$/, '').trimEnd();
};
const fixtures = p => /^tools\/(lean\/)?selftest\//.test(p);
const lean = entries.filter(e => e.path.endsWith('.lean') && !fixtures(e.path));
const targets = entries.filter(e => /^formal\/targets\/.*\.yaml$/.test(e.path)).map(e => {
  if (!fs.existsSync(e.path)) return {...e, status:'spec_not_materialized'};
  const bytes = fs.readFileSync(e.path);
  const blob = crypto.createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex');
  if (blob !== e.blob) throw Error(`target spec differs from inventory revision: ${e.path}`);
  const text = bytes.toString('utf8');
  const workspace = scalar(text, 'workspace');
  const theorem_file = scalar(text, 'theorem_file');
  const source = path.posix.normalize(path.posix.join(workspace, theorem_file));
  return {spec:e.path, spec_blob:e.blob, claim_id:scalar(text,'claim_id'),
    theorem_name:scalar(text,'theorem_name'), theorem_file:source,
    status:tracked.has(source) ? 'source_present_not_rechecked' : 'undischarged_in_snapshot'};
});
const report = {
  schema:'lean-retrospective.inventory.v1', revision,
  scope:'Tracked Lean source paths, Lake projects and frozen formal target specs at this revision. Not an extraction of every prose claim, not a build or semantic-fidelity audit, and not a review of earlier Git revisions.',
  counts:{lean_sources_excluding_selftests:lean.length,
    lake_projects:entries.filter(e=>/(^|\/)lakefile\.(toml|lean)$/.test(e.path) && !fixtures(e.path)).length,
    formal_target_specs:targets.length,
    targets_without_source:targets.filter(t=>t.status==='undischarged_in_snapshot').length},
  lean_sources:lean.map(e=>({path:e.path, blob:e.blob, status:'not_rechecked_by_inventory'})),
  lake_projects:entries.filter(e=>/(^|\/)lakefile\.(toml|lean)$/.test(e.path) && !fixtures(e.path)).map(e=>({path:e.path,blob:e.blob})),
  targets
};
fs.writeFileSync(output, JSON.stringify(report,null,2)+'\n', {flag:'wx'});
console.log(JSON.stringify(report.counts));
