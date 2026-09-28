const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('../ui/node_modules/jsdom');
const root = path.resolve(__dirname, '..');
const app = fs.readFileSync(path.join(root, 'ui/static/app.js'), 'utf8')
  .replace(/initChrome\(\);\s*renderNav\(\);\s*route\(\);\s*boot\(\);\s*$/, 'window.ui = {viewRecord, state, opsPanel, fmtIops, fmtCount, fmtBytes, progressPanel, viewCompare, comparisonReasons, viewExperiments};');
const raw = '---\nid: KN-FIND-test\n---\n# Finding\n<script>alert(1)</script>\n';
const detail = {
  summary: { id: 'KN-FIND-test', kind: 'KN', area: 'FIND', title: 'A scoped finding', path: 'knowledge/findings/KN-FIND-test.md' },
  body: { proof_status: 'derivation', confidence: 'established', tags: [] },
  markdown: '## Finding\nA scoped observation.\n## Limits\nNo general result.\n## Next work\nReview the claim.',
  verified: true, links: { in: [], out: [] }, source_url: 'sources/KN-FIND-test.json',
};
const settle = () => new Promise(resolve => setImmediate(resolve));
function setup(sourceFailure = false) {
  const dom = new JSDOM(fs.readFileSync(path.join(root, 'ui/static/index.html'), 'utf8'), {
    url: 'https://example.test/crypto-autoresearcher/#/record/KN-FIND-test', runScripts: 'outside-only',
  });
  const calls = [], copied = [];
  let fail = sourceFailure;
  dom.window.HTMLElement.prototype.scrollIntoView = function() {};
  Object.defineProperty(dom.window.navigator, 'clipboard', { value: { writeText: async text => copied.push(text) } });
  dom.window.fetch = async url => {
    calls.push(url);
    if (url.includes('/sources/') && fail) { fail = false; return {ok: false, status: 503}; }
    return {ok: true, json: async () => url.includes('/sources/') ? {raw, path: detail.summary.path} : structuredClone(detail)};
  };
  dom.window.eval(app);
  dom.window.ui.state.meta = {mode: 'static', commit: 'abc123', repo_url: 'https://github.com/example/research', built_at: '2026-09-07T00:00:00+00:00'};
  return {dom, calls, copied};
}

test('entry is complete without downloading source; outline and proof basis are visible', async () => {
  const {dom, calls} = setup();
  await dom.window.ui.viewRecord(detail.summary.id);
  assert.match(dom.window.document.querySelector('.md').textContent, /No general result/);
  assert.equal(dom.window.document.querySelectorAll('.outline-link').length, 3);
  assert.match(dom.window.document.querySelector('.proof-basis').textContent, /not a machine-verified proof/);
  assert.equal(calls.length, 1);
  assert.match(calls[0], /\/crypto-autoresearcher\/data\/records\//);
  dom.window.close();
});

test('source deep link loads escaped full text and copies the original bytes', async () => {
  const {dom, calls, copied} = setup();
  await dom.window.ui.viewRecord(detail.summary.id, new dom.window.URLSearchParams('tab=source'));
  await settle();
  assert.equal(dom.window.document.querySelector('.raw').textContent, raw);
  assert.equal(dom.window.document.querySelector('.source-reader script'), null);
  assert.equal(dom.window.document.querySelector('[role=tab][aria-selected=true]').textContent, 'source');
  [...dom.window.document.querySelectorAll('button')].find(b => b.textContent === 'Copy source').click();
  await settle();
  assert.deepEqual(copied, [raw]);
  assert.match(calls[1], /\/crypto-autoresearcher\/data\/sources\/KN-FIND-test.json$/);
  dom.window.close();
});

test('keyboard tabs update their link and source failure offers a working retry', async () => {
  const {dom} = setup(true);
  await dom.window.ui.viewRecord(detail.summary.id);
  const tabs = dom.window.document.querySelectorAll('[role=tab]');
  tabs[0].dispatchEvent(new dom.window.KeyboardEvent('keydown', {key:'ArrowRight', bubbles:true}));
  assert.equal(dom.window.document.activeElement, tabs[1]);
  tabs[1].dispatchEvent(new dom.window.KeyboardEvent('keydown', {key:'ArrowRight', bubbles:true}));
  await settle();
  assert.match(dom.window.location.hash, /\?tab=source$/);
  assert.match(dom.window.document.querySelector('[role=alert]').textContent, /Source could not be loaded/);
  [...dom.window.document.querySelectorAll('button')].find(b => b.textContent === 'Retry source').click();
  await settle();
  assert.equal(dom.window.document.querySelector('.raw').textContent, raw);
  dom.window.close();
});

test('a network failure is recoverable and is not labelled a missing record', async () => {
  const {dom} = setup();
  dom.window.fetch = async () => { throw new Error('offline'); };
  await dom.window.ui.viewRecord(detail.summary.id);
  const alert = dom.window.document.querySelector('[role=alert]');
  assert.match(alert.textContent, /Could not load this record/);
  assert.match(alert.textContent, /Try again/);
  assert.doesNotMatch(alert.textContent, /not included in this snapshot/);
  dom.window.close();
});

test('ops panel is omitted when the snapshot has no AWS credentials', () => {
  const {dom} = setup();
  assert.equal(dom.window.ui.opsPanel({
    available: false, reason: 'no AWS credentials in this environment',
  }), null);
  assert.equal(dom.window.ui.fmtIops(null), '—');
  assert.equal(dom.window.ui.fmtIops(0), '0/s');
  assert.equal(dom.window.ui.fmtBytes(null), '—');
  dom.window.close();
});

test('an empty last-hour window shows an em dash, never a naked zero', () => {
  const {dom} = setup();
  const latest = new Date(Date.now() - 3 * 3600 * 1000).toISOString();
  const el = dom.window.ui.opsPanel({
    available: true,
    stale: true,
    latest_point: latest,
    database: {id: 'rho-dp', engine: 'postgres', engine_version: '16.13',
               class: 'db.r7g.xlarge', region: 'us-west-2'},
    last_hour: {basis: 'latest_sample', empty: true, samples: 0,
                write_iops: null, read_iops: null,
                write_bytes_per_sec: null, read_bytes_per_sec: null},
    last_24h: {write_iops: 502.4, read_iops: 11600, write_ops: 43406068,
               read_ops: 1000000000, samples: 288,
               write_bytes_per_sec: 25e6, read_bytes_per_sec: 134e6},
    storage: {used_bytes: 50.9 * (1024 ** 3), free_bytes: 349.1 * (1024 ** 3),
              allocated_bytes: 400 * (1024 ** 3)},
    object_store: {bucket: 'crypto-autoresearcher', bytes: 850e9, objects: 12,
                   as_of: latest},
    cpu_percent: 41.2,
    connections: 18,
  });
  assert.equal(el.getAttribute('aria-label'), 'Database load');
  assert.match(el.textContent, /Hour at latest sample/);
  assert.match(el.textContent, /No samples in this window/);
  assert.match(el.textContent, /hour ending at that sample/);
  assert.doesNotMatch(el.textContent, /No samples in this window[\s\S]*0\/s/);
  assert.match(el.textContent, /43\.41M/);
  assert.match(el.textContent, /writes/);
  assert.match(el.textContent, /reads/);
  assert.match(el.textContent, /Storage/);
  assert.match(el.textContent, /crypto-autoresearcher/);
  assert.doesNotMatch(el.textContent, /\.rds\.amazonaws\.com/);
  dom.window.close();
});

test('a live hour shows writes and reads per second, not a zero placeholder', () => {
  const {dom} = setup();
  const el = dom.window.ui.opsPanel({
    available: true,
    stale: false,
    latest_point: new Date().toISOString(),
    database: {id: 'rho-dp', engine: 'postgres', region: 'us-west-2'},
    last_hour: {basis: 'wall', empty: false, samples: 60,
                write_iops: 1720, read_iops: 11600,
                write_bytes_per_sec: 25 * 1024 * 1024,
                read_bytes_per_sec: 134 * 1024 * 1024},
    last_24h: {write_iops: 500, read_iops: 10000, write_ops: 40000000,
               read_ops: 800000000, samples: 288,
               write_bytes_per_sec: 20e6, read_bytes_per_sec: 100e6},
    storage: {used_bytes: 50 * (1024 ** 3), free_bytes: 350 * (1024 ** 3),
              allocated_bytes: 400 * (1024 ** 3)},
  });
  assert.match(el.textContent, /Last hour/);
  assert.match(el.textContent, /1\.7k\/s/);
  assert.match(el.textContent, /11\.6k\/s/);
  assert.doesNotMatch(el.textContent, /No samples in this window/);
  dom.window.close();
});

test('progress shows missing and stale telemetry honestly and preserves zero cost', () => {
  const {dom} = setup();
  const ui = dom.window.ui;
  assert.match(ui.progressPanel({available:false}).textContent, /unavailable/);
  assert.doesNotMatch(ui.progressPanel({available:false}).textContent, /\$0/);
  const p = {available:true, generated_at:'2020-01-01T00:00:00Z', source_updated_at:'2020-01-01T00:00:00Z',
    metrics:{actions_last_24h:0, design_actions_last_24h:0, run_actions_last_24h:0,
      measured_cost_usd_last_24h:0, runner_coverage_24h:'0/0', cost_coverage_last_24h:'1/2',
      runner_output_validated_trial_delta_24h:-1}};
  const panel = ui.progressPanel(p);
  assert.match(panel.textContent, /Stale snapshot/);
  assert.match(panel.textContent, /\$0\.0000/);
  assert.match(panel.textContent, /Cost coverage: 1\/2/);
  assert.match(panel.textContent, /not yet measured/);
  dom.window.close();
});

function comparisonFixture(id) {
  return {id, label:id, manifest_sha256:'a'.repeat(64), scope:'bounded-Boolean-solver-stage',
    timing_boundary:'same boundary', excluded_costs:['setup'], complete:true, verification:'recorded_verified',
    environment:{python:'fixture',platform:'fixture',harness_sha256:'c'.repeat(64)},
    metrics:{total_wall_seconds:0}, backend:{id:'fixture',mode:'cold'}, outcomes:{verified:1},
    attempt_status:{timeout:1}, sources:{summary:{path:'fixtures/summary.json',sha256:'b'.repeat(64)}}};
}

test('comparison gates mismatched, incomplete, unknown and fixture receipts', () => {
  const {dom} = setup();
  const reasons = dom.window.ui.comparisonReasons;
  const a = comparisonFixture('a'), b = comparisonFixture('b');
  assert.equal(reasons(a,b).length, 0);
  assert.match(reasons(a,{...b,manifest_sha256:'different'}).join(' '), /manifests differ/);
  assert.match(reasons(a,{...b,complete:false}).join(' '), /incomplete/);
  assert.match(reasons(a,{...b,verification:'unknown'}).join(' '), /Verification/);
  assert.match(reasons(a,{...b,fixture:true}).join(' '), /not performance evidence/);
  assert.match(reasons(a,a).join(' '), /different receipts/);
  dom.window.close();
});

test('comparison is selectable, deep linked, source linked, and safe to render', async () => {
  const {dom, calls} = setup();
  dom.window.ui.state.ready = true;
  const a = comparisonFixture('a'), b = comparisonFixture('b');
  b.label = '<script>unsafe</script>';
  dom.window.fetch = async url => { calls.push(url); return {ok:true,json:async()=>({receipts:[a,b],errors:[]})}; };
  await dom.window.ui.viewCompare(new dom.window.URLSearchParams('a=a&b=b'));
  const doc = dom.window.document;
  assert.match(calls[0], /\/crypto-autoresearcher\/data\/comparisons.json$/);
  assert.match(doc.querySelector('table').textContent, /0s/);
  assert.match(doc.querySelector('table').textContent, /1 timeout/);
  assert.equal(doc.querySelector('table script'), null);
  assert.match(doc.querySelector('table a').href, /\/blob\/abc123\/fixtures\/summary\.json$/);
  const second = doc.querySelector('[aria-label="Second run"]');
  second.value = 'a'; second.dispatchEvent(new dom.window.Event('change', {bubbles:true}));
  assert.match(dom.window.location.hash, /a=a&b=a/);
  assert.match(doc.querySelector('[aria-live]').textContent, /different receipts/);
  dom.window.close();
});

test('comparison empty state and transient failure are recoverable', async () => {
  const {dom} = setup();
  dom.window.ui.state.ready = true;
  let fail = true;
  dom.window.fetch = async () => { if (fail) { fail=false; throw new Error('offline'); }
    return {ok:true,json:async()=>({receipts:[],errors:[]})}; };
  await dom.window.ui.viewCompare();
  assert.match(dom.window.document.querySelector('[role=alert]').textContent, /could not be loaded/);
  [...dom.window.document.querySelectorAll('button')].find(b=>b.textContent==='Retry').click();
  await settle();
  assert.match(dom.window.document.querySelector('.empty').textContent, /No archived comparison receipts/);
  dom.window.close();
});

test('experiment totals render recorded zero as zero and unknown as a dash', async () => {
  const {dom} = setup();
  const ui = dom.window.ui;
  ui.state.ready = true;
  const common = {status:'completed',run_count:1,runs_timed:0,runs_measured:1,dated:'',contract:'specification.yaml',
    runs:[{id:'zero',status:'completed',duration_seconds:0}]};
  ui.state.experimentsPayload = {experiments:[{...common,id:'EXP-ZERO',title:'zero duration',total_seconds:0},
    {...common,id:'EXP-UNKNOWN',title:'unknown duration',total_seconds:null}],
    timing:{runs:2,runs_with_duration:1,total_measured_seconds:0,git:{available:false}}};
  await ui.viewExperiments(new dom.window.URLSearchParams());
  const rows = [...dom.window.document.querySelectorAll('tr')];
  assert.match(rows.find(r=>r.textContent.includes('EXP-ZERO')).textContent, /0s/);
  assert.doesNotMatch(rows.find(r=>r.textContent.includes('EXP-UNKNOWN')).textContent, /0s/);
  assert.match(dom.window.document.querySelector('.stat-row').textContent, /0stotal measured/);
  dom.window.close();
});
