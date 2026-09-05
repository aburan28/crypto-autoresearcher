/* autoresearch UI — vanilla JS, no build step, no external dependencies.
 *
 * One app, two hosts. It reads a directory of JSON files under `data/`,
 * which `ui/build.py` writes for GitHub Pages and `ui/server.py` computes
 * live from the working tree. Paths are RELATIVE so the same bundle works
 * at a project-pages base (`/crypto-autoresearcher/`) and at the root.
 *
 * A static host cannot answer a query, so nothing here asks one: the whole
 * summary index is loaded once (~0.8 MB gzipped) and every filter, sort and
 * search runs in the browser.
 *
 * The app is a reader. Its only non-GET is `api/refresh` against the local
 * server. Nothing here can change research state: that authority belongs to
 * the Coordinator, through the ledger.
 */
'use strict';

// ---------------------------------------------------------------------------
// DOM helpers
// ---------------------------------------------------------------------------
function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k === 'text') el.textContent = v;
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? '' : v);
  }
  for (const kid of kids.flat(9)) {
    if (kid === null || kid === undefined || kid === false) continue;
    el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return el;
}
const $ = (sel) => document.querySelector(sel);
const clear = (el) => { while (el.firstChild) el.removeChild(el.firstChild); return el; };

/** Replace an element's children, flattening arrays the way h() does.
 *  Node.append() stringifies an array it is handed, so `el.append(rows.map(f))`
 *  renders "[object HTMLDivElement],…" instead of the rows. Every re-render
 *  goes through here so that cannot happen. */
function fill(el, ...kids) {
  clear(el);
  for (const kid of kids.flat(9)) {
    if (kid === null || kid === undefined || kid === false) continue;
    el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return el;
}

// `data/` sits beside index.html. Resolving against the document keeps the
// bundle base-path agnostic: project pages serve it from /<repo>/.
const DATA = new URL('data/', document.baseURI).href;
const cache = new Map();

async function getJSON(rel, { cached = true } = {}) {
  if (cached && cache.has(rel)) return cache.get(rel);
  const res = await fetch(DATA + rel, { cache: 'no-cache' });
  if (!res.ok) {
    const err = new Error(`${rel}: ${res.status}`);
    err.status = res.status;
    throw err;
  }
  const body = await res.json();
  if (cached) cache.set(rel, body);
  return body;
}

// ---------------------------------------------------------------------------
// Vocabulary: how a status is coloured. One place, so a status means the
// same thing on every screen.
// ---------------------------------------------------------------------------
let KIND_LABEL = {
  GOAL: 'goals', RQ: 'questions', IDEA: 'proposals', H: 'hypotheses',
  EXP: 'experiments', RUN: 'runs', EV: 'evidence', DEC: 'decisions',
  TASK: 'handoffs', BATCH: 'checkpoints', CORR: 'corrections', KN: 'knowledge',
  OTHER: 'other',
};
const TERMINAL = new Set(['completed', 'closed_at_budget', 'cancelled']);

function statusTone(status) {
  const s = (status || '').toLowerCase();
  if (!s) return '';
  if (s === 'paused' || s === 'blocked') return 'bad';         // forbidden for goals
  if (['active', 'running', 'approved', 'supported', 'completed_valid', 'replicated',
       'validated'].includes(s)) return 'ok';
  if (['completed', 'analyzed', 'specified', 'frozen'].includes(s)) return 'info';
  if (['draft', 'proposed', 'speculative', 'pending', 'inconclusive',
       'unstated'].includes(s)) return 'warn';
  if (['rejected', 'rejected_scoped', 'refuted', 'failed', 'unparseable', 'cancelled',
       'error', 'no-manifest', 'unreadable'].includes(s)) return 'bad';
  return '';
}
const tag = (text, tone, title) =>
  h('span', { class: `tag ${tone || ''}`, title: title || '' }, text);
const statusTag = (status) => status ? tag(status, statusTone(status)) : null;

// ---------------------------------------------------------------------------
// Identifier linking. Mirrors RECORD_ID_RE in ui/scan.py: the second segment
// is an area token for most kinds but a date for DEC/IDEA/TASK/CORR and a
// bare token for BATCH, so it cannot be required to start with a letter.
// ---------------------------------------------------------------------------
const ID_RE = /\b(?:GOAL|RQ|IDEA|EXP|RUN|EV|DEC|TASK|BATCH|CORR|KN|H)-[A-Za-z0-9]{1,20}(?:-[A-Za-z0-9]{1,32}){0,2}\b/g;

function idLink(id, extra) {
  const href = id.startsWith('GOAL-') && !id.includes('~')
    ? `#/goal/${id}` : `#/record/${id}`;
  return h('a', { class: `id-link ${extra || ''}`, href }, id);
}

/** Free text with known identifiers linked. One that names nothing stays
 *  plain text — which is how a dangling reference shows itself while you
 *  are reading, rather than only in a report. */
function linkify(text) {
  const frag = document.createDocumentFragment();
  const src = String(text ?? '');
  let last = 0;
  for (const m of src.matchAll(ID_RE)) {
    if (!state.byId.has(m[0])) continue;
    if (m.index > last) frag.append(src.slice(last, m.index));
    frag.append(idLink(m[0]));
    last = m.index + m[0].length;
  }
  if (last < src.length) frag.append(src.slice(last));
  return frag;
}

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const state = {
  meta: null,
  records: [],                 // decoded index rows, in file order
  byId: new Map(),
  overview: null, goals: null, experiments: null,
  searchShards: new Map(),     // kind -> Map(id -> excerpt)
  ready: false,
  fatal: null,
};

const view = () => $('#view');
const setCrumb = (t) => { $('#crumb').textContent = t || ''; };
const loading = (label) => h('div', { class: 'empty row', style: 'justify-content:center' },
  h('span', { class: 'spin' }), ' ', label || 'loading…');

/** data/index.json rows are positional; name them once, here. */
function rowToRecord(row) {
  const [id, kind, status, title, date, area, ecc, backlinks] = row;
  return { id, kind, status, title, date, area: area || null, ecc: !!ecc, backlinks };
}

function sourceUrl(path) {
  const { repo_url: repo, commit } = state.meta || {};
  if (!repo || !path) return null;
  return `${repo}/blob/${commit || 'HEAD'}/${path}`;
}

// ---------------------------------------------------------------------------
// Chrome
// ---------------------------------------------------------------------------
const NAV = [
  { route: '#/', label: 'Portfolio' },
  { route: '#/goals', label: 'Goals', count: (s) => s.goals?.length },
  { route: '#/records', label: 'Records', count: (s) => s.records.length },
  { route: '#/experiments', label: 'Experiments', count: (s) => s.meta?.experiments },
  { route: '#/integrity', label: 'Integrity', count: (s) => s.overview
      ? Object.entries(s.overview.integrity_totals)
          .filter(([k]) => !k.endsWith('_state'))
          .reduce((a, [, v]) => a + (v || 0), 0)
      : null },
];

function renderNav() {
  const here = location.hash || '#/';
  const nav = clear($('#nav'));
  for (const item of NAV) {
    const active = here === item.route ||
      (item.route !== '#/' && here.startsWith(item.route)) ||
      (item.route === '#/goals' && here.startsWith('#/goal/')) ||
      (item.route === '#/records' && here.startsWith('#/record/'));
    const n = item.count ? item.count(state) : null;
    nav.append(h('a', { class: 'nav-item', href: item.route, 'aria-current': active },
      h('span', {}, item.label),
      n === null || n === undefined ? null : h('span', { class: 'n' }, n.toLocaleString())));
  }
}

function renderFooter() {
  const m = state.meta;
  const el = clear($('#build-state'));
  if (!m) { el.append('starting…'); return; }
  if (m.state === 'building') {
    el.append(h('span', { class: 'spin' }), ` indexing… ${m.elapsed ?? 0}s`);
    return;
  }
  if (m.state === 'error') { el.append(tag('index failed', 'bad')); return; }
  el.append(h('span', {}, `${(m.records || 0).toLocaleString()} records`));
  if (m.mode === 'live' && m.deep_scan === 'running') {
    el.append(h('span', { class: 'faint', title: 'exact YAML parse of every ledger record' },
      ' · deep scan…'));
  }
  $('#refresh').hidden = m.mode !== 'live';
  $('#brand-sub').textContent = m.mode === 'static' ? 'snapshot · read-only' : 'live · read-only';
}

/** A published page is a snapshot of one commit and has to say so.
 *  A reader comparing it against their working tree needs to know which. */
function snapshotBanner() {
  const m = state.meta;
  if (!m || m.mode !== 'static') return null;
  const short = (m.commit || '').slice(0, 7);
  const when = m.built_at ? m.built_at.replace('T', ' ').replace('+00:00', ' UTC') : 'unknown';
  return h('div', { class: 'banner info', style: 'margin-bottom:14px' },
    h('div', {},
      h('b', {}, 'Snapshot, not live. '),
      'Built ', h('span', { class: 'mono' }, when), ' from ',
      m.repo_url && m.commit
        ? h('a', { class: 'mono', href: `${m.repo_url}/commit/${m.commit}`,
                   target: '_blank', rel: 'noreferrer' }, short)
        : h('span', { class: 'mono' }, short || 'an unknown commit'),
      '. Records committed after that are not here; every source link points at that commit.'));
}

// ---------------------------------------------------------------------------
// Shared pieces
// ---------------------------------------------------------------------------
function statCard(value, label, opts = {}) {
  return h('div', {
    class: `stat ${opts.alert ? 'alert' : ''} ${opts.href ? 'clickable' : ''}`,
    title: opts.title || '',
    onclick: opts.href ? () => { location.hash = opts.href; } : null,
  }, h('div', { class: 'v' }, value), h('div', { class: 'k' }, label));
}

function goalCard(goal) {
  const classes = ['goal-card'];
  if (goal.ecc) classes.push('ecc');
  if (goal.flags?.length) classes.push('flagged');
  if (goal.terminal) classes.push('terminal');
  return h('div', {
    class: classes.join(' '),
    onclick: () => { location.hash = `#/goal/${goal.id}`; },
  },
    h('div', { class: 'spread' },
      h('span', { class: 'id-link' }, goal.id),
      h('div', { class: 'row' },
        goal.ecc ? tag('ECC', 'acc', 'ECC areas are selected first (CLAUDE.md rule 11)') : null,
        statusTag(goal.status))),
    h('h4', { class: 'clamp3' }, goal.title || h('span', { class: 'faint' }, '(no title)')),
    goal.next_action_preview
      // The clamp goes on an inner element: overflow:hidden clips at the
      // PADDING box, so clamping the padded box lets the next line show
      // through the bottom padding as a sliver of ascenders.
      ? h('div', { class: 'next-action' },
          h('div', { class: 'clamp3' }, linkify(goal.next_action_preview)))
      : null,
    h('div', { class: 'row faint mono', style: 'font-size:11px' },
      goal.current_batch_id ? `batch ${goal.current_batch_id}` : null,
      goal.batches ? `· ${goal.batches} checkpoint${goal.batches === 1 ? '' : 's'}` : null,
      goal.updated_at ? `· updated ${goal.updated_at}` : null,
      goal.budget?.maximum_batches === null && goal.budget?.total_wall_clock_seconds === null
        ? h('span', { class: 'tag ok', title: 'unbounded campaign budget' }, '∞ budget') : null),
    goal.flags?.length
      ? h('div', { class: 'banner bad', style: 'font-size:11px' }, goal.flags.join(' · '))
      : null,
    goal.impediment_count
      ? h('div', { class: 'row' },
          tag(`${goal.impediment_count} impediment${goal.impediment_count === 1 ? '' : 's'}`,
              'warn', 'Recorded impediment — the goal stays active (CLAUDE.md rule 10)'))
      : null);
}

function recordTable(records, opts = {}) {
  if (!records.length) return h('div', { class: 'empty' }, 'nothing matches');
  return h('table', {},
    h('thead', {}, h('tr', {},
      h('th', {}, 'id'), h('th', {}, 'kind'), h('th', {}, 'status'),
      h('th', {}, 'title'), opts.compact ? null : h('th', {}, 'area'),
      h('th', {}, 'date'),
      opts.compact ? null : h('th', { title: 'records citing this one' }, 'in'))),
    h('tbody', {}, records.map((r) => h('tr', {},
      h('td', {}, idLink(r.id)),
      h('td', { class: 'faint mono', style: 'font-size:11px' }, KIND_LABEL[r.kind] || r.kind),
      h('td', {}, statusTag(r.status) || h('span', { class: 'faint' }, '—')),
      h('td', { style: 'max-width:640px' },
        h('div', { class: 'clamp2' }, r.title || h('span', { class: 'faint' }, '(no title)'))),
      opts.compact ? null : h('td', {},
        r.area
          ? h('a', { href: `#/records?area=${r.area}`, class: 'mono' },
              r.ecc ? h('span', { class: 'tag acc' }, r.area) : r.area)
          : h('span', { class: 'faint' }, '—')),
      h('td', { class: 'mono faint', style: 'white-space:nowrap' }, r.date || '—'),
      opts.compact ? null : h('td', { class: 'mono faint' }, r.backlinks || '')))));
}

const resolve = (ids) => ids.map((id) => state.byId.get(id)).filter(Boolean);

function distribution(map, kind) {
  const entries = Object.entries(map || {}).sort((a, b) => b[1] - a[1]);
  if (!entries.length) return h('div', { class: 'faint' }, 'nothing recorded');
  const total = entries.reduce((a, [, v]) => a + v, 0);
  return h('div', { class: 'stack', style: 'gap:7px' }, entries.map(([name, n]) => {
    const tone = statusTone(name);
    const colour = tone ? `var(--${tone})` : 'var(--line-strong)';
    return h('div', { class: 'row', style: 'gap:10px' },
      h('div', { style: 'flex:0 0 175px;min-width:0' },
        kind
          ? h('a', { href: `#/records?kind=${kind}&status=${encodeURIComponent(name)}`,
                     class: 'mono' }, name)
          : h('span', { class: 'mono' }, name)),
      h('div', { class: 'bar', style: 'flex:1' },
        h('i', { style: `width:${(n / total) * 100}%;background:${colour}` })),
      h('span', { class: 'mono faint', style: 'flex:0 0 52px;text-align:right' }, n));
  }));
}

// ---------------------------------------------------------------------------
// Portfolio
// ---------------------------------------------------------------------------
async function viewOverview() {
  setCrumb('portfolio');
  const root = fill(view(), loading('building the index…'));
  if (!state.ready) return;
  state.overview ??= await getJSON('overview.json');
  const o = state.overview;

  const goalStats = h('div', { class: 'stat-row' },
    statCard(o.goals.active, 'active goals', { href: '#/goals' }),
    statCard(o.goals.ecc_active, 'ECC active',
      { title: 'ECC comes first at every selection point' }),
    statCard(o.goals.terminal, 'retired'),
    statCard(o.experiments.total.toLocaleString(), 'experiments', { href: '#/experiments' }),
    statCard(o.experiments.runs.toLocaleString(), 'runs'),
    statCard(o.integrity_totals.unparseable_state === 'complete'
      ? o.integrity_totals.unparseable : '…', 'unparseable',
      { href: '#/integrity', alert: o.integrity_totals.unparseable > 0,
        title: o.integrity_totals.unparseable_state === 'complete'
          ? 'ledger records that do not parse' : 'deep scan still running' }));

  const counts = h('div', { class: 'stat-row' },
    ...o.counts.filter((c) => c.count).map((c) =>
      statCard(c.count.toLocaleString(), c.label,
        { href: `#/records?kind=${c.key}`, title: `browse ${c.label}` })));

  const cardGrid = (goals) => h('div', { class: 'panel-body grid',
    style: 'grid-template-columns:repeat(auto-fill,minmax(300px,1fr))' }, goals.map(goalCard));

  fill(root, h('div', { class: 'stack' },
    snapshotBanner(),
    goalStats, counts,
    h('section', { class: 'panel' },
      h('div', { class: 'panel-head' }, h('h3', {}, 'ECC first'),
        h('a', { href: '#/goals', class: 'faint' }, 'all goals →')),
      o.ecc_first.length ? cardGrid(o.ecc_first)
        : h('div', { class: 'empty' }, 'no active ECC goals')),
    o.attention.length ? h('section', { class: 'panel' },
      h('div', { class: 'panel-head' }, h('h3', {}, 'Wants attention'),
        h('span', { class: 'faint' }, 'flagged, or carrying a recorded impediment')),
      cardGrid(o.attention)) : null,
    h('div', { class: 'grid', style: 'grid-template-columns:repeat(auto-fit,minmax(320px,1fr))' },
      h('section', { class: 'panel' },
        h('div', { class: 'panel-head' }, h('h3', {}, 'Hypotheses by status')),
        h('div', { class: 'panel-body' }, distribution(o.hypothesis_status, 'H'))),
      h('section', { class: 'panel' },
        h('div', { class: 'panel-head' }, h('h3', {}, 'Runs by terminal status')),
        h('div', { class: 'panel-body' }, distribution(o.run_status, null)))),
    h('section', { class: 'panel' },
      h('div', { class: 'panel-head' }, h('h3', {}, 'Latest records'),
        h('span', { class: 'faint' }, 'decisions, evidence, handoffs, corrections')),
      h('div', { class: 'scroll-x' }, recordTable(resolve(o.recent), { compact: true })))));
}

// ---------------------------------------------------------------------------
// Goals
// ---------------------------------------------------------------------------
async function viewGoals() {
  setCrumb('goals');
  const root = fill(view(), loading());
  if (!state.ready) return;
  state.goals ??= (await getJSON('goals.json')).goals;

  const filters = { text: '', only: 'active' };
  const grid = h('div', { class: 'grid',
    style: 'grid-template-columns:repeat(auto-fill,minmax(310px,1fr))' });
  const summary = h('div', { class: 'faint mono' });

  function draw() {
    const needle = filters.text.toLowerCase();
    const rows = state.goals.filter((g) => {
      if (filters.only === 'active' && g.status !== 'active') return false;
      if (filters.only === 'ecc' && !(g.ecc && g.status === 'active')) return false;
      if (filters.only === 'attention' && !(g.flags?.length || g.impediment_count)) return false;
      if (filters.only === 'retired' && !g.terminal) return false;
      if (!needle) return true;
      return `${g.id} ${g.title} ${g.area} ${g.next_action_preview}`.toLowerCase()
        .includes(needle);
    });
    fill(grid, rows.length ? rows.map(goalCard) : h('div', { class: 'empty' }, 'no goals match'));
    summary.textContent = `${rows.length} of ${state.goals.length} goals`;
  }

  const chip = (key, label, title) => {
    const el = h('button', { class: 'chip', 'aria-pressed': filters.only === key,
                             title: title || '' }, label);
    el.addEventListener('click', () => {
      filters.only = key;
      for (const c of el.parentElement.children) c.setAttribute('aria-pressed', c === el);
      draw();
    });
    return el;
  };

  fill(root, h('div', { class: 'stack' },
    snapshotBanner(),
    h('div', { class: 'spread' },
      h('div', { class: 'chip-row' },
        chip('active', 'active'),
        chip('ecc', 'ECC active', 'ECC goals are selected before all others'),
        chip('attention', 'wants attention'),
        chip('retired', 'retired'),
        chip('all', 'all')),
      h('div', { class: 'row' }, summary,
        h('input', { class: 'mono field', placeholder: 'filter goals…',
                     oninput: (e) => { filters.text = e.target.value; draw(); } }))),
    grid));
  draw();
}

async function viewGoal(id) {
  setCrumb(id);
  const root = fill(view(), loading());
  let goal;
  try {
    goal = await getJSON(`goals/${encodeURIComponent(id)}.json`);
  } catch {
    fill(root, h('div', { class: 'banner bad' }, `unknown goal ${id}`));
    return;
  }

  const head = h('section', { class: 'panel' },
    h('div', { class: 'panel-body stack', style: 'gap:10px' },
      h('div', { class: 'spread' },
        h('div', { class: 'row' },
          h('b', { class: 'id-link', style: 'font-size:14px' }, goal.id),
          goal.ecc ? tag('ECC', 'acc') : null, statusTag(goal.status),
          goal.owner ? tag(goal.owner) : null),
        h('div', { class: 'row' },
          sourceUrl(goal.path)
            ? h('a', { class: 'faint mono', href: sourceUrl(goal.path),
                       target: '_blank', rel: 'noreferrer' }, 'source ↗') : null,
          h('a', { class: 'faint mono', href: `#/records?q=${encodeURIComponent(goal.id)}` },
            `${goal.mentions.length} mentions →`))),
      h('h2', { style: 'font-size:17px;line-height:1.35' }, goal.title),
      goal.flags?.length ? h('div', { class: 'banner bad' },
        h('div', {}, h('b', {}, 'flagged'), ' ', goal.flags.join(' · '))) : null,
      h('dl', { class: 'kv' },
        kv('path', h('code', {}, goal.path)),
        kv('batch', goal.current_batch_id || '—'),
        kv('updated', goal.updated_at || '—'),
        kv('created', goal.created_at || '—'),
        kv('layout', goal.sharded ? 'sharded (checkpoints/)' : 'flat'),
        kv('budget', budgetLine(goal.budget)))));

  const panel = (title, note, body) => body ? h('section', { class: 'panel' },
    h('div', { class: 'panel-head' }, h('h3', {}, title),
      note ? h('span', { class: 'faint' }, note) : null), body) : null;

  fill(root, h('div', { class: 'stack' },
    snapshotBanner(), head,
    panel('Next action', null, goal.next_action
      ? h('div', { class: 'panel-body' },
          h('div', { class: 'next-action', style: 'font-size:12px' },
            linkify(goal.next_action))) : null),
    panel('Objective', null, goal.objective
      ? h('div', { class: 'panel-body', style: 'line-height:1.65' },
          linkify(goal.objective)) : null),
    panel('Completion criteria',
      'a committed Coordinator decision showing one was met closes the goal',
      goal.completion_criteria?.length
        ? h('div', { class: 'panel-body' }, yamlTree(goal.completion_criteria)) : null),
    panel('Impediments', 'recorded, not paused', goal.impediments?.length
      ? h('div', { class: 'panel-body' }, yamlTree(goal.impediments)) : null),
    panel(`Batch checkpoints (${goal.checkpoints.length})`, 'write-once',
      goal.checkpoints.length ? h('div', { class: 'scroll-x' }, h('table', {},
        h('thead', {}, h('tr', {}, h('th', {}, 'batch'), h('th', {}, 'recorded'),
          h('th', {}, 'summary'))),
        h('tbody', {}, goal.checkpoints.map((c) => h('tr', {},
          h('td', { class: 'mono' }, c.batch_id || '—'),
          h('td', { class: 'mono faint' }, c.recorded_at || '—'),
          h('td', {}, h('div', { class: 'clamp3' }, linkify(c.summary || '—')))))))) : null),
    h('section', { class: 'panel' },
      h('div', { class: 'panel-head' }, h('h3', {}, 'Bound records')),
      h('div', { class: 'panel-body stack' },
        linkedBlock('research questions', goal.question_ids),
        linkedBlock('active hypotheses', goal.active_hypothesis_ids)))));
}

function linkedBlock(label, ids) {
  const head = h('div', { class: 'faint',
    style: 'text-transform:uppercase;font-size:10px;letter-spacing:.07em' }, label);
  if (!ids?.length) return h('div', {}, head, h('div', { class: 'faint' }, 'none'));
  const found = resolve(ids);
  const missing = ids.filter((id) => !state.byId.has(id));
  return h('div', { class: 'stack', style: 'gap:6px' }, head,
    found.length ? h('div', { class: 'scroll-x' }, recordTable(found, { compact: true })) : null,
    missing.length ? h('div', { class: 'banner warn', style: 'font-size:11px' },
      `named but not found in the ledger: ${missing.join(', ')}`) : null);
}

function budgetLine(budget) {
  if (!budget) return '—';
  const unbounded = budget.maximum_batches === null && budget.total_wall_clock_seconds === null;
  const parts = [
    budget.maximum_batches === null ? 'batches ∞' : `batches ≤ ${budget.maximum_batches}`,
    budget.total_wall_clock_seconds === null
      ? 'wall-clock ∞' : `wall-clock ≤ ${budget.total_wall_clock_seconds}s`,
  ];
  if (budget.max_concurrent !== null && budget.max_concurrent !== undefined) {
    parts.push(`max_concurrent ${budget.max_concurrent}`);
  }
  return h('span', { class: 'row' }, h('span', { class: 'mono' }, parts.join(' · ')),
    unbounded ? tag('unbounded', 'ok') : null);
}

const kv = (key, value) => h('div', { style: 'display:contents' },
  h('dt', {}, key), h('dd', {}, value));

// ---------------------------------------------------------------------------
// Records browser — every filter runs here, over the loaded index.
// ---------------------------------------------------------------------------
const PAGE = 100;

async function loadShards(kinds) {
  // Only kinds the index actually holds. `KIND_LABEL` names every kind the
  // schema allows, including ones with no records here (`RUN` lives under
  // experiments/, not the ledger), and asking for those shards produced a
  // 404 per search. The facets are the kinds that exist.
  const present = new Set(state.meta.facets.kinds.map((k) => k.key));
  const wanted = [...(kinds.length ? kinds : present)]
    .filter((k) => present.has(k) && !state.searchShards.has(k));
  await Promise.all(wanted.map(async (kind) => {
    const shard = await getJSON(`search/${kind}.json`);
    const map = new Map();
    shard.ids.forEach((id, i) => map.set(id, (shard.text[i] || '').toLowerCase()));
    state.searchShards.set(kind, map);
  }));
}

async function viewRecords(params) {
  setCrumb('records');
  const root = fill(view(), loading());
  if (!state.ready) return;

  const f = {
    q: params.get('q') || '',
    kind: new Set((params.get('kind') || '').split(',').filter(Boolean)),
    area: new Set((params.get('area') || '').split(',').filter(Boolean)),
    status: new Set((params.get('status') || '').split(',').filter(Boolean)),
    bodies: params.get('bodies') === '1',
  };
  $('#q').value = f.q;
  let shown = PAGE;

  const results = h('div', { class: 'panel scroll-x' });
  const meta = h('div', { class: 'faint mono' });
  const more = h('div', {});
  const note = h('div', {});

  function pushRoute() {
    const p = new URLSearchParams();
    if (f.q) p.set('q', f.q);
    for (const key of ['kind', 'area', 'status']) if (f[key].size) p.set(key, [...f[key]].join(','));
    if (f.bodies) p.set('bodies', '1');
    const next = `#/records${p.toString() ? `?${p}` : ''}`;
    if (location.hash !== next) history.replaceState(null, '', next);
  }

  function matches() {
    const needle = f.q.trim().toLowerCase();
    const out = [];
    for (const r of state.records) {
      if (f.kind.size && !f.kind.has(r.kind)) continue;
      if (f.area.size && !f.area.has(r.area)) continue;
      if (f.status.size && !f.status.has(r.status)) continue;
      if (!needle) { out.push(r); continue; }
      const name = `${r.id} ${r.title} ${r.status} ${r.area || ''}`.toLowerCase();
      if (name.includes(needle)) { out.push(r); continue; }
      if (f.bodies) {
        const shard = state.searchShards.get(r.kind);
        if (shard && (shard.get(r.id) || '').includes(needle)) out.push(r);
      }
    }
    // Identifier matches outrank a title match, which outranks a body hit;
    // then newest first.
    const rank = (r) => !needle ? 1
      : r.id.toLowerCase().includes(needle) ? 0
      : (r.title || '').toLowerCase().includes(needle) ? 1 : 2;
    out.sort((a, b) => rank(a) - rank(b) ||
      (b.date || '').localeCompare(a.date || '') || a.id.localeCompare(b.id));
    return out;
  }

  function draw() {
    const rows = matches();
    meta.textContent = `${rows.length.toLocaleString()} matching · showing ${
      Math.min(shown, rows.length).toLocaleString()}`;
    fill(results, recordTable(rows.slice(0, shown)));
    fill(more, shown < rows.length
      ? h('button', { class: 'btn',
          onclick: () => { shown += PAGE * 5; draw(); } },
          `show ${Math.min(PAGE * 5, rows.length - shown).toLocaleString()} more`)
      : null);
  }

  async function setBodies(on) {
    f.bodies = on;
    if (!on) { pushRoute(); draw(); return; }
    fill(note, h('div', { class: 'banner info', style: 'font-size:11.5px' },
      h('span', { class: 'spin' }), ' loading body excerpts…'));
    await loadShards([...f.kind]);
    const chars = 1200;
    fill(note, h('div', { class: 'banner info', style: 'font-size:11.5px' },
      `Searching the first ${chars} characters of each record body. Full source is on GitHub.`));
    pushRoute(); draw();
  }

  const facetRow = (label, group, items, render) => h('div', { class: 'stack', style: 'gap:6px' },
    h('div', { class: 'faint',
      style: 'text-transform:uppercase;font-size:10px;letter-spacing:.07em' }, label),
    h('div', { class: 'chip-row' }, items.map((item) => {
      const el = h('button', { class: 'chip', 'aria-pressed': f[group].has(item.key) },
        render(item));
      el.addEventListener('click', () => {
        f[group].has(item.key) ? f[group].delete(item.key) : f[group].add(item.key);
        el.setAttribute('aria-pressed', f[group].has(item.key));
        shown = PAGE; pushRoute(); draw();
      });
      return el;
    })));

  const facets = state.meta.facets;
  const bodiesChip = h('button', { class: 'chip', 'aria-pressed': f.bodies,
    title: 'Also search record bodies. Loads excerpt shards on demand.' }, 'search bodies');
  bodiesChip.addEventListener('click', () => {
    const on = bodiesChip.getAttribute('aria-pressed') !== 'true';
    bodiesChip.setAttribute('aria-pressed', on);
    setBodies(on);
  });

  fill(root, h('div', { class: 'stack' },
    snapshotBanner(),
    h('section', { class: 'panel' }, h('div', { class: 'panel-body stack', style: 'gap:12px' },
      facetRow('kind', 'kind', facets.kinds, (i) => `${i.label} ${i.count.toLocaleString()}`),
      facetRow('area', 'area', facets.areas.slice(0, 60), (i) =>
        h('span', {}, i.ecc ? h('span', { class: 'tag acc', style: 'margin-right:4px' }, 'ECC') : null,
          `${i.key} ${i.count}`)),
      facetRow('status', 'status', facets.statuses.slice(0, 40),
        (i) => `${i.key} ${i.count.toLocaleString()}`))),
    note,
    h('div', { class: 'spread' },
      h('div', { class: 'row' }, meta, bodiesChip),
      h('button', { class: 'btn', onclick: () => { location.hash = '#/records'; route(); } },
        'clear filters')),
    results, more));

  pushRoute();
  if (f.bodies) await setBodies(true); else draw();
}

// ---------------------------------------------------------------------------
// Record detail
// ---------------------------------------------------------------------------
async function viewRecord(id) {
  setCrumb(id);
  const root = fill(view(), loading());
  let body;
  try {
    body = await getJSON(`records/${encodeURIComponent(id)}.json`);
  } catch {
    fill(root, h('div', { class: 'banner bad' },
      h('div', {}, h('b', {}, `${id} is not in the index. `),
        'It may be a run, a coordination task, or a dangling reference.')));
    return;
  }
  const s = body.summary;
  const src = sourceUrl(s.path);

  const panes = {};
  const paneHost = h('div', { class: 'panel-body' });
  const tabs = h('div', { class: 'tabs' });
  function show(key) {
    fill(paneHost, panes[key] ??= buildPane(key, body, src));
    for (const t of tabs.children) t.setAttribute('aria-selected', t.dataset.key === key);
  }
  for (const [key, label] of [
    ['structured', 'record'], ['source', 'source'],
    ['links', `links (${body.links.out.length}↗ ${body.links.in.length}↙)`],
  ]) {
    tabs.append(h('button', { class: 'tab', 'data-key': key, onclick: () => show(key) }, label));
  }

  const linkList = (title, ids) => h('section', { class: 'panel' },
    h('div', { class: 'panel-head' }, h('h3', {}, `${title} (${ids.length})`)),
    h('div', { class: 'panel-body stack', style: 'gap:5px;max-height:420px;overflow:auto' },
      ids.length
        ? ids.map((rid) => {
            const r = state.byId.get(rid);
            return h('div', { class: 'row', style: 'gap:6px' },
              idLink(rid), r ? statusTag(r.status) : null);
          })
        : h('span', { class: 'faint' }, 'none')));

  fill(root, h('div', { class: 'stack' },
    snapshotBanner(),
    !body.verified && body.parse_error
      ? h('div', { class: 'banner bad' },
          h('div', {}, h('b', {}, 'this record does not parse. '), body.parse_error,
            h('div', { class: 'faint', style: 'margin-top:4px' },
              'Reported, not repaired: records are immutable and a correction supersedes them.')))
      : null,
    h('section', { class: 'panel' },
      h('div', { class: 'panel-body stack', style: 'gap:9px' },
        h('div', { class: 'spread' },
          h('div', { class: 'row' },
            h('b', { class: 'id-link', style: 'font-size:14px' }, s.id),
            tag(KIND_LABEL[s.kind] || s.kind),
            s.area ? h('a', { href: `#/records?area=${s.area}` },
              s.ecc ? tag(s.area, 'acc') : tag(s.area)) : null,
            statusTag(s.status),
            s.date ? h('span', { class: 'faint mono' }, s.date) : null),
          body.verified
            ? tag('parsed', 'ok', 'A real YAML parse of the record on disk')
            : tag('parse failed', 'bad', body.parse_error || '')),
        s.title ? h('h2', { style: 'font-size:16px;line-height:1.4' }, s.title) : null,
        h('div', { class: 'row faint mono', style: 'font-size:11px' },
          h('span', {}, s.path),
          src ? h('a', { href: src, target: '_blank', rel: 'noreferrer' }, 'source ↗') : null))),
    h('div', { class: 'detail' },
      h('section', { class: 'panel' }, tabs, paneHost),
      h('aside', { class: 'stack' },
        linkList('Cited by', body.links.in), linkList('Cites', body.links.out)))));
  show('structured');
}

function buildPane(key, body, src) {
  if (key === 'source') {
    // The live server inlines the file; the published snapshot links it on
    // GitHub at the built commit rather than shipping 116 MB of YAML.
    if (typeof body.raw === 'string') return h('pre', { class: 'raw' }, body.raw);
    return h('div', { class: 'empty stack', style: 'gap:10px' },
      h('div', {}, 'Source text is not bundled into the published snapshot.'),
      src ? h('a', { class: 'btn', href: src, target: '_blank', rel: 'noreferrer' },
        `open ${body.summary.path} on GitHub ↗`)
        : h('div', { class: 'faint' }, 'and no repository URL was recorded at build time'));
  }
  if (key === 'links') {
    return h('div', { class: 'stack' },
      h('div', {}, h('h3', { style: 'font-size:12px;margin-bottom:8px' },
        `Cites — ${body.links.out.length}`),
        h('div', { class: 'scroll-x' }, recordTable(resolve(body.links.out)))),
      h('div', {}, h('h3', { style: 'font-size:12px;margin-bottom:8px' },
        `Cited by — ${body.links.in.length}`),
        h('div', { class: 'scroll-x' }, recordTable(resolve(body.links.in)))));
  }
  if (body.body === null || body.body === undefined) {
    return h('div', { class: 'empty' }, 'no parsed body — see the source tab');
  }
  return yamlTree(body.body);
}

/** A parsed record as a collapsible tree, with identifiers linked. */
function yamlTree(value, depth = 0) {
  if (value === null || value === undefined) return h('span', { class: 'yaml-null' }, 'null');
  if (typeof value !== 'object') {
    if (typeof value === 'boolean' || typeof value === 'number') {
      return h('span', { class: 'mono', style: 'color:var(--accent)' }, String(value));
    }
    return h('span', { class: 'yaml-scalar' }, linkify(String(value)));
  }
  if (Array.isArray(value)) {
    if (!value.length) return h('span', { class: 'yaml-null' }, '[]');
    return h('div', { class: depth ? 'yaml-node' : '' },
      value.map((item, i) => h('div', { class: 'yaml-row row',
          style: 'align-items:flex-start;gap:8px' },
        h('span', { class: 'faint mono', style: 'flex:none' }, `${i}`),
        h('div', { style: 'min-width:0;flex:1' }, yamlTree(item, depth + 1)))));
  }
  const entries = Object.entries(value);
  if (!entries.length) return h('span', { class: 'yaml-null' }, '{}');
  return h('div', { class: depth ? 'yaml-node' : '' }, entries.map(([k, v]) => {
    const complex = v && typeof v === 'object' && Object.keys(v).length;
    const bodyEl = h('div', { style: 'min-width:0' }, yamlTree(v, depth + 1));
    if (!complex) {
      return h('div', { class: 'yaml-row row', style: 'align-items:baseline;gap:8px' },
        h('span', { class: 'yaml-key', style: 'flex:none' }, `${k}:`), bodyEl);
    }
    const count = Array.isArray(v) ? `${v.length} items` : `${Object.keys(v).length} keys`;
    return h('div', { class: 'yaml-row' },
      h('details', { open: depth < 1 },
        h('summary', { style: 'cursor:pointer;padding:3px 0' },
          h('span', { class: 'yaml-key' }, `${k}`),
          h('span', { class: 'faint mono', style: 'font-size:10.5px' }, ` ${count}`)),
        bodyEl));
  }));
}

// ---------------------------------------------------------------------------
// Experiments
// ---------------------------------------------------------------------------
async function viewExperiments() {
  setCrumb('experiments');
  const root = fill(view(), loading());
  if (!state.ready) return;
  state.experiments ??= (await getJSON('experiments.json')).experiments;

  let only = 'with-runs';
  let text = '';
  const host = h('div', { class: 'panel scroll-x' });
  const meta = h('div', { class: 'faint mono' });

  function draw() {
    const needle = text.toLowerCase();
    const rows = state.experiments.filter((e) => {
      if (only === 'with-runs' && !e.run_count) return false;
      if (only === 'no-runs' && e.run_count) return false;
      if (only === 'ecc' && !e.ecc) return false;
      return !needle || `${e.id} ${e.title} ${e.status}`.toLowerCase().includes(needle);
    });
    meta.textContent = `${rows.length} of ${state.experiments.length} experiments`;
    fill(host, rows.length ? h('table', {},
      h('thead', {}, h('tr', {}, h('th', {}, 'id'), h('th', {}, 'status'), h('th', {}, 'runs'),
        h('th', {}, 'title'), h('th', {}, 'hypothesis'), h('th', {}, 'frozen'))),
      h('tbody', {}, rows.map((e) => h('tr', {},
        h('td', {}, idLink(e.id)),
        h('td', {}, statusTag(e.status) || h('span', { class: 'faint' }, '—')),
        h('td', {}, runPills(e.runs)),
        h('td', { style: 'max-width:620px' }, h('div', { class: 'clamp2' }, e.title || '—')),
        h('td', {}, e.hypothesis_id && e.hypothesis_id !== 'null'
          ? idLink(e.hypothesis_id) : h('span', { class: 'faint' }, 'none')),
        h('td', {}, e.frozen === 'true' ? tag('frozen', 'info')
          : h('span', { class: 'faint mono' }, e.frozen || '—'))))))
      : h('div', { class: 'empty' }, 'no experiments match'));
  }

  const chip = (key, label) => {
    const el = h('button', { class: 'chip', 'aria-pressed': only === key }, label);
    el.addEventListener('click', () => {
      only = key;
      for (const c of el.parentElement.children) c.setAttribute('aria-pressed', c === el);
      draw();
    });
    return el;
  };

  fill(root, h('div', { class: 'stack' },
    snapshotBanner(),
    h('div', { class: 'spread' },
      h('div', { class: 'chip-row' }, chip('with-runs', 'with runs'), chip('no-runs', 'no runs'),
        chip('ecc', 'ECC'), chip('all', 'all')),
      h('div', { class: 'row' }, meta,
        h('input', { class: 'mono field', placeholder: 'filter…',
                     oninput: (e) => { text = e.target.value; draw(); } }))),
    host));
  draw();
}

function runPills(runs) {
  if (!runs.length) return h('span', { class: 'faint' }, '—');
  const counts = {};
  for (const r of runs) counts[r.status] = (counts[r.status] || 0) + 1;
  return h('span', { class: 'row', style: 'gap:4px' },
    Object.entries(counts).map(([status, n]) => tag(`${n} ${status}`, statusTone(status), status)));
}

// ---------------------------------------------------------------------------
// Integrity
// ---------------------------------------------------------------------------
async function viewIntegrity() {
  setCrumb('integrity');
  const root = fill(view(), loading());
  if (!state.ready) return;
  const body = await getJSON('integrity.json', { cached: state.meta.mode === 'static' });

  const section = (title, note, content) => h('section', { class: 'panel' },
    h('div', { class: 'panel-head' }, h('h3', {}, title),
      note ? h('span', { class: 'faint' }, note) : null), content);
  const table = (headers, rows) => h('div', { class: 'scroll-x' }, h('table', {},
    h('thead', {}, h('tr', {}, headers.map((x) => h('th', {}, x)))),
    h('tbody', {}, rows)));

  const pending = body.unparseable_state !== 'complete';

  fill(root, h('div', { class: 'stack' },
    snapshotBanner(),
    h('div', { class: 'banner info' }, h('div', {},
      h('b', {}, 'Flagged, never fixed. '),
      'Records are immutable and a correction supersedes them — a repair is a Coordinator act, ',
      'and breakage already on main is owned by its campaign, not by whoever is reading this.')),
    body.ecc_policy_error ? h('div', { class: 'banner warn' },
      `ECC priority policy could not be loaded: ${body.ecc_policy_error}. ECC ordering is off.`)
      : null,
    section(`Unparseable ledger records${pending ? '' : ` (${body.unparseable.length})`}`,
      'exact YAML parse of every record under ledger/',
      pending
        ? h('div', { class: 'panel-body' }, loading('deep scan running — not yet measured'))
        : (body.unparseable.length
          ? table(['path', 'parser error'], body.unparseable.map((u) => h('tr', {},
              h('td', { class: 'mono' },
                sourceUrl(u.path)
                  ? h('a', { href: sourceUrl(u.path), target: '_blank', rel: 'noreferrer' }, u.path)
                  : u.path),
              h('td', { class: 'mono faint' }, u.error))))
          : h('div', { class: 'empty' }, 'every ledger record parses'))),
    body.goal_flags.length ? section(`Goal policy flags (${body.goal_flags.length})`,
      'checked against CLAUDE.md rules 10 and 11',
      h('div', { class: 'panel-body stack', style: 'gap:8px' },
        body.goal_flags.map((g) => h('div', { class: 'row' }, idLink(g.id),
          h('span', {}, g.flags.join(' · ')))))) : null,
    section(`Duplicate identifiers (${body.duplicate_ids.length})`,
      'the same id in more than one file — identifiers are immutable and never reused',
      body.duplicate_ids.length
        ? table(['id', 'paths'], body.duplicate_ids.map((d) => h('tr', {},
            h('td', {}, idLink(d.id)),
            h('td', { class: 'mono faint' }, d.paths.join('  ·  ')))))
        : h('div', { class: 'empty' }, 'no duplicates')),
    section(`Dangling references (${body.dangling_refs_total ?? body.dangling_refs.length})`,
      'a GOAL/RQ/H/EXP/EV/DEC/IDEA/KN identifier that is cited but has no record',
      body.dangling_refs.length
        ? table(['identifier', 'times cited'], body.dangling_refs.map((d) => h('tr', {},
            h('td', { class: 'mono' }, d.id), h('td', { class: 'mono faint' }, d.cited_by))))
        : h('div', { class: 'empty' }, 'every cited record exists')),
    section(`Filename does not match id (${body.id_path_mismatch.length})`,
      'cosmetic on its own; a signal when it is unexpected',
      body.id_path_mismatch.length
        ? table(['path', 'declared id'], body.id_path_mismatch.slice(0, 300).map((m) => h('tr', {},
            h('td', { class: 'mono' }, m.path), h('td', {}, idLink(m.id)))))
        : h('div', { class: 'empty' }, 'all filenames match'))));
}

// ---------------------------------------------------------------------------
// Router
// ---------------------------------------------------------------------------
function parseHash() {
  const raw = (location.hash || '#/').slice(1);
  const [path, qs] = raw.split('?');
  return { path: path || '/', params: new URLSearchParams(qs || '') };
}

async function route() {
  const { path, params } = parseHash();
  renderNav();
  try {
    if (state.fatal) {
      fill(view(), h('div', { class: 'banner bad' }, state.fatal));
      return;
    }
    if (path.startsWith('/goal/')) return await viewGoal(decodeURIComponent(path.slice(6)));
    if (path.startsWith('/record/')) return await viewRecord(decodeURIComponent(path.slice(8)));
    if (path === '/goals') return await viewGoals();
    if (path === '/records') return await viewRecords(params);
    if (path === '/experiments') return await viewExperiments();
    if (path === '/integrity') return await viewIntegrity();
    return await viewOverview();
  } catch (err) {
    fill(view(), h('div', { class: 'banner bad' }, String(err)));
  }
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
async function boot() {
  let meta;
  try {
    meta = await getJSON('meta.json', { cached: false });
  } catch (err) {
    state.fatal = `Could not read data/meta.json (${err.message}). ` +
      'Serve this with `make ui`, or build the static bundle with `make ui-build`.';
    renderFooter(); await route(); return;
  }
  state.meta = meta;
  renderFooter();

  if (meta.mode === 'live' && meta.state !== 'ready') {
    if (meta.state === 'error') { state.fatal = `Index build failed: ${meta.error}`; }
    await route();
    setTimeout(boot, 1200);
    return;
  }

  KIND_LABEL = meta.kind_labels || KIND_LABEL;
  const rows = await getJSON('index.json', { cached: false });
  state.records = rows.map(rowToRecord);
  state.byId = new Map(state.records.map((r) => [r.id, r]));
  state.ready = true;
  state.fatal = null;
  renderNav();
  await route();

  // The live server keeps refining while it serves: the exact-parse sweep
  // lands after the index does.
  if (meta.mode === 'live' && meta.deep_scan === 'running') setTimeout(softPoll, 2000);
}

async function softPoll() {
  try {
    state.meta = await getJSON('meta.json', { cached: false });
  } catch { return; }
  renderFooter();
  if (state.meta.deep_scan === 'running') { setTimeout(softPoll, 2000); return; }
  cache.delete('overview.json');
  cache.delete('integrity.json');
  state.overview = null;
  if (['/', '/integrity'].includes(parseHash().path)) route();
}

function initChrome() {
  const stored = localStorage.getItem('autoresearch-theme');
  if (stored) document.documentElement.setAttribute('data-theme', stored);
  $('#theme').addEventListener('click', () => {
    const now = document.documentElement.getAttribute('data-theme');
    const dark = now ? now === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    const next = dark ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('autoresearch-theme', next); } catch { /* private mode */ }
  });

  $('#refresh').addEventListener('click', async () => {
    state.ready = false;
    state.overview = state.goals = state.experiments = null;
    state.searchShards.clear();
    cache.clear();
    await fetch(new URL('api/refresh', document.baseURI), { method: 'POST' }).catch(() => {});
    boot();
  });

  let timer = null;
  $('#q').addEventListener('input', (e) => {
    clearTimeout(timer);
    const value = e.target.value;
    timer = setTimeout(() => {
      const p = new URLSearchParams(parseHash().params);
      if (value) p.set('q', value); else p.delete('q');
      const next = `#/records${p.toString() ? `?${p}` : ''}`;
      if (location.hash === next) route(); else location.hash = next;
    }, 200);
  });

  addEventListener('keydown', (e) => {
    if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
      e.preventDefault(); $('#q').focus(); $('#q').select();
    }
    if (e.key === 'Escape' && document.activeElement === $('#q')) $('#q').blur();
  });

  addEventListener('hashchange', route);
}

initChrome();
renderNav();
route();
boot();
