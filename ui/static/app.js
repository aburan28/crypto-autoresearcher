/* autoresearch UI — vanilla JS, no build step, no external dependencies.
 *
 * The whole app is a reader. There is no POST anywhere except /api/refresh,
 * which re-reads the corpus from disk. Nothing here can change research
 * state: that authority belongs to the Coordinator, through the ledger.
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
    else if (k === 'html') el.innerHTML = v;
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
 *  silently renders "[object HTMLDivElement],…" instead of the rows. Every
 *  re-render goes through here so that cannot happen. */
function fill(el, ...kids) {
  clear(el);
  for (const kid of kids.flat(9)) {
    if (kid === null || kid === undefined || kid === false) continue;
    el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return el;
}

async function api(path, opts) {
  const res = await fetch(path, opts);
  const body = await res.json().catch(() => ({ error: `${res.status} ${res.statusText}` }));
  if (!res.ok && res.status !== 503) throw new Error(body.error || res.statusText);
  return { ok: res.ok, status: res.status, body };
}

// ---------------------------------------------------------------------------
// Vocabulary: how a status is coloured. Kept in one place so a status means
// the same thing on every screen.
// ---------------------------------------------------------------------------
const KIND_LABEL = {
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
  if (TERMINAL.has(s)) return '';
  return '';
}
const tag = (text, tone, title) =>
  h('span', { class: `tag ${tone || ''}`, title: title || '' }, text);

const statusTag = (status) => status ? tag(status, statusTone(status)) : null;

// ---------------------------------------------------------------------------
// Identifier linking. Every program identifier that names a record we have
// becomes a link; one that names nothing stays plain text, which is how a
// dangling reference makes itself visible while reading.
// ---------------------------------------------------------------------------
// Mirrors RECORD_ID_RE in ui/scan.py. The second segment is an area token
// for most kinds but a date for DEC/IDEA/TASK and a bare token for BATCH,
// so it cannot be required to start with a letter.
const ID_RE = /\b(?:GOAL|RQ|IDEA|EXP|RUN|EV|DEC|TASK|BATCH|CORR|KN|H)-[A-Za-z0-9]{1,20}(?:-[A-Za-z0-9]{1,32}){0,2}\b/g;
const known = new Set();

function idLink(id, extraClass) {
  const href = id.startsWith('GOAL-') ? `#/goal/${id}` : `#/record/${id}`;
  return h('a', { class: `id-link ${extraClass || ''}`, href }, id);
}

/** Turn free text into a fragment with known identifiers linked. */
function linkify(text) {
  const frag = document.createDocumentFragment();
  const src = String(text ?? '');
  let last = 0;
  for (const m of src.matchAll(ID_RE)) {
    if (!known.has(m[0])) continue;
    if (m.index > last) frag.append(src.slice(last, m.index));
    frag.append(idLink(m[0]));
    last = m.index + m[0].length;
  }
  if (last < src.length) frag.append(src.slice(last));
  return frag;
}

// ---------------------------------------------------------------------------
// App state
// ---------------------------------------------------------------------------
const state = {
  status: null, overview: null, goals: null, facets: null,
  experiments: null, integrity: null,
  filters: { q: '', kind: new Set(), area: new Set(), status: new Set() },
  ready: false,
};

const view = () => $('#view');
const setCrumb = (text) => { $('#crumb').textContent = text || ''; };

function loading(label) {
  return h('div', { class: 'empty row', style: 'justify-content:center' },
    h('span', { class: 'spin' }), ' ', label || 'loading…');
}

// ---------------------------------------------------------------------------
// Sidebar
// ---------------------------------------------------------------------------
const NAV = [
  { route: '#/', label: 'Portfolio' },
  { route: '#/goals', label: 'Goals', count: (s) => s.overview?.goals.total },
  { route: '#/records', label: 'Records', count: (s) => s.status?.records },
  { route: '#/experiments', label: 'Experiments', count: (s) => s.status?.experiments },
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

function renderBuildState() {
  const s = state.status;
  const el = $('#build-state');
  if (!s) { el.textContent = 'starting…'; return; }
  if (s.state === 'building') {
    fill(el, h('span', { class: 'spin' }), ` indexing… ${s.elapsed ?? 0}s`);
    return;
  }
  if (s.state === 'error') { fill(el, tag('index failed', 'bad')); return; }
  const deep = s.deep_scan === 'running'
    ? h('span', { class: 'faint', title: 'exact YAML parse of every ledger record' },
        ' · deep scan…')
    : null;
  fill(el, 
    h('span', { title: `built in ${s.build_seconds}s` },
      `${(s.records || 0).toLocaleString()} records`), deep);
}

// ---------------------------------------------------------------------------
// Views
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
      // The clamp goes on an inner element: `overflow:hidden` clips at the
      // PADDING box, so clamping the padded box itself lets the next line
      // show through the bottom padding as a sliver of ascenders.
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

async function viewOverview() {
  setCrumb('portfolio');
  const root = clear(view());
  if (!state.ready) { root.append(loading('building the index…')); return; }
  const o = state.overview;

  const counts = h('div', { class: 'stat-row' },
    ...o.counts.filter((c) => c.count).map((c) =>
      statCard(c.count.toLocaleString(), c.label,
        { href: `#/records?kind=${c.key}`, title: `browse ${c.label}` })));

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

  const ecc = h('section', { class: 'panel' },
    h('div', { class: 'panel-head' },
      h('h3', {}, 'ECC first'),
      h('a', { href: '#/goals', class: 'faint' }, 'all goals →')),
    h('div', { class: 'panel-body grid', style: 'grid-template-columns:repeat(auto-fill,minmax(300px,1fr))' },
      o.ecc_first.length
        ? o.ecc_first.map(goalCard)
        : h('div', { class: 'empty' }, 'no active ECC goals')));

  const attention = o.attention.length ? h('section', { class: 'panel' },
    h('div', { class: 'panel-head' }, h('h3', {}, 'Wants attention'),
      h('span', { class: 'faint' }, 'flagged, or carrying a recorded impediment')),
    h('div', { class: 'panel-body grid', style: 'grid-template-columns:repeat(auto-fill,minmax(300px,1fr))' },
      o.attention.map(goalCard))) : null;

  const hypPanel = h('section', { class: 'panel' },
    h('div', { class: 'panel-head' }, h('h3', {}, 'Hypotheses by status')),
    h('div', { class: 'panel-body' }, distribution(o.hypothesis_status, 'H')));

  const runPanel = h('section', { class: 'panel' },
    h('div', { class: 'panel-head' }, h('h3', {}, 'Runs by terminal status')),
    h('div', { class: 'panel-body' }, distribution(o.run_status, null)));

  const recent = h('section', { class: 'panel' },
    h('div', { class: 'panel-head' }, h('h3', {}, 'Latest records'),
      h('span', { class: 'faint' }, 'decisions, evidence, handoffs, corrections')),
    h('div', { class: 'scroll-x' }, recordTable(o.recent, { compact: true })));

  root.append(h('div', { class: 'stack' },
    goalStats, counts, ecc, attention,
    h('div', { class: 'grid', style: 'grid-template-columns:repeat(auto-fit,minmax(320px,1fr))' },
      hypPanel, runPanel),
    recent));
}

function distribution(map, kind) {
  const entries = Object.entries(map || {}).sort((a, b) => b[1] - a[1]);
  if (!entries.length) return h('div', { class: 'faint' }, 'nothing recorded');
  const total = entries.reduce((a, [, v]) => a + v, 0);
  return h('div', { class: 'stack', style: 'gap:7px' }, entries.map(([name, n]) => {
    const pct = (n / total) * 100;
    const tone = statusTone(name);
    const colour = tone ? `var(--${tone === 'ok' ? 'ok' : tone === 'bad' ? 'bad'
      : tone === 'warn' ? 'warn' : 'info'})` : 'var(--line-strong)';
    return h('div', { class: 'row', style: 'gap:10px' },
      h('div', { style: 'flex:0 0 175px;min-width:0' },
        kind ? h('a', { href: `#/records?kind=${kind}&status=${encodeURIComponent(name)}`,
                        class: 'mono' }, name)
             : h('span', { class: 'mono' }, name)),
      h('div', { class: 'bar', style: 'flex:1' },
        h('i', { style: `width:${pct}%;background:${colour}` })),
      h('span', { class: 'mono faint', style: 'flex:0 0 52px;text-align:right' }, n));
  }));
}

function recordTable(records, opts = {}) {
  if (!records.length) return h('div', { class: 'empty' }, 'nothing matches');
  return h('table', {},
    h('thead', {}, h('tr', {},
      h('th', {}, 'id'), h('th', {}, 'kind'), h('th', {}, 'status'),
      h('th', {}, 'title'), opts.compact ? null : h('th', {}, 'area'),
      h('th', {}, 'date'), opts.compact ? null : h('th', { title: 'records citing this one' }, 'in'))),
    h('tbody', {}, records.map((r) => h('tr', {},
      h('td', {}, idLink(r.id)),
      h('td', { class: 'faint mono', style: 'font-size:11px' }, KIND_LABEL[r.kind] || r.kind),
      h('td', {}, statusTag(r.status) || h('span', { class: 'faint' }, '—')),
      h('td', { style: 'max-width:640px' },
        h('div', { class: 'clamp2' }, r.title || h('span', { class: 'faint' }, '(no title)'))),
      opts.compact ? null : h('td', {},
        r.area ? h('a', { href: `#/records?area=${r.area}`, class: 'mono' },
          r.ecc ? h('span', { class: 'tag acc' }, r.area) : r.area) : h('span', { class: 'faint' }, '—')),
      h('td', { class: 'mono faint', style: 'white-space:nowrap' }, r.date || '—'),
      opts.compact ? null : h('td', { class: 'mono faint' }, r.backlinks || '')))));
}

async function viewGoals() {
  setCrumb('goals');
  const root = clear(view());
  if (!state.ready) { root.append(loading()); return; }
  if (!state.goals) state.goals = (await api('/api/goals')).body.goals;

  const filters = { text: '', only: 'active' };
  const grid = h('div', { class: 'grid', style: 'grid-template-columns:repeat(auto-fill,minmax(310px,1fr))' });
  const summary = h('div', { class: 'faint mono' });

  function draw() {
    const needle = filters.text.toLowerCase();
    const rows = state.goals.filter((g) => {
      if (filters.only === 'active' && g.status !== 'active') return false;
      if (filters.only === 'ecc' && !(g.ecc && g.status === 'active')) return false;
      if (filters.only === 'attention' && !(g.flags?.length || g.impediment_count)) return false;
      if (filters.only === 'retired' && !g.terminal) return false;
      if (!needle) return true;
      return `${g.id} ${g.title} ${g.area} ${g.next_action_preview}`.toLowerCase().includes(needle);
    });
    fill(grid, rows.length ? rows.map(goalCard)
      : h('div', { class: 'empty' }, 'no goals match'));
    summary.textContent = `${rows.length} of ${state.goals.length} goals`;
  }

  const chip = (key, label, title) => h('button', {
    class: 'chip', 'aria-pressed': filters.only === key, title: title || '',
    onclick: (e) => {
      filters.only = key;
      for (const c of e.target.parentElement.children) c.setAttribute('aria-pressed', c === e.target);
      draw();
    },
  }, label);

  root.append(h('div', { class: 'stack' },
    h('div', { class: 'spread' },
      h('div', { class: 'chip-row' },
        chip('active', 'active'),
        chip('ecc', 'ECC active', 'ECC goals are selected before all others'),
        chip('attention', 'wants attention'),
        chip('retired', 'retired'),
        chip('all', 'all')),
      h('div', { class: 'row' }, summary,
        h('input', {
          class: 'mono', style: 'padding:6px 9px;border:1px solid var(--line-strong);border-radius:6px;background:var(--bg-panel);color:inherit',
          placeholder: 'filter goals…', oninput: (e) => { filters.text = e.target.value; draw(); },
        }))),
    grid));
  draw();
}

async function viewGoal(id) {
  setCrumb(id);
  const root = clear(view());
  root.append(loading());
  const { ok, body: goal } = await api(`/api/goals/${encodeURIComponent(id)}`);
  if (!ok) { fill(root, h('div', { class: 'banner bad' }, `unknown goal ${id}`)); return; }
  clear(root);

  const head = h('section', { class: 'panel' },
    h('div', { class: 'panel-body stack', style: 'gap:10px' },
      h('div', { class: 'spread' },
        h('div', { class: 'row' },
          h('b', { class: 'id-link', style: 'font-size:14px' }, goal.id),
          goal.ecc ? tag('ECC', 'acc') : null, statusTag(goal.status),
          goal.owner ? tag(goal.owner) : null),
        h('a', { class: 'faint mono', href: `#/records?q=${encodeURIComponent(goal.id)}` },
          `${goal.mentions.length} mentions →`)),
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

  const nextAction = goal.next_action ? h('section', { class: 'panel' },
    h('div', { class: 'panel-head' }, h('h3', {}, 'Next action')),
    h('div', { class: 'panel-body' },
      h('div', { class: 'next-action', style: 'font-size:12px' }, linkify(goal.next_action)))) : null;

  const objective = goal.objective ? h('section', { class: 'panel' },
    h('div', { class: 'panel-head' }, h('h3', {}, 'Objective')),
    h('div', { class: 'panel-body', style: 'line-height:1.65' }, linkify(goal.objective))) : null;

  const criteria = goal.completion_criteria?.length ? h('section', { class: 'panel' },
    h('div', { class: 'panel-head' }, h('h3', {}, 'Completion criteria'),
      h('span', { class: 'faint' },
        'a committed Coordinator decision showing one was met closes the goal')),
    h('div', { class: 'panel-body' }, yamlTree(goal.completion_criteria))) : null;

  const impediments = goal.impediments?.length ? h('section', { class: 'panel' },
    h('div', { class: 'panel-head' }, h('h3', {}, 'Impediments'),
      h('span', { class: 'faint' }, 'recorded, not paused')),
    h('div', { class: 'panel-body' }, yamlTree(goal.impediments))) : null;

  const checkpoints = goal.checkpoints?.length ? h('section', { class: 'panel' },
    h('div', { class: 'panel-head' }, h('h3', {}, `Batch checkpoints (${goal.checkpoints.length})`),
      h('span', { class: 'faint' }, 'write-once')),
    h('div', { class: 'scroll-x' }, h('table', {},
      h('thead', {}, h('tr', {}, h('th', {}, 'batch'), h('th', {}, 'recorded'),
        h('th', {}, 'summary'))),
      h('tbody', {}, goal.checkpoints.map((c) => h('tr', {},
        h('td', { class: 'mono' }, c.batch_id || '—'),
        h('td', { class: 'mono faint' }, c.recorded_at || '—'),
        h('td', {}, h('div', { class: 'clamp3' }, linkify(c.summary || '—')))))))))
    : null;

  const linked = h('section', { class: 'panel' },
    h('div', { class: 'panel-head' }, h('h3', {}, 'Bound records')),
    h('div', { class: 'panel-body stack' },
      linkedBlock('research questions', goal.questions, goal.question_ids),
      linkedBlock('active hypotheses', goal.hypotheses, goal.active_hypothesis_ids)));

  root.append(h('div', { class: 'stack' },
    head, nextAction, objective, criteria, impediments, checkpoints, linked));
}

function linkedBlock(label, records, ids) {
  if (!ids?.length) {
    return h('div', {}, h('div', { class: 'k faint', style: 'text-transform:uppercase;font-size:10px;letter-spacing:.07em' }, label),
      h('div', { class: 'faint' }, 'none'));
  }
  const missing = ids.filter((id) => !records.some((r) => r.id === id));
  return h('div', { class: 'stack', style: 'gap:6px' },
    h('div', { class: 'faint', style: 'text-transform:uppercase;font-size:10px;letter-spacing:.07em' }, label),
    records.length ? h('div', { class: 'scroll-x' }, recordTable(records, { compact: true })) : null,
    missing.length ? h('div', { class: 'banner warn', style: 'font-size:11px' },
      `named but not found in the ledger: ${missing.join(', ')}`) : null);
}

function budgetLine(budget) {
  if (!budget) return '—';
  const unbounded = budget.maximum_batches === null && budget.total_wall_clock_seconds === null;
  const parts = [];
  parts.push(budget.maximum_batches === null ? 'batches ∞' : `batches ≤ ${budget.maximum_batches}`);
  parts.push(budget.total_wall_clock_seconds === null
    ? 'wall-clock ∞' : `wall-clock ≤ ${budget.total_wall_clock_seconds}s`);
  if (budget.max_concurrent !== null && budget.max_concurrent !== undefined) {
    parts.push(`max_concurrent ${budget.max_concurrent}`);
  }
  return h('span', { class: 'row' }, h('span', { class: 'mono' }, parts.join(' · ')),
    unbounded ? tag('unbounded', 'ok') : null);
}

const kv = (key, value) => h('div', { style: 'display:contents' },
  h('dt', {}, key), h('dd', {}, value));

// ---------------------------------------------------------------------------
// Records browser
// ---------------------------------------------------------------------------
async function viewRecords(params) {
  setCrumb('records');
  const root = clear(view());
  if (!state.ready) { root.append(loading()); return; }
  if (!state.facets) state.facets = (await api('/api/facets')).body;

  const f = state.filters;
  f.q = params.get('q') || '';
  f.kind = new Set((params.get('kind') || '').split(',').filter(Boolean));
  f.area = new Set((params.get('area') || '').split(',').filter(Boolean));
  f.status = new Set((params.get('status') || '').split(',').filter(Boolean));
  $('#q').value = f.q;
  let offset = 0;

  const results = h('div', { class: 'panel scroll-x' });
  const meta = h('div', { class: 'faint mono' });
  const more = h('div', {});

  function pushRoute() {
    const p = new URLSearchParams();
    if (f.q) p.set('q', f.q);
    for (const key of ['kind', 'area', 'status']) {
      if (f[key].size) p.set(key, [...f[key]].join(','));
    }
    const next = `#/records${p.toString() ? `?${p}` : ''}`;
    if (location.hash !== next) history.replaceState(null, '', next);
  }

  async function load(append) {
    const p = new URLSearchParams({ limit: '100', offset: String(offset) });
    if (f.q) p.set('q', f.q);
    for (const key of ['kind', 'area', 'status']) {
      if (f[key].size) p.set(key, [...f[key]].join(','));
    }
    const { body } = await api(`/api/records?${p}`);
    meta.textContent = `${body.total.toLocaleString()} matching · showing ${
      Math.min(offset + body.records.length, body.total).toLocaleString()}`;
    if (append) {
      const tbody = results.querySelector('tbody');
      if (tbody) for (const r of body.records) tbody.append(recordTable([r]).querySelector('tr'));
    } else {
      fill(results, recordTable(body.records));
    }
    clear(more);
    if (offset + body.records.length < body.total) {
      more.append(h('button', {
        class: 'btn', onclick: () => { offset += 100; load(true); },
      }, `load 100 more (${(body.total - offset - body.records.length).toLocaleString()} left)`));
    }
  }

  function toggle(group, key, el) {
    const set = f[group];
    if (set.has(key)) set.delete(key); else set.add(key);
    el.setAttribute('aria-pressed', set.has(key));
    offset = 0; pushRoute(); load(false);
  }

  const facetRow = (label, group, items, render) => h('div', { class: 'stack', style: 'gap:6px' },
    h('div', { class: 'faint', style: 'text-transform:uppercase;font-size:10px;letter-spacing:.07em' }, label),
    h('div', { class: 'chip-row' }, items.map((item) => {
      const el = h('button', { class: 'chip', 'aria-pressed': f[group].has(item.key) },
        render(item));
      el.addEventListener('click', () => toggle(group, item.key, el));
      return el;
    })));

  root.append(h('div', { class: 'stack' },
    h('section', { class: 'panel' }, h('div', { class: 'panel-body stack', style: 'gap:12px' },
      facetRow('kind', 'kind', state.facets.kinds,
        (i) => `${i.label} ${i.count.toLocaleString()}`),
      facetRow('area', 'area', state.facets.areas.slice(0, 60),
        (i) => h('span', {}, i.ecc ? h('span', { class: 'tag acc', style: 'margin-right:4px' }, 'ECC') : null,
          `${i.key} ${i.count}`)),
      facetRow('status', 'status', state.facets.statuses.slice(0, 40),
        (i) => `${i.key} ${i.count.toLocaleString()}`))),
    h('div', { class: 'spread' }, meta,
      h('button', { class: 'btn', onclick: () => {
        f.kind.clear(); f.area.clear(); f.status.clear(); f.q = '';
        $('#q').value = ''; location.hash = '#/records'; route();
      } }, 'clear filters')),
    results, more));

  pushRoute();
  await load(false);
}

// ---------------------------------------------------------------------------
// Record detail
// ---------------------------------------------------------------------------
async function viewRecord(id) {
  setCrumb(id);
  const root = clear(view());
  root.append(loading());
  const { ok, body } = await api(`/api/records/${encodeURIComponent(id)}`);
  if (!ok) {
    fill(root, h('div', { class: 'banner bad' },
      h('div', {}, h('b', {}, `${id} is not in the index. `),
        'It may be a run, a batch, a coordination task, or a dangling reference.')));
    return;
  }
  clear(root);
  const s = body.summary;

  const panes = { structured: null, raw: null, links: null };
  const paneHost = h('div', { class: 'panel-body' });
  const tabs = h('div', { class: 'tabs' });
  const tabDefs = [
    ['structured', 'record'],
    ['raw', 'source'],
    ['links', `links (${body.links.out.length}↗ ${body.links.in.length}↙)`],
  ];
  function show(key) {
    fill(paneHost, panes[key] ??= buildPane(key, body));
    for (const t of tabs.children) t.setAttribute('aria-selected', t.dataset.key === key);
  }
  for (const [key, label] of tabDefs) {
    const t = h('button', { class: 'tab', 'data-key': key, onclick: () => show(key) }, label);
    tabs.append(t);
  }

  const head = h('section', { class: 'panel' },
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
          ? tag('parsed', 'ok', 'This view is a real YAML parse of the record on disk')
          : tag('parse failed', 'bad', body.parse_error || '')),
      s.title ? h('h2', { style: 'font-size:16px;line-height:1.4' }, s.title) : null,
      h('div', { class: 'faint mono', style: 'font-size:11px' }, s.path)));

  if (!body.verified && body.parse_error) {
    root.append(h('div', { class: 'banner bad', style: 'margin-bottom:14px' },
      h('div', {}, h('b', {}, 'this record does not parse. '),
        body.parse_error,
        h('div', { class: 'faint', style: 'margin-top:4px' },
          'Reported, not repaired: records are immutable and a correction supersedes them.'))));
  }

  const side = h('aside', { class: 'stack' },
    h('section', { class: 'panel' },
      h('div', { class: 'panel-head' }, h('h3', {}, `Cited by (${body.links.in.length})`)),
      h('div', { class: 'panel-body stack', style: 'gap:5px;max-height:420px;overflow:auto' },
        body.links.in.length
          ? body.links.in.map((r) => h('div', { class: 'row', style: 'gap:6px' },
              idLink(r.id), statusTag(r.status)))
          : h('span', { class: 'faint' }, 'nothing cites this record'))),
    h('section', { class: 'panel' },
      h('div', { class: 'panel-head' }, h('h3', {}, `Cites (${body.links.out.length})`)),
      h('div', { class: 'panel-body stack', style: 'gap:5px;max-height:420px;overflow:auto' },
        body.links.out.length
          ? body.links.out.map((r) => h('div', { class: 'row', style: 'gap:6px' },
              idLink(r.id), statusTag(r.status)))
          : h('span', { class: 'faint' }, 'cites nothing in the index'))));

  root.append(h('div', { class: 'stack' }, head,
    h('div', { class: 'detail' },
      h('section', { class: 'panel' }, tabs, paneHost), side)));
  show('structured');
}

function buildPane(key, body) {
  if (key === 'raw') return h('pre', { class: 'raw' }, body.raw);
  if (key === 'links') {
    return h('div', { class: 'stack' },
      h('div', {}, h('h3', { style: 'font-size:12px;margin-bottom:8px' },
        `Cites — ${body.links.out.length}`),
        h('div', { class: 'scroll-x' }, recordTable(body.links.out))),
      h('div', {}, h('h3', { style: 'font-size:12px;margin-bottom:8px' },
        `Cited by — ${body.links.in.length}`),
        h('div', { class: 'scroll-x' }, recordTable(body.links.in))));
  }
  if (body.body === null || body.body === undefined) {
    return h('div', { class: 'empty' }, 'no parsed body — read the source tab');
  }
  return yamlTree(body.body);
}

/** Render a parsed record as a collapsible tree with identifiers linked. */
function yamlTree(value, depth = 0) {
  if (value === null || value === undefined) return h('span', { class: 'yaml-null' }, 'null');
  if (typeof value !== 'object') {
    const text = String(value);
    if (typeof value === 'boolean' || typeof value === 'number') {
      return h('span', { class: 'mono', style: 'color:var(--accent)' }, text);
    }
    return h('span', { class: 'yaml-scalar' }, linkify(text));
  }
  if (Array.isArray(value)) {
    if (!value.length) return h('span', { class: 'yaml-null' }, '[]');
    return h('div', { class: depth ? 'yaml-node' : '' },
      value.map((item, i) => h('div', { class: 'yaml-row row', style: 'align-items:flex-start;gap:8px' },
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
    const details = h('details', { open: depth < 1 },
      h('summary', { style: 'cursor:pointer;padding:3px 0' },
        h('span', { class: 'yaml-key' }, `${k}`),
        h('span', { class: 'faint mono', style: 'font-size:10.5px' }, ` ${count}`)),
      bodyEl);
    return h('div', { class: 'yaml-row' }, details);
  }));
}

// ---------------------------------------------------------------------------
// Experiments
// ---------------------------------------------------------------------------
async function viewExperiments() {
  setCrumb('experiments');
  const root = clear(view());
  if (!state.ready) { root.append(loading()); return; }
  if (!state.experiments) state.experiments = (await api('/api/experiments')).body.experiments;

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
      if (!needle) return true;
      return `${e.id} ${e.title} ${e.status}`.toLowerCase().includes(needle);
    });
    meta.textContent = `${rows.length} of ${state.experiments.length} experiments`;
    fill(host, rows.length ? h('table', {},
      h('thead', {}, h('tr', {}, h('th', {}, 'id'), h('th', {}, 'status'),
        h('th', {}, 'runs'), h('th', {}, 'title'), h('th', {}, 'hypothesis'), h('th', {}, 'frozen'))),
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

  root.append(h('div', { class: 'stack' },
    h('div', { class: 'spread' },
      h('div', { class: 'chip-row' }, chip('with-runs', 'with runs'), chip('no-runs', 'no runs'),
        chip('ecc', 'ECC'), chip('all', 'all')),
      h('div', { class: 'row' }, meta, h('input', {
        class: 'mono', placeholder: 'filter…',
        style: 'padding:6px 9px;border:1px solid var(--line-strong);border-radius:6px;background:var(--bg-panel);color:inherit',
        oninput: (e) => { text = e.target.value; draw(); },
      }))),
    host));
  draw();
}

function runPills(runs) {
  if (!runs.length) return h('span', { class: 'faint' }, '—');
  const counts = {};
  for (const r of runs) counts[r.status] = (counts[r.status] || 0) + 1;
  return h('span', { class: 'row', style: 'gap:4px' },
    Object.entries(counts).map(([status, n]) =>
      tag(`${n} ${status}`, statusTone(status), status)));
}

// ---------------------------------------------------------------------------
// Integrity
// ---------------------------------------------------------------------------
async function viewIntegrity() {
  setCrumb('integrity');
  const root = clear(view());
  if (!state.ready) { root.append(loading()); return; }
  const { body } = await api('/api/integrity');
  state.integrity = body;
  clear(root);

  const section = (title, note, content) => h('section', { class: 'panel' },
    h('div', { class: 'panel-head' }, h('h3', {}, title),
      note ? h('span', { class: 'faint' }, note) : null),
    content);

  const pending = body.unparseable_state !== 'complete';
  const unparseable = section(
    `Unparseable ledger records${pending ? '' : ` (${body.unparseable.length})`}`,
    'exact YAML parse of every record under ledger/',
    pending
      ? h('div', { class: 'panel-body' }, loading('deep scan running — not yet measured'))
      : (body.unparseable.length
        ? h('div', { class: 'scroll-x' }, h('table', {},
            h('thead', {}, h('tr', {}, h('th', {}, 'path'), h('th', {}, 'parser error'))),
            h('tbody', {}, body.unparseable.map((u) => h('tr', {},
              h('td', { class: 'mono' }, u.path),
              h('td', { class: 'mono faint' }, u.error))))))
        : h('div', { class: 'empty' }, 'every ledger record parses')));

  const dupes = section(`Duplicate identifiers (${body.duplicate_ids.length})`,
    'the same id in more than one file — identifiers are immutable and never reused',
    body.duplicate_ids.length
      ? h('div', { class: 'scroll-x' }, h('table', {},
          h('thead', {}, h('tr', {}, h('th', {}, 'id'), h('th', {}, 'paths'))),
          h('tbody', {}, body.duplicate_ids.map((d) => h('tr', {},
            h('td', {}, idLink(d.id)),
            h('td', { class: 'mono faint' }, d.paths.join('  ·  ')))))))
      : h('div', { class: 'empty' }, 'no duplicates'));

  const mismatch = section(`Filename does not match id (${body.id_path_mismatch.length})`,
    'cosmetic on its own; a signal when it is unexpected',
    body.id_path_mismatch.length
      ? h('div', { class: 'scroll-x' }, h('table', {},
          h('thead', {}, h('tr', {}, h('th', {}, 'path'), h('th', {}, 'declared id'))),
          h('tbody', {}, body.id_path_mismatch.slice(0, 300).map((m) => h('tr', {},
            h('td', { class: 'mono' }, m.path), h('td', {}, idLink(m.id)))))))
      : h('div', { class: 'empty' }, 'all filenames match'));

  const dangling = section(`Dangling references (${body.dangling_refs_total ?? body.dangling_refs.length})`,
    'a GOAL/RQ/H/EXP/EV/DEC/IDEA/KN identifier that is cited but has no record',
    body.dangling_refs.length
      ? h('div', { class: 'scroll-x' }, h('table', {},
          h('thead', {}, h('tr', {}, h('th', {}, 'identifier'), h('th', {}, 'times cited'))),
          h('tbody', {}, body.dangling_refs.map((d) => h('tr', {},
            h('td', { class: 'mono' }, d.id),
            h('td', { class: 'mono faint' }, d.cited_by))))))
      : h('div', { class: 'empty' }, 'every cited record exists'));

  const goalFlags = body.goal_flags.length ? section(
    `Goal policy flags (${body.goal_flags.length})`, 'checked against CLAUDE.md rules 10 and 11',
    h('div', { class: 'panel-body stack', style: 'gap:8px' },
      body.goal_flags.map((g) => h('div', { class: 'row' }, idLink(g.id),
        h('span', {}, g.flags.join(' · ')))))) : null;

  root.append(h('div', { class: 'stack' },
    h('div', { class: 'banner info' }, h('div', {},
      h('b', {}, 'Flagged, never fixed. '),
      'Records are immutable and a correction supersedes them — a repair is a Coordinator act, ',
      'and breakage already on main is owned by its campaign, not by whoever is reading this.')),
    body.ecc_policy_error ? h('div', { class: 'banner warn' },
      `ECC priority policy could not be loaded: ${body.ecc_policy_error}. ECC ordering is off.`) : null,
    unparseable, goalFlags, dupes, dangling, mismatch));
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
async function poll() {
  const { body } = await api('/api/status');
  const wasReady = state.ready;
  state.status = body;
  renderBuildState();

  if (body.state === 'ready' && !wasReady) {
    state.ready = true;
    const [overview, goals, facets] = await Promise.all([
      api('/api/overview'), api('/api/goals'), api('/api/facets'),
    ]);
    state.overview = overview.body;
    state.goals = goals.body.goals;
    state.facets = facets.body;
    // Identifier linking needs to know what exists, so the id set is pulled
    // once, before the first render: a link that resolves to nothing is
    // worse than plain text, and re-rendering later would make links
    // appear under the reader's cursor.
    const ids = await api('/api/ids');
    for (const id of ids.body.ids) known.add(id);
    renderNav();
    await route();
  }
  if (body.state === 'building' || body.deep_scan === 'running') {
    setTimeout(poll, 1200);
  }
}

function initChrome() {
  const stored = localStorage.getItem('autoresearch-theme');
  if (stored) document.documentElement.setAttribute('data-theme', stored);
  $('#theme').addEventListener('click', () => {
    const now = document.documentElement.getAttribute('data-theme');
    const isDark = now ? now === 'dark'
      : matchMedia('(prefers-color-scheme: dark)').matches;
    const next = isDark ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('autoresearch-theme', next); } catch { /* private mode */ }
  });

  $('#refresh').addEventListener('click', async () => {
    state.ready = false;
    state.overview = state.goals = state.facets = state.experiments = state.integrity = null;
    known.clear();
    await api('/api/refresh', { method: 'POST' });
    poll();
  });

  let timer = null;
  $('#q').addEventListener('input', (e) => {
    clearTimeout(timer);
    const value = e.target.value;
    timer = setTimeout(() => {
      const p = new URLSearchParams(parseHash().params);
      if (value) p.set('q', value); else p.delete('q');
      location.hash = `#/records${p.toString() ? `?${p}` : ''}`;
      if (parseHash().path === '/records') route();
    }, 220);
  });

  addEventListener('keydown', (e) => {
    if (e.key === '/' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
      e.preventDefault(); $('#q').focus(); $('#q').select();
    }
    if (e.key === 'Escape' && document.activeElement === $('#q')) $('#q').blur();
  });

  addEventListener('hashchange', route);
}

initChrome();
renderNav();
route();
poll();
