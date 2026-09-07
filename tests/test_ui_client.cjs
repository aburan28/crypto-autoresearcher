const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('../ui/node_modules/jsdom');
const root = path.resolve(__dirname, '..');
const app = fs.readFileSync(path.join(root, 'ui/static/app.js'), 'utf8')
  .replace(/initChrome\(\);\s*renderNav\(\);\s*route\(\);\s*boot\(\);\s*$/, 'window.ui = {viewRecord, state};');
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
