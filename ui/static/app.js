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
 * The page is organised around the question a reader arrives with. "What
 * has this program established?" is the findings board; "what is it doing?"
 * is the goals board; "show me everything" is the records browser. The
 * overview puts those three in order and says how much of what went into the
 * program's loop came out the other end.
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
// A `KN-` identifier carries its family where every other kind carries an
// area, so a knowledge row is labelled by family rather than "knowledge".
const KN_FAMILY = { FIND: 'finding', OPEN: 'open problem', TECH: 'technique', LIT: 'literature' };
const TERMINAL = new Set(['completed', 'closed_at_budget', 'cancelled']);

const kindLabel = (r) => r.kind === 'KN' ? (KN_FAMILY[r.area] || 'knowledge') : (KIND_LABEL[r.kind] || r.kind);

function statusTone(status) {
  const s = (status || '').toLowerCase();
  if (!s) return '';
  if (s === 'paused' || s === 'blocked') return 'bad';         // forbidden for goals
  if (['active', 'running', 'approved', 'supported', 'completed_valid', 'replicated',
       'validated', 'strong', 'established', 'proved', 'certificate', 'current'].includes(s)) return 'ok';
  if (['completed', 'analyzed', 'specified', 'frozen', 'moderate', 'derivation',
       'supported_scoped', 'closed_at_budget'].includes(s)) return 'info';
  if (['draft', 'proposed', 'speculative', 'pending', 'inconclusive', 'unstated', 'preliminary',
       'weak', 'anecdotal', 'single_run', 'weakened', 'superseded', 'empirical_only',
       'provisional', 'reported'].includes(s)) return 'warn';
  if (['rejected', 'rejected_scoped', 'refuted', 'failed', 'unparseable', 'cancelled',
       'error', 'no-manifest', 'unreadable', 'withdrawn', 'contradictory'].includes(s)) return 'bad';
  return '';
}

// Evidence direction. The schema names four values; the records use forty
// spellings. `direction_polarity` in ui/payloads.py folds them for the board;
// this mirrors it for records the board did not pre-classify. The author's
// exact word is always what is displayed -- only the colour is derived.
const POLARITY_TONE = { supports: 'ok', weakens: 'bad', mixed: 'warn', neutral: '' };
const NEUTRAL = new Set(['', 'neutral', 'inconclusive', 'n/a', 'none', 'not_applicable', 'null']);
function directionPolarity(direction) {
  const d = (direction || '').trim().toLowerCase();
  if (NEUTRAL.has(d)) return 'neutral';
  if (/^(weaken|contradict|refute|negative|against|adverse)/.test(d)) return 'weakens';
  if (/^(support|confirm|corroborat|positive|strengthen|enabling)/.test(d)) return 'supports';
  return 'mixed';
}
function decisionTone(decision) {
  const d = (decision || '').toLowerCase();
  if (!d) return '';
  if (/^(weaken|reject|infrastructure)/.test(d)) return 'bad';
  if (/^(pause|supersede|revise|refine|inconclusive|defer)/.test(d)) return 'warn';
  if (/^(approve|support|confirm|expand|replicate|promote|accept|complete|advance|curate)/.test(d)) return 'ok';
  if (/^(open|close)/.test(d)) return 'info';
  return '';
}
// docs/claims-and-verification.md "Refutation artifacts": the strongest
// checkable basis a record has for what it says.
const PROOF_TONE = { certificate: 'ok', derivation: 'info', empirical_only: 'warn', not_applicable: '' };
const PROOF_NOTE = {
  certificate: 'an explicit instance re-checked by code independent of the solver',
  derivation: 'a written, step-checkable argument — not a machine-verified proof',
  empirical_only: 'replicated observations; no instance or argument isolates the mechanism',
  not_applicable: 'nothing here to prove or refute',
};

const tag = (text, tone, title) =>
  h('span', { class: `tag ${tone || ''}`, title: title || '' }, text);
const statusTag = (status) => status ? tag(status, statusTone(status)) : null;
const proofTag = (p) => p ? tag(p, PROOF_TONE[p] ?? '', PROOF_NOTE[p] || 'proof status') : null;
const directionTag = (d) => d ? tag(d, POLARITY_TONE[directionPolarity(d)], 'direction, as recorded') : null;
const decisionTag = (d) => d ? tag(d, decisionTone(d), 'the Coordinator’s recorded decision') : null;

// ---------------------------------------------------------------------------
// Identifier linking. Mirrors RECORD_ID_RE in ui/scan.py: the second segment
// is an area token for most kinds but a date for DEC/IDEA/TASK/CORR and a
// bare token for BATCH, so it cannot be required to start with a letter.
// ---------------------------------------------------------------------------
const ID_RE = /\b(?:GOAL|RQ|IDEA|EXP|RUN|EV|DEC|TASK|BATCH|CORR|KN|H)-[A-Za-z0-9]{1,20}(?:-[A-Za-z0-9]{1,32}){0,2}\b/g;
const ID_ONLY_RE = /^(?:GOAL|RQ|IDEA|EXP|RUN|EV|DEC|TASK|BATCH|CORR|KN|H)-[A-Za-z0-9]{1,20}(?:-[A-Za-z0-9]{1,32}){0,2}$/;

function idLink(id, extra) {
  const href = id.startsWith('GOAL-') && !id.includes('~')
    ? `#/goal/${id}` : `#/record/${id}`;
  // Cards navigate on click; a link inside one must win over the card.
  return h('a', { class: `id-link ${extra || ''}`, href, onclick: (e) => e.stopPropagation() }, id);
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
  overview: null, goals: null, experiments: null, experimentsPayload: null, findings: null,
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

/** A repository-relative path, linked to its source at the built commit
 *  when a repository URL is known and left as text otherwise. */
function pathLink(path, label) {
  const src = sourceUrl(path);
  return src
    ? h('a', { class: 'mono', href: src, target: '_blank', rel: 'noreferrer' }, label || path)
    : h('span', { class: 'mono' }, label || path);
}

// ---------------------------------------------------------------------------
// Time. Two kinds of it, and the difference is load-bearing.
//
//   DECLARED  a date the record asserts about itself (`approved_at`,
//             `recorded_at`). Shown under the field name that carried it.
//   OBSERVED  a commit time from git history, via ui/gitdates.py. Shown as
//             "committed". Most of this corpus declares no date at all, so
//             this is usually the only time there is.
//
// They are never merged. A page that showed a commit time under "approved"
// would be asserting something no record says.
// ---------------------------------------------------------------------------
const fmtDate = (d) => (d || '').slice(0, 10) || '—';

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/** Epoch seconds or an ISO string to a Date, or null. */
function asDate(value) {
  if (value === null || value === undefined || value === '') return null;
  if (typeof value === 'number') return Number.isFinite(value) ? new Date(value * 1000) : null;
  const text = String(value).trim();
  // A bare `YYYY-MM-DD` is parsed as UTC midnight by design: the corpus
  // writes dates without a zone and reading them in local time shifts half
  // the world's readers to the previous day.
  const iso = /^\d{4}-\d{2}-\d{2}$/.test(text) ? `${text}T00:00:00Z` : text;
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? null : d;
}

/** `2026-09-04 04:45 UTC`, or `2026-09-04` when there is no time of day. */
function exactUTC(value, { dateOnly = false } = {}) {
  const d = asDate(value);
  if (!d) return '';
  const day = `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}-${
    String(d.getUTCDate()).padStart(2, '0')}`;
  if (dateOnly) return day;
  return `${day} ${String(d.getUTCHours()).padStart(2, '0')}:${
    String(d.getUTCMinutes()).padStart(2, '0')} UTC`;
}

/** "3 days ago", "in 2 hours", "just now". */
function relative(value) {
  const d = asDate(value);
  if (!d) return '';
  const seconds = (Date.now() - d.getTime()) / 1000;
  const ago = seconds >= 0;
  const n = Math.abs(seconds);
  const say = (v, unit) => {
    const rounded = Math.round(v);
    const text = `${rounded} ${unit}${rounded === 1 ? '' : 's'}`;
    return ago ? `${text} ago` : `in ${text}`;
  };
  if (n < 45) return 'just now';
  if (n < 3600) return say(n / 60, 'minute');
  if (n < 86400) return say(n / 3600, 'hour');
  if (n < 86400 * 30) return say(n / 86400, 'day');
  if (n < 86400 * 365) return say(n / 2629800, 'month');
  return say(n / 31557600, 'year');
}

/** A timestamp as a `<time>`: short text, exact instant on hover.
 *
 *  `label` names WHAT the time is ("approved", "committed") and goes in the
 *  tooltip, so a reader hovering a bare date learns which fact it is. An
 *  absent value renders the em dash every other empty cell uses, never a
 *  guess and never today's date. */
function timeEl(value, { label = '', dateOnly = false, style = 'short', className = '' } = {}) {
  const d = asDate(value);
  if (!d) return h('span', { class: `faint ${className}` }, '—');
  const exact = exactUTC(value, { dateOnly });
  const rel = relative(value);
  const short = dateOnly || style === 'date'
    ? `${d.getUTCDate()} ${MONTHS[d.getUTCMonth()]} ${String(d.getUTCFullYear()).slice(2)}`
    : rel;
  return h('time', {
    class: `when mono ${className}`,
    datetime: d.toISOString(),
    title: [label, exact, dateOnly ? '' : rel && `(${rel})`].filter(Boolean).join(' · '),
  }, style === 'both' ? `${exact}` : short);
}

/** A duration in seconds as `2h 14m`, `11m 8s`, `4.2s`. */
function fmtDuration(seconds) {
  if (seconds === null || seconds === undefined || !Number.isFinite(seconds)) return '';
  if (seconds < 1) return `${(Math.round(seconds * 1000) / 1000)}s`;
  if (seconds < 60) return `${Math.round(seconds * 10) / 10}s`;
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  if (m < 60) return s ? `${m}m ${s}s` : `${m}m`;
  const hours = Math.floor(m / 60);
  const mins = m % 60;
  if (hours < 24) return mins ? `${hours}h ${mins}m` : `${hours}h`;
  return `${Math.floor(hours / 24)}d ${hours % 24}h`;
}
function clip(text, n) {
  const s = String(text ?? '');
  return s.length <= n ? s : `${s.slice(0, n).replace(/\s+\S*$/, '')}…`;
}
const sum = (map) => Object.values(map || {}).reduce((a, b) => a + (b || 0), 0);
const split = (v) => (v || '').split(',').filter(Boolean);

// ---------------------------------------------------------------------------
// Chrome
// ---------------------------------------------------------------------------
const NAV = [
  { route: '#/', label: 'Overview' },
  { route: '#/findings', label: 'Findings', count: (s) => s.meta?.findings },
  { route: '#/goals', label: 'Goals', count: (s) => s.meta?.goals },
  { route: '#/experiments', label: 'Experiments', count: (s) => s.meta?.experiments },
  { route: '#/records', label: 'Records', count: (s) => s.records.length || null },
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
  if (!m) { el.append('reading the index…'); return; }
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

/** A titled panel; null when there is nothing to put in it, so a caller can
 *  list panels and let the empty ones vanish. */
function panel(title, note, body, opts = {}) {
  if (!body) return null;
  return h('section', { class: 'panel', id: opts.id || null },
    h('div', { class: 'panel-head' }, h('h3', {}, title),
      note ? (note.nodeType ? note : h('span', { class: 'faint' }, note)) : null),
    body);
}
const kicker = (text) => h('div', { class: 'kicker' }, text);

const thead = (cols) => h('thead', {}, h('tr', {}, cols.map((c) =>
  typeof c === 'string' ? h('th', {}, c) : h('th', { title: c.title || '' }, c.label))));
const td = (...kids) => h('td', {}, ...kids);

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
      goal.updated_at ? `· updated ${fmtDate(goal.updated_at)}` : null,
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

/** One promoted finding. The border colour is its proof status, because that
 *  is the first thing a reader should weigh: what kind of basis this rests on. */
function findingCard(fd) {
  const tone = PROOF_TONE[fd.proof_status] ?? '';
  const retiredNote = fd.superseded_by ? `superseded by ${fd.superseded_by}`
    : fd.withdrawn_by ? `withdrawn by ${fd.withdrawn_by}` : '';
  return h('div', {
    class: `finding-card ${tone ? `tone-${tone}` : ''} ${fd.status !== 'current' ? 'retired' : ''}`,
    onclick: () => { location.hash = `#/record/${fd.id}`; },
  },
    h('div', { class: 'spread' },
      h('span', { class: 'id-link' }, fd.id),
      h('div', { class: 'row', style: 'gap:4px' },
        fd.ecc ? tag('ECC', 'acc') : null,
        fd.status !== 'current' ? tag(fd.status, 'bad', retiredNote) : null,
        proofTag(fd.proof_status),
        fd.claim_tier ? tag(fd.claim_tier, 'info', 'claim tier of the evidence it rests on') : null)),
    h('h4', { class: 'clamp3' }, fd.title || h('span', { class: 'faint' }, '(no title)')),
    fd.excerpt
      ? h('div', { class: 'excerpt' }, h('div', { class: 'clamp4' }, linkify(fd.excerpt)))
      : h('div', { class: 'excerpt faint' }, fd.error ? `no front matter — ${fd.error}` : 'no statement excerpt'),
    // The other half of a finding: what its author says it does NOT
    // establish. Shown in their words, because a claim without its boundary
    // is the overclaim the program's rules exist to prevent.
    fd.non_claim
      ? h('div', { class: 'non-claim' }, h('span', { class: 'kicker' }, 'not claimed'),
          h('div', { class: 'clamp2' }, linkify(fd.non_claim)))
      : null,
    h('div', { class: 'row faint mono', style: 'font-size:11px' },
      fd.added ? h('span', {}, `added ${fmtDate(fd.added)}`) : null,
      fd.confidence ? h('span', { title: `confidence, as the entry states it: ${fd.confidence}` },
        `· ${clip(fd.confidence, 36)}`) : null,
      fd.goal_ids.length ? h('span', { class: 'row', style: 'gap:4px;display:inline-flex' },
        '·', fd.goal_ids.slice(0, 2).map((g) => idLink(g))) : null,
      fd.cited_by ? h('span', {}, `· cited by ${fd.cited_by}`) : null));
}

function areaCell(r) {
  if (r.kind === 'KN' || !r.area) return h('span', { class: 'faint' }, '—');
  return h('a', { href: `#/records?area=${r.area}`, class: 'mono' },
    r.ecc ? h('span', { class: 'tag acc' }, r.area) : r.area);
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
      h('td', { class: 'faint mono', style: 'font-size:11px' }, kindLabel(r)),
      h('td', {}, (r.kind === 'DEC' ? decisionTag(r.status) : statusTag(r.status))
        || h('span', { class: 'faint' }, '—')),
      h('td', { style: 'max-width:640px' },
        h('div', { class: 'clamp2' }, r.title || h('span', { class: 'faint' }, '(no title)'))),
      opts.compact ? null : h('td', {}, areaCell(r)),
      h('td', { class: 'mono faint', style: 'white-space:nowrap' }, fmtDate(r.date)),
      opts.compact ? null : h('td', { class: 'mono faint' }, r.backlinks || '')))));
}

const resolve = (ids) => ids.map((id) => state.byId.get(id)).filter(Boolean);

/** Horizontal bars for a {name: count} map. `opts.href(name)` makes a row a
 *  link; `opts.tone(name)` colours it; a kind string is the legacy shorthand
 *  for "link to the records browser filtered to that kind and status". */
function distribution(map, opts = {}) {
  if (typeof opts === 'string') {
    const kind = opts;
    opts = { href: (name) => `#/records?kind=${kind}&status=${encodeURIComponent(name)}` };
  }
  // Largest first, except a folded "other (…)" tail, which stays a tail.
  const isTail = ([name]) => name.startsWith('other (');
  const entries = Object.entries(map || {})
    .sort((a, b) => (isTail(a) - isTail(b)) || b[1] - a[1]);
  if (!entries.length) return h('div', { class: 'faint' }, 'nothing recorded');
  const total = entries.reduce((a, [, v]) => a + v, 0);
  return h('div', { class: 'stack', style: 'gap:7px' }, entries.map(([name, n]) => {
    const tone = opts.tone ? opts.tone(name) : statusTone(name);
    const colour = tone ? `var(--${tone})` : 'var(--line-strong)';
    const href = opts.href ? opts.href(name) : null;
    return h('div', { class: 'row', style: 'gap:10px' },
      h('div', { style: 'flex:0 0 175px;min-width:0', class: 'clamp2' },
        href ? h('a', { href, class: 'mono' }, name) : h('span', { class: 'mono' }, name)),
      h('div', { class: 'bar', style: 'flex:1' },
        h('i', { style: `width:${(n / total) * 100}%;background:${colour}` })),
      h('span', { class: 'mono faint', style: 'flex:0 0 52px;text-align:right' }, n));
  }));
}

/** A labelled row of toggle chips. `pressed(key)` says which are on. */
function facetRow(label, items, pressed, onToggle, render) {
  if (!items.length) return null;
  return h('div', { class: 'stack', style: 'gap:6px' },
    kicker(label),
    h('div', { class: 'chip-row' }, items.map((item) => {
      const el = h('button', { class: 'chip', 'aria-pressed': pressed(item.key), title: item.title || '' },
        render ? render(item) : `${item.label ?? item.key} ${(item.count ?? '').toLocaleString()}`);
      el.addEventListener('click', () => onToggle(item.key, el));
      return el;
    })));
}

/** Single-choice chips: one is pressed at a time. */
function choiceChips(options, current, onPick) {
  const row = h('div', { class: 'chip-row' });
  for (const [key, label, title] of options) {
    const el = h('button', { class: 'chip', 'aria-pressed': current === key, title: title || '' }, label);
    el.addEventListener('click', () => {
      for (const c of row.children) c.setAttribute('aria-pressed', c === el);
      onPick(key);
    });
    row.append(el);
  }
  return row;
}

const kv = (key, value) => h('div', { style: 'display:contents' },
  h('dt', {}, key), h('dd', {}, value));

// ---------------------------------------------------------------------------
// Markdown. Knowledge entries are markdown and the entry IS the content, so
// the page renders it. Small on purpose: headings, paragraphs, lists, quotes,
// fenced code, tables, emphasis, links. Everything is built as DOM nodes from
// text -- nothing is ever assigned to innerHTML -- and identifiers in prose
// link to their records like everywhere else.
// ---------------------------------------------------------------------------
const MD_HEADING = /^(#{1,6})\s+(.*?)\s*#*\s*$/;
const MD_LIST = /^(\s*)([-*+]|\d+[.)])\s+(.*)$/;
const MD_INLINE = /(`[^`\n]+`)|(\*\*[^*\n]+\*\*)|(__[^_\n]+__)|(\*[^*\s][^*\n]*?\*)|(\[[^\]\n]+\]\([^)\s]+\))|(<?https?:\/\/[^\s<>)\]]+>?)/g;

function renderMarkdown(src, depth = 0) {
  const root = h('div', { class: depth ? 'md nested' : 'md' });
  const lines = String(src || '').replace(/\r\n?/g, '\n').split('\n');
  const para = [];
  const flush = () => {
    if (para.length) root.append(h('p', {}, mdInline(para.join(' '))));
    para.length = 0;
  };
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (/^\s*```/.test(line)) {                                   // fenced code
      flush();
      const code = [];
      i += 1;
      while (i < lines.length && !/^\s*```/.test(lines[i])) code.push(lines[i++]);
      i += 1;
      root.append(h('pre', {}, h('code', {}, code.join('\n'))));
      continue;
    }
    const heading = MD_HEADING.exec(line);
    if (heading) {                                                 // demoted one level: the
      flush();                                                     // page already has the h2
      root.append(h(`h${Math.min(heading[1].length + 1, 6)}`, {}, mdInline(heading[2])));
      i += 1;
      continue;
    }
    if (/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(line)) { flush(); root.append(h('hr')); i += 1; continue; }
    if (/^\s*>/.test(line)) {                                      // blockquote
      flush();
      const quote = [];
      while (i < lines.length && /^\s*>/.test(lines[i])) quote.push(lines[i++].replace(/^\s*>\s?/, ''));
      root.append(h('blockquote', {}, renderMarkdown(quote.join('\n'), depth + 1)));
      continue;
    }
    if (/^\s*\|.*\|\s*$/.test(line) && i + 1 < lines.length && /^\s*\|?\s*:?-{2,}/.test(lines[i + 1])) {
      flush();
      const rows = [];
      while (i < lines.length && /^\s*\|/.test(lines[i])) rows.push(lines[i++]);
      root.append(h('div', { class: 'scroll-x' }, mdTable(rows)));
      continue;
    }
    const list = MD_LIST.exec(line);
    if (list && depth < 6) {
      flush();
      const ordered = /\d/.test(list[2]);
      const base = list[1].length;
      const items = [];
      while (i < lines.length) {
        const m = MD_LIST.exec(lines[i]);
        if (m && m[1].length <= base) { items.push({ text: m[3], sub: [] }); i += 1; continue; }
        const cur = items[items.length - 1];
        if (m && m[1].length > base) { cur.sub.push(lines[i].slice(base + 2)); i += 1; continue; }
        if (/^\s+\S/.test(lines[i])) {                             // continuation or nested block
          if (cur.sub.length) cur.sub.push(lines[i].slice(base + 2)); else cur.text += ` ${lines[i].trim()}`;
          i += 1; continue;
        }
        break;
      }
      root.append(h(ordered ? 'ol' : 'ul', {}, items.map((it) =>
        h('li', {}, mdInline(it.text), it.sub.length ? renderMarkdown(it.sub.join('\n'), depth + 1) : null))));
      continue;
    }
    if (!line.trim()) { flush(); i += 1; continue; }
    if (/^\s*<!--.*-->\s*$/.test(line)) { i += 1; continue; }     // one-line html comment
    para.push(line.trim());
    i += 1;
  }
  flush();
  return root;
}

function mdInline(text) {
  const frag = document.createDocumentFragment();
  let last = 0;
  for (const m of String(text).matchAll(MD_INLINE)) {
    if (m.index > last) frag.append(linkify(text.slice(last, m.index)));
    const tok = m[0];
    if (m[1]) frag.append(h('code', {}, tok.slice(1, -1)));
    else if (m[2] || m[3]) frag.append(h('strong', {}, mdInline(tok.slice(2, -2))));
    else if (m[4]) frag.append(h('em', {}, mdInline(tok.slice(1, -1))));
    else if (m[5]) {
      const link = /^\[([^\]]+)\]\(([^)\s]+)\)$/.exec(tok);
      frag.append(mdLink(link[1], link[2]));
    } else if (m[6]) {
      const url = tok.replace(/^<|>$/g, '');
      frag.append(mdLink(url, url));
    }
    last = m.index + tok.length;
  }
  if (last < text.length) frag.append(linkify(text.slice(last)));
  return frag;
}

function mdLink(label, href) {
  if (/^https?:\/\//i.test(href)) {
    return h('a', { href, target: '_blank', rel: 'noreferrer' }, mdInline(label));
  }
  if (/^#/.test(href)) return h('span', {}, mdInline(label));      // in-document anchors: no page for them
  // A repository-relative path: the file at the built commit, if we know the repo.
  const src = sourceUrl(href.replace(/^\.?\//, ''));
  return src
    ? h('a', { href: src, target: '_blank', rel: 'noreferrer' }, mdInline(label))
    : h('span', {}, mdInline(label));
}

function mdTable(rows) {
  const cells = (row) => row.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
  const [head, , ...body] = rows;
  return h('table', {},
    h('thead', {}, h('tr', {}, cells(head).map((c) => h('th', {}, mdInline(c))))),
    h('tbody', {}, body.map((r) => h('tr', {}, cells(r).map((c) => h('td', {}, mdInline(c)))))));
}

// ---------------------------------------------------------------------------
// At a glance: the fields of a record that say what it IS, rendered above
// the full tree. Per kind, in the order a reader wants them. A field that
// is absent is skipped, so a record built on an older schema shows what it
// has and nothing invented.
// ---------------------------------------------------------------------------
const GLANCE = {
  EV: [
    ['direction', 'direction', 'direction'], ['strength', 'strength', 'status'],
    ['claim_tier', 'claim tier', 'tag'], ['proof_status', 'proof status', 'proof'],
    ['type', 'type', 'tag'],
    ['hypothesis_id', 'hypothesis', 'ids'], ['goal_id', 'goal', 'ids'],
    ['experiment_ids', 'experiments', 'ids'], ['run_ids', 'runs', 'ids'],
    ['headline_non_result', 'headline', 'text'], ['scope_statement', 'scope', 'text'],
    ['conclusion', 'conclusion', 'text'], ['inference', 'inference', 'text'],
    ['summary', 'summary', 'text'], ['obstruction.statement', 'obstruction', 'text'],
    ['obstruction.value', 'measured', 'text'],
    ['boundaries', 'boundaries', 'list'], ['unresolved_confounds', 'unresolved confounds', 'list'],
    ['observations', 'observations', 'observations'],
    ['knowledge_promotion', 'knowledge promotion', 'promotion'],
  ],
  DEC: [
    ['decision', 'decision', 'decision'], ['decision_label', 'label', 'text'],
    ['target_ids', 'targets', 'ids'], ['goal_id', 'goal', 'ids'],
    ['evidence_refs', 'evidence', 'ids'], ['evidence_ids', 'evidence', 'ids'],
    ['context', 'context', 'text'], ['what_is_approved', 'approved', 'text'],
    ['what_is_NOT_approved', 'not approved', 'text'],
    ['hypothesis_status_transition', 'hypothesis status', 'kv'],
    ['rationale', 'rationale', 'list'], ['limitations', 'limitations', 'list'],
    ['next_actions', 'next actions', 'list'], ['non_claims', 'non-claims', 'list'],
    ['knowledge_promotion', 'knowledge promotion', 'promotion'], ['decided_at', 'decided', 'text'],
  ],
  H: [
    ['status', 'status', 'status'], ['statement', 'statement', 'text'],
    ['mechanism', 'mechanism', 'text'], ['question_id', 'question', 'ids'],
    ['goal_id', 'goal', 'ids'], ['derived_from_idea', 'from proposal', 'ids'],
    ['source_idea_id', 'from proposal', 'ids'], ['asymptotic_claim', 'asymptotic claim', 'kv'],
    ['predictions', 'predictions', 'kvlist'], ['falsification_conditions', 'falsification', 'list'],
    ['assumptions', 'assumptions', 'list'], ['interpretation_limits', 'limits', 'list'],
  ],
  EXP: [
    ['status', 'status', 'status'], ['frozen', 'frozen', 'tag'],
    ['execution_authorized', 'execution authorized', 'tag'],
    ['hypothesis_id', 'hypothesis', 'ids'], ['question_id', 'question', 'ids'],
    ['objective', 'objective', 'text'], ['success_criterion', 'success criterion', 'text'],
    ['falsification_criterion', 'falsification criterion', 'text'],
    ['scale_relevance', 'scale', 'kv'], ['budget', 'budget', 'kv'], ['controls', 'controls', 'list'],
  ],
  RQ: [
    ['status', 'status', 'status'], ['motivation', 'motivation', 'text'],
    ['decision_target', 'decision target', 'text'], ['constraints', 'constraints', 'list'],
    ['scope', 'scope', 'kv'],
  ],
  IDEA: [
    ['status', 'status', 'status'], ['novelty_status', 'novelty', 'tag'],
    ['question_id', 'question', 'ids'], ['claim', 'claim', 'text'],
    ['mechanism', 'mechanism', 'text'], ['minimal_test', 'minimal test', 'text'],
    ['predictions', 'predictions', 'kvlist'], ['falsification', 'falsification', 'list'],
    ['dominated_by', 'dominated by', 'text'], ['sota_delta', 'SOTA delta', 'kv'],
  ],
  TASK: [
    ['from', 'from', 'tag'], ['to', 'to', 'tag'], ['status', 'status', 'status'],
    ['objective', 'objective', 'text'], ['uncertainty_reduced', 'uncertainty reduced', 'text'],
    ['deliverables', 'deliverables', 'list'], ['inference.policy', 'policy', 'tag'],
  ],
  CORR: [
    ['record_id', 'record', 'ids'], ['field', 'field', 'text'], ['reason', 'reason', 'text'],
    ['prior_value', 'prior value', 'text'], ['corrected_value', 'corrected value', 'text'],
  ],
  BATCH: [
    ['batch_id', 'batch', 'text'], ['recorded_at', 'recorded', 'text'],
    ['summary', 'summary', 'text'], ['outcome', 'outcome', 'text'],
  ],
};

const getPath = (obj, path) => path.split('.').reduce((o, k) => (o && typeof o === 'object' ? o[k] : undefined), obj);
const isEmpty = (v) => v === null || v === undefined || v === '' || v === 'null'
  || (Array.isArray(v) && !v.length) || (typeof v === 'object' && !Array.isArray(v) && !Object.keys(v).length);
const scalar = (v) => v !== null && typeof v !== 'object';

function idOrText(v) {
  const s = String(v);
  return ID_ONLY_RE.test(s) && state.byId.has(s) ? idLink(s) : h('span', { class: 'mono' }, s);
}

/** The scalar fields of a small mapping, as "key: value" lines. */
function kvLines(obj, limit = 8) {
  const rows = Object.entries(obj || {}).filter(([, v]) => scalar(v) && !isEmpty(v)).slice(0, limit);
  if (!rows.length) return null;
  return h('div', { class: 'stack', style: 'gap:2px' }, rows.map(([k, v]) =>
    h('div', { class: 'row', style: 'gap:6px;align-items:baseline' },
      h('span', { class: 'yaml-key' }, `${k}:`), h('span', {}, linkify(String(v))))));
}

function moreNote(n) { return n > 0 ? h('div', { class: 'faint', style: 'font-size:11px' }, `+${n} more in the full record`) : null; }

function glanceValue(as, v) {
  switch (as) {
    case 'tag': return scalar(v) ? tag(String(v)) : null;
    case 'status': return scalar(v) ? statusTag(String(v)) : null;
    case 'direction': return scalar(v) ? directionTag(String(v)) : null;
    case 'decision': return scalar(v) ? decisionTag(String(v)) : null;
    case 'proof': return scalar(v) ? proofTag(String(v)) : null;
    case 'text': return scalar(v) ? h('div', { class: 'glance-text' }, linkify(clip(v, 1400))) : null;
    case 'ids': {
      const items = (Array.isArray(v) ? v : [v]).filter((x) => scalar(x) && !isEmpty(x));
      if (!items.length) return null;
      return h('div', { class: 'row', style: 'gap:6px' }, items.slice(0, 12).map(idOrText), moreNote(items.length - 12));
    }
    case 'list': {
      if (!Array.isArray(v)) return scalar(v) ? h('div', { class: 'glance-text' }, linkify(clip(v, 800))) : null;
      const shown = v.slice(0, 4);
      return h('div', {}, h('ul', { class: 'glance-list' }, shown.map((item) =>
        h('li', {}, scalar(item) ? linkify(clip(item, 500)) : (kvLines(item, 6) || h('span', { class: 'faint' }, 'structured'))))),
        moreNote(v.length - 4));
    }
    case 'kv': return typeof v === 'object' && !Array.isArray(v) ? kvLines(v) : null;
    case 'kvlist': {
      if (!Array.isArray(v)) return null;
      return h('div', { class: 'stack', style: 'gap:6px' }, v.slice(0, 4).map((item) =>
        scalar(item) ? h('div', {}, linkify(clip(item, 400))) : kvLines(item, 6)), moreNote(v.length - 4));
    }
    case 'observations': {
      if (!Array.isArray(v)) return null;
      const text = (o) => scalar(o) ? String(o) : (o?.text ?? o?.observation ?? o?.statement ?? Object.values(o || {}).find(scalar) ?? '');
      return h('div', {}, h('div', { class: 'faint', style: 'font-size:11px;margin-bottom:4px' }, `${v.length} recorded`),
        h('ul', { class: 'glance-list' }, v.slice(0, 2).map((o) => h('li', {}, linkify(clip(text(o), 420))))),
        moreNote(v.length - 2));
    }
    case 'promotion': {
      if (scalar(v)) return h('div', { class: 'glance-text' }, linkify(String(v)));
      const promoted = (Array.isArray(v?.promoted) ? v.promoted : []).filter(scalar);
      const why = v?.not_warranted;
      if (!promoted.length && isEmpty(why)) return kvLines(v);
      return h('div', { class: 'stack', style: 'gap:4px' },
        promoted.length ? h('div', { class: 'row', style: 'gap:6px' }, 'promoted:', promoted.map(idOrText)) : null,
        !isEmpty(why) && scalar(why) ? h('div', { class: 'glance-text' }, 'not warranted: ', linkify(clip(why, 600))) : null);
    }
    default: return null;
  }
}

/** The at-a-glance block for a parsed record body, or null. */
function glanceBlock(kind, body) {
  const spec = GLANCE[kind];
  if (!spec || !body || typeof body !== 'object' || Array.isArray(body)) return null;
  const rows = [];
  for (const [key, label, as] of spec) {
    const v = getPath(body, key);
    if (isEmpty(v)) continue;
    const rendered = glanceValue(as, v);
    if (rendered) rows.push(kv(label, rendered));
  }
  if (!rows.length) return null;
  return h('dl', { class: 'kv glance' }, rows);
}

// ---------------------------------------------------------------------------
// Overview: the program in one page, in the order a reader asks about it.
// ---------------------------------------------------------------------------
const STAGE_HREF = {
  RQ: '#/records?kind=RQ', IDEA: '#/records?kind=IDEA', H: '#/records?kind=H',
  EXP: '#/experiments', RUN: '#/experiments', EV: '#/records?kind=EV',
  DEC: '#/records?kind=DEC', FIND: '#/findings',
};
const STAGE_NOTE_HREF = {
  H: '#/findings?tab=verdicts', EXP: '#/experiments', EV: '#/findings?tab=evidence',
  FIND: '#/findings?status=all',
};

/** The program's own loop as a row of counts, left to right. */
function pipelineStrip(stages) {
  return h('div', { class: 'pipeline' }, (stages || []).map((s) => h('div', {
    class: 'stage', role: 'link', tabindex: '0', title: `open ${s.label}`,
    onclick: () => { location.hash = STAGE_HREF[s.key] || '#/records'; },
    onkeydown: (e) => { if (e.key === 'Enter') location.hash = STAGE_HREF[s.key] || '#/records'; },
  },
    h('div', { class: 'v' }, (s.count || 0).toLocaleString()),
    h('div', { class: 'k' }, s.label),
    s.note ? h('a', { class: 'note', href: STAGE_NOTE_HREF[s.key] || STAGE_HREF[s.key],
      onclick: (e) => e.stopPropagation() }, s.note) : null)));
}

async function viewOverview() {
  setCrumb('overview');
  const root = fill(view(), loading('building the index…'));
  if (!state.ready) return;
  state.overview ??= await getJSON('overview.json');
  const o = state.overview;
  const m = state.meta;
  const count = (key) => (o.counts.find((c) => c.key === key) || {}).count || 0;
  const evidenceTotal = sum(o.evidence_polarity);
  const directional = evidenceTotal - (o.evidence_polarity?.neutral || 0);

  const intro = h('section', { class: 'panel' },
    h('div', { class: 'panel-body stack', style: 'gap:12px' },
      h('div', {},
        kicker('state of the program'),
        h('h2', { style: 'font-size:18px;line-height:1.35;margin-top:3px' },
          'What the program has established, what it is working on, and what is still open')),
      h('p', { class: 'lede' },
        'An autonomous, reproducible cryptanalysis research program centred on the elliptic-curve ',
        'discrete logarithm problem, with ECC campaigns selected first. This page is read straight off ',
        'the committed ledger, experiment records and knowledge corpus; it writes nothing and holds no ',
        'authority — only a Coordinator decision changes research state, and every claim below links to ',
        'the record that makes it. Start with ', h('a', { href: '#/findings' }, 'findings'),
        ' for results, ', h('a', { href: '#/goals' }, 'goals'), ' for the campaigns, or ',
        h('a', { href: '#/records' }, 'records'), ' to browse everything.'),
      h('div', {}, kicker('the loop, as counts — read left to right'), pipelineStrip(o.pipeline))));

  const f = o.findings || { total: 0, current: 0, latest: [], by_proof_status: {} };
  const proofNote = Object.entries(f.by_proof_status || {}).map(([k, n]) => `${k} ${n}`).join(' · ');
  const established = panel('Established so far',
    h('span', { class: 'faint' },
      `${f.current} current finding${f.current === 1 ? '' : 's'}`,
      f.added_last_30_days !== undefined
        ? ` · ${f.added_last_7_days} added in the last 7 days, ${f.added_last_30_days} in 30` : '',
      proofNote ? ` · ${proofNote}` : '', ' · ', h('a', { href: '#/findings' }, 'all findings →')),
    f.latest.length
      ? h('div', { class: 'panel-body grid',
          style: 'grid-template-columns:repeat(auto-fill,minmax(330px,1fr))' },
          f.latest.map(findingCard))
      : h('div', { class: 'empty' }, 'no finding has been promoted yet'));

  const dirs = o.directions || { total: 0, top: [] };
  const byArea = panel('By research area',
    h('span', { class: 'faint' },
      `the ${dirs.top.length} areas with most established, of ${dirs.total} with records · `,
      h('a', { href: '#/findings?tab=areas' }, 'all areas →')),
    dirs.top.length ? h('div', { class: 'scroll-x' }, directionsTable(dirs.top, { compact: true })) : null);

  const verdicts = panel('Hypothesis verdicts',
    `${sum(o.hypothesis_verdicts)} of ${count('H').toLocaleString()} hypotheses reached one`,
    h('div', { class: 'panel-body' }, distribution(o.hypothesis_verdicts,
      { href: (v) => `#/findings?tab=verdicts&verdict=${v}` })));
  const polarity = panel('Evidence, by what it points at',
    `${directional} of ${evidenceTotal} evidence records take a direction`,
    h('div', { class: 'panel-body' }, distribution(o.evidence_polarity,
      { href: (p) => `#/findings?tab=evidence&polarity=${p}`, tone: (p) => POLARITY_TONE[p] || '' })));
  const decisions = panel('Decisions, by verdict', 'the Coordinator’s recorded rulings',
    h('div', { class: 'panel-body' }, distribution(o.decision_verdicts, {
      href: (d) => d.startsWith('other') || d === '(unstated)'
        ? '#/records?kind=DEC' : `#/records?kind=DEC&status=${encodeURIComponent(d)}`,
      tone: decisionTone })));

  const cardGrid = (goals) => h('div', { class: 'panel-body grid',
    style: 'grid-template-columns:repeat(auto-fill,minmax(300px,1fr))' }, goals.map(goalCard));
  const eccIds = new Set(o.ecc_first.map((g) => g.id));
  const attention = o.attention.filter((g) => !eccIds.has(g.id));

  const recentDecisions = resolve(o.recent_decisions || []);
  const openLatest = o.open_problems?.latest || [];
  const it = o.integrity_totals;

  fill(root, h('div', { class: 'stack' },
    snapshotBanner(),
    intro,
    established,
    byArea,
    h('div', { class: 'grid', style: 'grid-template-columns:repeat(auto-fit,minmax(300px,1fr))' },
      verdicts, polarity, decisions),
    panel('Where the work is: ECC first',
      h('span', { class: 'faint' }, `${o.goals.ecc_active} active ECC goals of ${o.goals.active} active · `,
        h('a', { href: '#/goals' }, 'all goals →')),
      o.ecc_first.length ? cardGrid(o.ecc_first.slice(0, 9))
        : h('div', { class: 'empty' }, 'no active ECC goals')),
    attention.length ? panel('Wants attention', 'flagged, or carrying a recorded impediment — and not shown above',
      h('div', { class: 'scroll-x' }, h('table', {},
        thead(['goal', 'status', 'title', 'why']),
        h('tbody', {}, attention.map((g) => h('tr', {},
          td(idLink(g.id)), td(statusTag(g.status)),
          h('td', { style: 'max-width:560px' }, h('div', { class: 'clamp2' }, g.title)),
          td(h('div', { class: 'row' },
            g.flags?.length ? tag(g.flags.join(' · '), 'bad') : null,
            g.impediment_count ? tag(`${g.impediment_count} impediment${g.impediment_count === 1 ? '' : 's'}`, 'warn') : null)))))))) : null,
    h('div', { class: 'grid', style: 'grid-template-columns:minmax(0,2fr) minmax(280px,1fr)' },
      panel('Recent decisions', h('a', { href: '#/records?kind=DEC', class: 'faint' }, 'all decisions →'),
        h('div', { class: 'scroll-x' }, h('table', {},
          thead(['id', 'verdict', 'context', 'date']),
          h('tbody', {}, recentDecisions.map((d) => h('tr', {},
            td(idLink(d.id)), td(decisionTag(d.status) || h('span', { class: 'faint' }, '—')),
            h('td', { style: 'max-width:720px' },
              h('div', { class: 'clamp2' }, d.title || h('span', { class: 'faint' }, '(no context)'))),
            h('td', { class: 'mono faint', style: 'white-space:nowrap' }, fmtDate(d.date)))))))),
      panel('Still open', h('a', { href: '#/findings?tab=open', class: 'faint' },
        `${o.open_problems?.open ?? 0} open problems →`),
        openLatest.length ? h('div', { class: 'panel-body stack', style: 'gap:10px' },
          openLatest.map((p) => h('div', {},
            h('a', { href: `#/record/${p.id}`, style: 'font-weight:600;line-height:1.4' }, p.title),
            h('div', { class: 'faint mono', style: 'font-size:11px' }, `${p.id} · ${fmtDate(p.added)}`))))
          : h('div', { class: 'empty' }, 'no open problems recorded'))),
    h('div', { class: 'row faint', style: 'font-size:12px;justify-content:flex-end' },
      'integrity: ',
      h('span', { class: it.unparseable ? 'tag bad' : 'tag ok' },
        it.unparseable_state === 'complete' ? `${it.unparseable} unparseable` : 'deep scan running'),
      tag(`${it.dangling_refs} dangling refs`, it.dangling_refs ? 'warn' : 'ok'),
      tag(`${it.duplicate_ids} duplicate ids`, it.duplicate_ids ? 'warn' : 'ok'),
      tag(`${it.goal_flags} goal flags`, it.goal_flags ? 'bad' : 'ok'),
      h('a', { href: '#/integrity' }, 'details →'))));
}

// ---------------------------------------------------------------------------
// Findings: what the program has established, and what still stands against it.
// ---------------------------------------------------------------------------
// An area the program has invested in or produced from: a goal, a finding,
// a hypothesis verdict or an open problem. The long tail of areas that only
// ever reached a proposal is still there, behind a chip.
const investedArea = (r) => r.goals.length > 0 || r.findings_total > 0
  || Object.keys(r.verdicts || {}).length > 0 || r.open_problems > 0;

const FINDINGS_TABS = [
  ['findings', 'Findings', (d) => d.counts.current],
  ['areas', 'By area', (d) => d.directions.filter(investedArea).length],
  ['verdicts', 'Hypothesis verdicts', (d) => d.hypothesis_verdicts.length],
  ['evidence', 'Evidence', (d) => d.evidence.filter((e) => !e.neutral).length],
  ['obstructions', 'Obstructions', (d) => d.obstructions.length],
  ['open', 'Open problems', (d) => d.open_problems.filter((p) => p.status === 'open').length],
];

const VERDICT_ORDER = ['supported', 'supported_scoped', 'weakened', 'rejected_scoped', 'rejected',
  'refuted', 'contradicted', 'inconclusive', 'superseded'];
const VERDICT_NOTE = {
  supported: 'the evidence supports the hypothesis as stated, within the scope it was tested on',
  supported_scoped: 'supported on the instances tested and claimed nowhere else',
  weakened: 'evidence went against it; not rejected',
  rejected_scoped: 'rejected on the tested instances — the scope is part of the verdict',
  rejected: 'rejected as stated',
  refuted: 'refuted',
  contradicted: 'contradicted by evidence',
  inconclusive: 'tested, and the result pointed neither way',
  superseded: 'replaced by a later hypothesis',
};

/** Replace the hash's query without adding a history entry. */
function replaceRoute(path, params) {
  const p = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    const val = v instanceof Set ? [...v].join(',') : v;
    if (val !== '' && val !== null && val !== undefined && val !== false) p.set(k, val);
  }
  const next = `${path}${p.toString() ? `?${p}` : ''}`;
  if (location.hash !== next) history.replaceState(null, '', next);
}

async function viewFindings(params) {
  setCrumb('findings');
  const root = fill(view(), loading());
  if (!state.ready) return;
  [state.findings, state.overview] = await Promise.all([
    state.findings || getJSON('findings.json'),
    state.overview || getJSON('overview.json'),
  ]);
  const d = state.findings;
  const tab = FINDINGS_TABS.some(([k]) => k === params.get('tab')) ? params.get('tab') : 'findings';

  const tabs = h('div', { class: 'chip-row' }, FINDINGS_TABS.map(([key, label, count]) =>
    h('a', { class: 'chip tab-chip', 'aria-pressed': key === tab, href: `#/findings?tab=${key}` },
      label, ' ', h('span', { class: 'n' }, count(d).toLocaleString()))));

  const docs = sourceUrl('docs/claims-and-verification.md');
  const intro = h('div', { class: 'banner info' }, h('div', {},
    h('div', {},
      h('b', {}, 'What counts as a finding here. '),
      'A result is promoted from an evidence record into ', h('code', {}, 'knowledge/findings/'),
      ' by a Coordinator decision, and carries the proof status and claim tier of the evidence it rests on — never more',
      docs ? [' (', h('a', { href: docs, target: '_blank', rel: 'noreferrer' }, 'claims and verification'), ')'] : null,
      '. Most evidence is neutral and most hypotheses never reach a verdict; the counts say so rather than hide it.'),
    h('div', { style: 'margin-top:6px;font-size:11.5px' },
      'Proof status: ', proofTag('certificate'), ' an explicit instance re-checked by independent code · ',
      proofTag('derivation'), ' a written, step-checkable argument · ',
      proofTag('empirical_only'), ' replicated observations only. ',
      'Each card also says what the entry does ', h('b', {}, 'not'), ' claim, in its own words.')));

  const body = ({
    findings: findingsTab, areas: directionsTab, verdicts: verdictsTab, evidence: evidenceTab,
    obstructions: obstructionsTab, open: openProblemsTab,
  })[tab](d, params);

  fill(root, h('div', { class: 'stack' }, snapshotBanner(), tabs, intro, body));
}

function findingsTab(d, params) {
  const f = {
    status: params.get('status') || 'current',
    proof: new Set(split(params.get('proof'))),
    tier: new Set(split(params.get('tier'))),
    area: new Set(split(params.get('area'))),
    q: params.get('q') || '',
    group: params.get('group') === 'date' ? 'date' : 'area',
  };
  const host = h('div', { class: 'stack', style: 'gap:20px' });
  const summary = h('div', { class: 'faint mono' });
  const byArea = new Map(d.directions.map((r) => [r.area, r]));
  const cardGrid = (items) => h('div', { class: 'grid',
    style: 'grid-template-columns:repeat(auto-fill,minmax(340px,1fr))' }, items.map(findingCard));

  /** Findings under the area they are filed in, with the goals of that
   *  area beside the heading — so a reader sees which campaign produced
   *  what, rather than eighty cards in date order. */
  function sections(items) {
    const groups = new Map();
    for (const x of items) {
      const key = x.area || '';
      (groups.get(key) ?? groups.set(key, []).get(key)).push(x);
    }
    const order = [...d.directions.map((r) => r.area).filter((a) => groups.has(a)),
      ...(groups.has('') ? [''] : [])];
    return order.map((area) => {
      const dir = byArea.get(area);
      const rows = groups.get(area);
      const goals = dir?.goals || [];
      return h('section', { class: 'area-group' },
        h('div', { class: 'area-head' },
          h('div', { class: 'row', style: 'gap:10px;align-items:baseline' },
            area
              ? (dir?.ecc ? tag(area, 'acc', 'ECC area — selected first') : h('span', { class: 'mono area-name' }, area))
              : h('span', { class: 'faint area-name' }, 'no area named'),
            h('span', { class: 'faint mono', style: 'font-size:11px' },
              `${rows.length} finding${rows.length === 1 ? '' : 's'}`),
            goals.slice(0, 2).map((g) => h('a', { href: `#/goal/${g.id}`, class: 'ellipsis',
              title: `${g.id} · ${g.status}` }, g.title || g.id)),
            goals.length > 2 ? h('span', { class: 'faint', style: 'font-size:11.5px' }, `+${goals.length - 2} goals`) : null),
          h('div', { class: 'row faint mono', style: 'font-size:11px' },
            dir?.active_goals ? h('span', {}, `${dir.active_goals} active goal${dir.active_goals === 1 ? '' : 's'}`) : null,
            dir?.open_problems ? h('a', { href: `#/findings?tab=open&area=${area}` },
              `· ${dir.open_problems} open problem${dir.open_problems === 1 ? '' : 's'}`) : null,
            area ? h('a', { href: `#/findings?tab=areas` }, '· all areas') : null)),
        cardGrid(rows));
    });
  }

  const areaCounts = {};
  for (const x of d.findings) for (const a of x.areas) areaCounts[a] = (areaCounts[a] || 0) + 1;
  const areas = Object.entries(areaCounts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, 24).map(([key, count]) => ({ key, count }));
  const eccCount = d.findings.filter((x) => x.ecc).length;

  function rows() {
    const needle = f.q.trim().toLowerCase();
    return d.findings.filter((x) =>
      (f.status === 'all' || x.status === f.status)
      && (!f.proof.size || f.proof.has(x.proof_status || '(unstated)'))
      && (!f.tier.size || f.tier.has(x.claim_tier || '(unstated)'))
      && (!f.area.size || x.areas.some((a) => f.area.has(a)) || (f.area.has('ECC') && x.ecc))
      && (!needle || `${x.id} ${x.title} ${x.excerpt} ${x.tags.join(' ')} ${x.goal_ids.join(' ')} ${x.confidence}`
          .toLowerCase().includes(needle)));
  }
  function draw() {
    const r = rows();
    fill(host, !r.length ? h('div', { class: 'empty' }, 'no findings match')
      : f.group === 'area' ? sections(r) : cardGrid(r));
    summary.textContent = `${r.length} of ${d.findings.length} findings`;
    replaceRoute('#/findings', { tab: 'findings', status: f.status === 'current' ? '' : f.status,
      proof: f.proof, tier: f.tier, area: f.area, q: f.q, group: f.group === 'area' ? '' : f.group });
  }
  const toggle = (group) => (key, el) => {
    f[group].has(key) ? f[group].delete(key) : f[group].add(key);
    el.setAttribute('aria-pressed', f[group].has(key));
    draw();
  };
  const counts = d.counts;
  const tiers = Object.entries(counts.by_claim_tier).filter(([k]) => k !== '(unstated)');

  const facets = h('section', { class: 'panel' }, h('div', { class: 'panel-body stack', style: 'gap:10px' },
    h('div', { class: 'stack', style: 'gap:6px' }, kicker('status'),
      choiceChips([
        ['current', `current ${counts.current}`],
        ['superseded', `superseded ${counts.by_status.superseded || 0}`, 'a later finding replaced it'],
        ['withdrawn', `withdrawn ${counts.by_status.withdrawn || 0}`],
        ['all', `all ${counts.findings}`],
      ], f.status, (key) => { f.status = key; draw(); })),
    facetRow('proof status', Object.entries(counts.by_proof_status).map(([key, count]) =>
      ({ key, count, title: PROOF_NOTE[key] || '' })), (k) => f.proof.has(k), toggle('proof'),
      (i) => h('span', {}, proofTag(i.key === '(unstated)' ? null : i.key) || i.key, ` ${i.count}`)),
    tiers.length ? facetRow('claim tier', tiers.map(([key, count]) => ({ key, count })),
      (k) => f.tier.has(k), toggle('tier')) : null,
    facetRow('area named', [{ key: 'ECC', count: eccCount, title: 'any ECC area' }, ...areas],
      (k) => f.area.has(k), toggle('area'),
      (i) => h('span', {}, i.key === 'ECC' || state.meta.ecc_areas.includes(i.key)
        ? h('span', { class: 'tag acc', style: 'margin-right:4px' }, 'ECC') : null, `${i.key} ${i.count}`))));

  const search = h('input', { class: 'mono field', placeholder: 'filter findings…', value: f.q,
    oninput: (e) => { f.q = e.target.value; draw(); } });
  const grouping = choiceChips([['area', 'by area'], ['date', 'latest first']], f.group,
    (key) => { f.group = key; draw(); });
  draw();
  return h('div', { class: 'stack' }, facets,
    h('div', { class: 'spread' }, h('div', { class: 'row' }, grouping, summary), search), host);
}

// ---------------------------------------------------------------------------
// By area: the program as a map, one row per research area.
// ---------------------------------------------------------------------------
const VERDICT_PILL_ORDER = ['supported', 'supported_scoped', 'weakened', 'rejected_scoped', 'rejected',
  'refuted', 'contradicted', 'inconclusive', 'superseded'];

function verdictPills(map) {
  const items = VERDICT_PILL_ORDER.filter((k) => map?.[k]).map((k) => tag(`${map[k]} ${k}`, statusTone(k)));
  return items.length ? h('div', { class: 'row', style: 'gap:4px' }, items) : h('span', { class: 'faint' }, '—');
}

/** A stacked bar of evidence polarity, with its total beside it. */
function polarityBar(counts) {
  const total = sum(counts);
  if (!total) return h('span', { class: 'faint' }, '—');
  const keys = ['supports', 'weakens', 'mixed', 'neutral'];
  return h('div', { class: 'row', style: 'gap:8px', title: keys.map((k) => `${k} ${counts[k] || 0}`).join(' · ') },
    h('div', { class: 'stack-bar' }, keys.map((k) => counts[k]
      ? h('i', { style: `width:${(counts[k] / total) * 100}%;background:${
          POLARITY_TONE[k] ? `var(--${POLARITY_TONE[k]})` : 'var(--line-strong)'}` })
      : null)),
    h('span', { class: 'mono faint', style: 'font-size:11px' }, total));
}

function directionsTable(rows, { compact = false } = {}) {
  const goalsShown = compact ? 1 : 3;
  return h('table', { class: 'dense' },
    thead(['area', 'goals', 'findings', 'hypothesis verdicts',
      { label: 'evidence', title: 'supports · weakens · mixed · neutral' }, 'open', 'latest finding']),
    h('tbody', {}, rows.map((r) => h('tr', {},
      td(r.ecc ? tag(r.area, 'acc', 'ECC area — selected first') : h('span', { class: 'mono area-name' }, r.area)),
      h('td', { style: 'max-width:380px;min-width:220px' }, r.goals.length
        ? h('div', { class: 'stack', style: 'gap:3px' },
            r.goals.slice(0, goalsShown).map((g) => h('div', { class: 'row', style: 'gap:6px;align-items:baseline;flex-wrap:nowrap' },
              idLink(g.id), h('span', { style: 'flex:none' }, statusTag(g.status)),
              h('span', { class: 'ellipsis faint', style: 'font-size:11.5px;max-width:240px' }, g.title))),
            r.goals.length > goalsShown ? h('span', { class: 'faint', style: 'font-size:11px' },
              `+${r.goals.length - goalsShown} more`) : null)
        : h('span', { class: 'faint' }, `no goal · ${r.hypotheses} hypotheses, ${r.experiments} experiments`)),
      td(r.findings ? h('a', { href: `#/findings?tab=findings&area=${r.area}`, class: 'mono' }, r.findings)
        : h('span', { class: 'faint mono' }, '0')),
      td(verdictPills(r.verdicts)),
      td(polarityBar(r.evidence)),
      td(r.open_problems ? h('a', { href: `#/findings?tab=open&area=${r.area}`, class: 'mono' }, r.open_problems)
        : h('span', { class: 'faint mono' }, '0')),
      h('td', { style: 'max-width:440px;min-width:220px' }, r.latest_finding
        ? h('div', {},
            // No `display:block` here: the clamp class IS the display, and an
            // inline display override was why long titles never clamped.
            h('a', { href: `#/record/${r.latest_finding.id}`, class: 'clamp2', style: 'line-height:1.4' },
              r.latest_finding.title),
            h('div', { class: 'faint mono', style: 'font-size:10.5px' }, fmtDate(r.latest_finding.added)))
        : h('span', { class: 'faint' }, 'nothing established yet'))))));
}

function directionsTab(d, params) {
  let only = ['findings', 'all'].includes(params.get('only')) ? params.get('only') : 'invested';
  const host = h('div', { class: 'panel scroll-x' });
  const summary = h('div', { class: 'faint mono' });
  const pick = (r) => only === 'all' ? true : only === 'findings' ? r.findings_total > 0 : investedArea(r);
  function draw() {
    const rows = d.directions.filter(pick);
    fill(host, rows.length ? directionsTable(rows) : h('div', { class: 'empty' }, 'no areas match'));
    summary.textContent = `${rows.length} of ${d.directions.length} areas`;
    replaceRoute('#/findings', { tab: 'areas', only: only === 'invested' ? '' : only });
  }
  const chips = choiceChips([
    ['invested', 'with a goal, finding, verdict or open problem'],
    ['findings', 'with findings'],
    ['all', 'every area with records'],
  ], only, (key) => { only = key; draw(); });
  draw();
  return h('div', { class: 'stack' },
    h('div', { class: 'banner info' }, h('div', {},
      h('b', {}, 'One row per research area. '),
      'The area is the token in the middle of a record identifier (GOAL-PFDR-…), the closest thing the corpus has to a research direction. ',
      'A finding or open problem is filed under its goal’s area, or the first record it cites, so nothing counts twice. ECC areas come first (CLAUDE.md rule 11).')),
    h('div', { class: 'spread' }, chips, summary),
    host);
}

function verdictsTab(d, params) {
  const only = params.get('verdict');
  const groups = new Map();
  for (const v of d.hypothesis_verdicts) (groups.get(v.verdict) ?? groups.set(v.verdict, []).get(v.verdict)).push(v);
  const order = [...VERDICT_ORDER, ...[...groups.keys()].filter((k) => !VERDICT_ORDER.includes(k))];
  const shown = order.filter((v) => groups.has(v) && (!only || only === v));

  const context = panel('All hypotheses, by status',
    'a verdict is a status past the design stages: proposed, analyzed, specified, approved',
    h('div', { class: 'panel-body' }, distribution(state.overview.hypothesis_status, 'H')));

  const table = (rows) => h('div', { class: 'scroll-x' }, h('table', {},
    thead(['hypothesis', 'status', 'statement', 'area', { label: 'evidence', title: 'evidence records citing it' }, 'findings', 'date']),
    h('tbody', {}, rows.map((v) => h('tr', {},
      td(idLink(v.id)), td(statusTag(v.status)),
      h('td', { style: 'max-width:640px;min-width:280px' },
        h('div', { class: 'clamp3' }, v.statement ? linkify(v.statement) : h('span', { class: 'faint' }, '(no statement)'))),
      td(v.area ? (v.ecc ? tag(v.area, 'acc') : h('span', { class: 'mono' }, v.area)) : h('span', { class: 'faint' }, '—')),
      td(v.evidence_ids.length ? h('a', { href: `#/record/${v.id}`, class: 'mono' }, v.evidence_ids.length) : h('span', { class: 'faint' }, '0')),
      td(v.finding_ids.length ? h('div', { class: 'row', style: 'gap:4px' }, v.finding_ids.slice(0, 3).map((id) => idLink(id))) : h('span', { class: 'faint' }, '—')),
      h('td', { class: 'mono faint', style: 'white-space:nowrap' }, fmtDate(v.date)))))));

  return h('div', { class: 'stack' },
    only ? h('div', { class: 'row' }, h('a', { class: 'chip', href: '#/findings?tab=verdicts' }, '← every verdict')) : null,
    shown.map((v) => panel(`${v} (${groups.get(v).length})`, VERDICT_NOTE[v] || null, table(groups.get(v)))),
    shown.length ? null : h('div', { class: 'empty' }, 'no hypothesis carries that verdict'),
    context);
}

function evidenceTab(d, params) {
  const f = {
    polarity: new Set(split(params.get('polarity'))),
    strength: new Set(split(params.get('strength'))),
    tier: new Set(split(params.get('tier'))),
    proof: new Set(split(params.get('proof'))),
    q: params.get('q') || '',
  };
  if (!f.polarity.size) f.polarity = new Set(['supports', 'weakens', 'mixed']);
  let shown = 100;
  const host = h('div', { class: 'panel scroll-x' });
  const summary = h('div', { class: 'faint mono' });
  const more = h('div', {});

  function rows() {
    const needle = f.q.trim().toLowerCase();
    return d.evidence.filter((e) =>
      f.polarity.has(e.polarity)
      && (!f.strength.size || f.strength.has(e.strength || '(unstated)'))
      && (!f.tier.size || f.tier.has(e.claim_tier || '(unstated)'))
      && (!f.proof.size || f.proof.has(e.proof_status || '(unstated)'))
      && (!needle || `${e.id} ${e.title} ${e.direction} ${e.hypothesis_id} ${e.goal_id}`.toLowerCase().includes(needle)));
  }
  function draw() {
    const r = rows();
    summary.textContent = `${r.length} of ${d.evidence.length} evidence records · showing ${Math.min(shown, r.length)}`;
    // Eight columns, three of them holding tokens that cannot wrap
    // (`laboratory_implementation_conformance`): every long value is a
    // capped tag and the cells are tight, or the table outgrows the page.
    fill(host, r.length ? h('table', { class: 'dense' },
      thead(['evidence', 'direction', 'strength', 'tier', 'proof', 'hypothesis', 'what it says', 'date']),
      h('tbody', {}, r.slice(0, shown).map((e) => h('tr', {},
        td(idLink(e.id)),
        td(directionTag(e.direction) || h('span', { class: 'faint' }, '—')),
        td(statusTag(e.strength) || h('span', { class: 'faint' }, '—')),
        td(e.claim_tier ? tag(e.claim_tier, '', `claim tier: ${e.claim_tier}`) : h('span', { class: 'faint' }, '—')),
        td(proofTag(e.proof_status) || h('span', { class: 'faint' }, '—')),
        td(e.hypothesis_id ? idLink(e.hypothesis_id) : h('span', { class: 'faint' }, '—')),
        h('td', { style: 'max-width:560px;min-width:180px' },
          h('div', { class: 'clamp2' }, e.title || h('span', { class: 'faint' }, '(no statement)'))),
        h('td', { class: 'mono faint', style: 'white-space:nowrap' }, fmtDate(e.date))))))
      : h('div', { class: 'empty' }, 'no evidence matches'));
    fill(more, shown < r.length
      ? h('button', { class: 'btn', onclick: () => { shown += 200; draw(); } }, `show ${Math.min(200, r.length - shown)} more`)
      : null);
    replaceRoute('#/findings', { tab: 'evidence', polarity: f.polarity, strength: f.strength, tier: f.tier, proof: f.proof, q: f.q });
  }
  const toggle = (group) => (key, el) => {
    f[group].has(key) ? f[group].delete(key) : f[group].add(key);
    el.setAttribute('aria-pressed', f[group].has(key));
    shown = 100; draw();
  };
  const ec = d.evidence_counts;
  const top = (map, n) => Object.entries(map).slice(0, n).map(([key, count]) => ({ key, count }));
  const facets = h('section', { class: 'panel' }, h('div', { class: 'panel-body stack', style: 'gap:10px' },
    facetRow('points at', ['supports', 'weakens', 'mixed', 'neutral'].map((key) => ({ key, count: ec.polarity[key] || 0,
      title: key === 'neutral' ? 'says nothing about any hypothesis' : key === 'mixed' ? 'revises, partially corroborates, or cuts both ways' : '' })),
      (k) => f.polarity.has(k), toggle('polarity'),
      (i) => h('span', {}, tag(i.key, POLARITY_TONE[i.key]), ` ${i.count}`)),
    facetRow('strength', top(ec.strength, 10), (k) => f.strength.has(k), toggle('strength')),
    facetRow('claim tier', top(ec.claim_tier, 8), (k) => f.tier.has(k), toggle('tier')),
    facetRow('proof status', top(ec.proof_status, 6), (k) => f.proof.has(k), toggle('proof'))));
  const search = h('input', { class: 'mono field', placeholder: 'filter evidence…', value: f.q,
    oninput: (e) => { f.q = e.target.value; shown = 100; draw(); } });
  draw();
  return h('div', { class: 'stack' }, facets, h('div', { class: 'spread' }, summary, search), host, more);
}

function obstructionsTab(d) {
  const note = h('div', { class: 'banner info' }, h('div', {},
    h('b', {}, 'A negative result, as a measurement. '),
    'An obstruction records what blocks an approach as a quantity over a stated scope — not "we could not make it work" but the number that stops it — so later work can compare it, re-scope it, or read it the other way round as a resource. ',
    'Each block also records whether that reversal was examined.'));
  if (!d.obstructions.length) return h('div', { class: 'stack' }, note, h('div', { class: 'empty' }, 'no obstruction blocks recorded'));
  const idsOrText = (items) => h('div', { class: 'row', style: 'gap:6px' }, items.map(idOrText));
  return h('div', { class: 'stack' }, note, d.obstructions.map((o) => h('section', { class: 'panel obstruction' },
    h('div', { class: 'panel-body stack', style: 'gap:10px' },
      h('div', { class: 'spread' },
        h('div', { class: 'row' }, idLink(o.evidence_id), directionTag(o.direction), statusTag(o.strength),
          o.claim_tier ? tag(o.claim_tier, 'info', 'claim tier') : null),
        h('div', { class: 'row faint mono', style: 'font-size:11px' },
          o.hypothesis_id ? h('span', { class: 'row', style: 'gap:4px' }, 'hypothesis', idOrText(o.hypothesis_id)) : null,
          o.goal_id ? h('span', { class: 'row', style: 'gap:4px' }, '· goal', idOrText(o.goal_id)) : null,
          o.date ? `· ${fmtDate(o.date)}` : null)),
      h('div', { style: 'font-size:13.5px;line-height:1.55;font-weight:600' }, linkify(o.statement)),
      h('dl', { class: 'kv glance' },
        o.quantity ? kv('quantity', h('div', { class: 'glance-text' }, linkify(o.quantity))) : null,
        o.value ? kv('measured value', h('div', { class: 'glance-text mono' }, linkify(o.value))) : null,
        o.scope ? kv('scope', h('div', { class: 'glance-text' }, linkify(o.scope))) : null,
        o.measured_by.length ? kv('measured by', idsOrText(o.measured_by)) : null,
        kv('read the other way?', h('div', { class: 'glance-text' },
          o.resource_examined === true ? tag('examined', 'ok') : o.resource_examined === false ? tag('not examined', 'warn') : tag('unstated'),
          o.resource_reading ? [' ', linkify(o.resource_reading)] : null,
          o.spawned_ids.length ? [' · spawned ', idsOrText(o.spawned_ids)] : null)))))));
}

function openProblemsTab(d, params) {
  let only = params.get('status') || 'open';
  let q = params.get('q') || '';
  const area = params.get('area') || '';
  const list = h('div', { class: 'stack' });
  const summary = h('div', { class: 'faint mono' });
  function draw() {
    const needle = q.trim().toLowerCase();
    const rows = d.open_problems.filter((p) =>
      (only === 'all' || (only === 'open' ? p.status === 'open' : p.status !== 'open'))
      && (!area || p.area === area || (p.areas || []).includes(area))
      && (!needle || `${p.id} ${p.title} ${p.statement} ${p.tags.join(' ')}`.toLowerCase().includes(needle)));
    summary.textContent = `${rows.length} of ${d.open_problems.length} open problems${area ? ` in ${area}` : ''}`;
    fill(list, rows.length ? rows.map((p) => h('section', { class: 'panel' },
      h('div', { class: 'panel-body stack', style: 'gap:8px' },
        h('div', { class: 'spread' },
          h('div', { class: 'row' }, idLink(p.id), tag(p.status || 'unstated', p.status === 'open' ? 'warn' : 'info')),
          h('div', { class: 'faint mono', style: 'font-size:11px' },
            p.added ? `added ${fmtDate(p.added)}` : null, p.cited_by ? ` · cited by ${p.cited_by}` : null)),
        h('h4', { style: 'font-size:14px;line-height:1.4' }, h('a', { href: `#/record/${p.id}` }, p.title)),
        p.statement ? h('div', { style: 'line-height:1.6' }, linkify(p.statement)) : null,
        h('dl', { class: 'kv glance' },
          p.current_state ? kv('current state', h('div', { class: 'glance-text' }, linkify(p.current_state))) : null,
          p.resolution ? kv('what would resolve it', h('div', { class: 'glance-text' }, linkify(p.resolution))) : null),
        p.tags.length ? h('div', { class: 'row', style: 'gap:4px' }, p.tags.slice(0, 8).map((t) => tag(t))) : null)))
      : h('div', { class: 'empty' }, 'no open problems match'));
    replaceRoute('#/findings', { tab: 'open', status: only === 'open' ? '' : only, q, area });
  }
  const chips = choiceChips([['open', 'open'], ['closed', 'resolved'], ['all', 'all']], only, (k) => { only = k; draw(); });
  const search = h('input', { class: 'mono field', placeholder: 'filter open problems…', value: q,
    oninput: (e) => { q = e.target.value; draw(); } });
  draw();
  return h('div', { class: 'stack' },
    h('div', { class: 'spread' },
      h('div', { class: 'row' }, chips,
        area ? h('a', { class: 'chip', href: '#/findings?tab=open', title: 'clear the area filter' }, `${area} ×`) : null),
      h('div', { class: 'row' }, summary, search)),
    list);
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

  fill(root, h('div', { class: 'stack' },
    snapshotBanner(),
    h('div', { class: 'spread' },
      choiceChips([
        ['active', 'active'],
        ['ecc', 'ECC active', 'ECC goals are selected before all others'],
        ['attention', 'wants attention'],
        ['retired', 'retired'],
        ['all', 'all'],
      ], filters.only, (key) => { filters.only = key; draw(); }),
      h('div', { class: 'row' }, summary,
        h('input', { class: 'mono field', placeholder: 'filter goals…',
                     oninput: (e) => { filters.text = e.target.value; draw(); } }))),
    grid));
  draw();
}

// The order a goal's trail is shown in: what it produced first, then how it
// got there. Checkpoints are left out because the goal page has its own panel
// for them.
const TRAIL_ORDER = ['KN:FIND', 'EV', 'DEC', 'H', 'EXP', 'RQ', 'IDEA', 'TASK', 'CORR', 'KN:OPEN', 'KN:TECH', 'KN:LIT', 'KN:OTHER', 'OTHER'];
const TRAIL_LABEL = {
  'KN:FIND': 'findings', EV: 'evidence', DEC: 'decisions', H: 'hypotheses', EXP: 'experiments',
  RQ: 'questions', IDEA: 'proposals', TASK: 'handoffs', CORR: 'corrections',
  'KN:OPEN': 'open problems', 'KN:TECH': 'techniques', 'KN:LIT': 'literature', 'KN:OTHER': 'knowledge', OTHER: 'other',
};

/** Records that cite a goal, grouped by what they are. */
function trailGroups(ids) {
  const groups = new Map();
  for (const id of ids) {
    const r = state.byId.get(id);
    if (!r || r.kind === 'BATCH' || r.kind === 'GOAL') continue;
    const key = r.kind === 'KN' ? `KN:${KN_FAMILY[r.area] ? r.area : 'OTHER'}` : (TRAIL_LABEL[r.kind] ? r.kind : 'OTHER');
    (groups.get(key) ?? groups.set(key, []).get(key)).push(r);
  }
  for (const rows of groups.values()) rows.sort((a, b) => (b.date || '').localeCompare(a.date || '') || a.id.localeCompare(b.id));
  return TRAIL_ORDER.filter((k) => groups.has(k)).map((k) => [k, groups.get(k)]);
}

function trailPanel(key, rows) {
  const LIMIT = 8;
  const host = h('div', { class: 'scroll-x' });
  const draw = (all) => fill(host, recordTable(all ? rows : rows.slice(0, LIMIT), { compact: true }),
    !all && rows.length > LIMIT
      ? h('div', { style: 'padding:8px 10px' }, h('button', { class: 'btn', onclick: () => draw(true) }, `show all ${rows.length}`))
      : null);
  draw(false);
  return panel(`${TRAIL_LABEL[key]} (${rows.length})`, null, host);
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
  const trail = trailGroups(goal.mentions || []);
  const findings = trail.find(([k]) => k === 'KN:FIND');

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
      // Buttons, not `#trail-…` anchors: the hash is the router's, and a
      // same-page anchor would be read as a route.
      h('div', { class: 'row', style: 'gap:6px' }, trail.map(([k, rows]) =>
        h('button', { class: 'chip', onclick: () => {
          const target = document.getElementById(k === 'KN:FIND' ? 'goal-findings' : `trail-${k.replace(':', '-')}`);
          if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } }, `${rows.length} ${TRAIL_LABEL[k]}`))),
      h('dl', { class: 'kv' },
        kv('path', pathLink(goal.path)),
        kv('batch', goal.current_batch_id || '—'),
        kv('updated', goal.updated_at || '—'),
        kv('created', goal.created_at || '—'),
        kv('layout', goal.sharded ? 'sharded (checkpoints/)' : 'flat'),
        kv('budget', budgetLine(goal.budget)))));

  fill(root, h('div', { class: 'stack' },
    snapshotBanner(), head,
    findings ? panel(`Findings from this goal (${findings[1].length})`, 'promoted into the knowledge corpus',
      h('div', { class: 'scroll-x' }, recordTable(findings[1], { compact: true })), { id: 'goal-findings' }) : null,
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
          h('td', { class: 'mono faint' }, fmtDate(c.recorded_at)),
          h('td', {}, h('div', { class: 'clamp3' }, linkify(c.summary || '—')))))))) : null),
    h('section', { class: 'panel' },
      h('div', { class: 'panel-head' }, h('h3', {}, 'Bound records'),
        h('span', { class: 'faint' }, 'named in the goal record itself')),
      h('div', { class: 'panel-body stack' },
        linkedBlock('research questions', goal.question_ids),
        linkedBlock('active hypotheses', goal.active_hypothesis_ids))),
    trail.length ? h('div', {}, kicker('record trail — everything that cites this goal, by kind')) : null,
    trail.filter(([k]) => k !== 'KN:FIND').map(([k, rows]) => {
      const p = trailPanel(k, rows);
      p.id = `trail-${k.replace(':', '-')}`;
      return p;
    })));
}

function linkedBlock(label, ids) {
  const head = kicker(label);
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
    kind: new Set(split(params.get('kind'))),
    area: new Set(split(params.get('area'))),
    status: new Set(split(params.get('status'))),
    bodies: params.get('bodies') === '1',
  };
  $('#q').value = f.q;
  let shown = PAGE;

  const results = h('div', { class: 'panel scroll-x' });
  const meta = h('div', { class: 'faint mono' });
  const more = h('div', {});
  const note = h('div', {});

  const pushRoute = () => replaceRoute('#/records',
    { q: f.q, kind: f.kind, area: f.area, status: f.status, bodies: f.bodies ? '1' : '' });

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

  const toggle = (group) => (key, el) => {
    f[group].has(key) ? f[group].delete(key) : f[group].add(key);
    el.setAttribute('aria-pressed', f[group].has(key));
    shown = PAGE; pushRoute(); draw();
  };

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
      facetRow('kind', facets.kinds, (k) => f.kind.has(k), toggle('kind'),
        (i) => `${i.label} ${i.count.toLocaleString()}`),
      // A knowledge entry's family lives in the same column as an area, so
      // the same filter reaches it; it is only shown as its own row.
      facetRow('knowledge', facets.knowledge || [], (k) => f.area.has(k), toggle('area'),
        (i) => `${i.label} ${i.count.toLocaleString()}`),
      facetRow('area', facets.areas.slice(0, 60), (k) => f.area.has(k), toggle('area'), (i) =>
        h('span', {}, i.ecc ? h('span', { class: 'tag acc', style: 'margin-right:4px' }, 'ECC') : null,
          `${i.key} ${i.count}`)),
      facetRow('status', facets.statuses.slice(0, 40), (k) => f.status.has(k), toggle('status'),
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
  const isEntry = s.kind === 'KN';
  const front = isEntry && body.body && typeof body.body === 'object' ? body.body : null;

  const panes = {};
  const paneHost = h('div', { class: 'panel-body' });
  const tabs = h('div', { class: 'tabs' });
  function show(key) {
    fill(paneHost, panes[key] ??= buildPane(key, body, src));
    for (const t of tabs.children) t.setAttribute('aria-selected', t.dataset.key === key);
  }
  const tabList = isEntry
    ? [['entry', 'entry'], ['structured', 'front matter']]
    : [['structured', 'record']];
  tabList.push(['source', 'source'],
    ['links', `links (${body.links.out.length}↗ ${body.links.in.length}↙)`]);
  for (const [key, label] of tabList) {
    tabs.append(h('button', { class: 'tab', 'data-key': key, onclick: () => show(key) }, label));
  }

  const linkList = (title, ids) => h('section', { class: 'panel' },
    h('div', { class: 'panel-head' }, h('h3', {}, `${title} (${ids.length})`)),
    h('div', { class: 'panel-body stack', style: 'gap:5px;max-height:420px;overflow:auto' },
      ids.length
        ? ids.map((rid) => {
            const r = state.byId.get(rid);
            return h('div', { class: 'row', style: 'gap:6px' },
              idLink(rid), r ? h('span', { class: 'faint', style: 'font-size:11px' }, kindLabel(r)) : null,
              r ? (r.kind === 'DEC' ? decisionTag(r.status) : statusTag(r.status)) : null);
          })
        : h('span', { class: 'faint' }, 'none')));

  // What the header says about the record, per kind: an entry shows its
  // proof status, confidence and tier; everything else its status.
  const headerTags = isEntry
    ? [tag(kindLabel(s)),
       front?.proof_status ? proofTag(String(front.proof_status)) : null,
       front?.claim_tier ? tag(String(front.claim_tier), 'info', 'claim tier') : null,
       front?.confidence ? tag(clip(String(front.confidence), 40), '', `confidence: ${front.confidence}`) : null,
       front?.status ? statusTag(String(front.status)) : null,
       front?.superseded_by ? tag(`superseded by ${front.superseded_by}`, 'bad') : null,
       front?.withdrawn_by ? tag(`withdrawn by ${front.withdrawn_by}`, 'bad') : null]
    : [tag(kindLabel(s)),
       s.area ? h('a', { href: `#/records?area=${s.area}` }, s.ecc ? tag(s.area, 'acc') : tag(s.area)) : null,
       s.kind === 'DEC' ? decisionTag(s.status) : statusTag(s.status)];

  const parseBadge = body.verified
    ? tag('parsed', 'ok', 'A real YAML parse of the record on disk')
    : isEntry
      ? tag(body.parse_error || 'no front matter', 'warn', 'The entry body is shown; its metadata could not be read')
      : tag('parse failed', 'bad', body.parse_error || '');

  fill(root, h('div', { class: 'stack' },
    snapshotBanner(),
    !body.verified && body.parse_error && !isEntry
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
            headerTags,
            s.date ? timeEl(s.date, { label: 'declared by the record', dateOnly: true, style: 'date' }) : null),
          parseBadge),
        s.title ? h('h2', { style: 'font-size:16px;line-height:1.4' }, s.title) : null,
        isEntry && Array.isArray(front?.tags) && front.tags.length
          ? h('div', { class: 'row', style: 'gap:4px' }, front.tags.slice(0, 12).map((t) => tag(String(t)))) : null,
        h('div', { class: 'row faint mono', style: 'font-size:11px' },
          h('span', {}, s.path),
          src ? h('a', { href: src, target: '_blank', rel: 'noreferrer' }, 'source ↗') : null,
          // Observed, not declared. Named "committed" for exactly that reason.
          s.committed ? h('span', { class: 'row', style: 'gap:5px' }, '· committed',
            timeEl(s.committed, { label: 'first committed' })) : null,
          s.last_commit && s.committed && s.last_commit - s.committed > 60
            ? h('span', { class: 'row', style: 'gap:5px' },
                '· last changed', timeEl(s.last_commit, { label: 'most recent commit touching this file' }))
            : null))),
    h('div', { class: 'detail' },
      h('section', { class: 'panel' }, tabs, paneHost),
      h('aside', { class: 'stack' },
        linkList('Cited by', body.links.in), linkList('Cites', body.links.out)))));
  show(tabList[0][0]);
}

function buildPane(key, body, src) {
  if (key === 'entry') {
    if (typeof body.markdown === 'string' && body.markdown.trim()) return renderMarkdown(body.markdown);
    return h('div', { class: 'empty stack', style: 'gap:10px' },
      h('div', {}, 'This entry has no body text.'),
      src ? h('a', { class: 'btn', href: src, target: '_blank', rel: 'noreferrer' },
        `open ${body.summary.path} on GitHub ↗`) : null);
  }
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
  const glance = body.summary.kind === 'KN' ? null : glanceBlock(body.summary.kind, body.body);
  return h('div', { class: 'stack', style: 'gap:16px' },
    glance ? h('div', {}, kicker('at a glance'), glance) : null,
    h('div', {}, glance ? kicker('full record') : null, yamlTree(body.body)));
}

const REPO_PATH_RE = /^(?:coordination|experiments|ledger|knowledge|docs|tools|inputs|harness|orchestration|src)\/[\w./~+-]+$/;

/** A parsed record as a collapsible tree, with identifiers linked. */
function yamlTree(value, depth = 0) {
  if (value === null || value === undefined) return h('span', { class: 'yaml-null' }, 'null');
  if (typeof value !== 'object') {
    if (typeof value === 'boolean' || typeof value === 'number') {
      return h('span', { class: 'mono', style: 'color:var(--accent)' }, String(value));
    }
    const text = String(value);
    // A repository path is a link to the file at the built commit.
    if (REPO_PATH_RE.test(text) && sourceUrl(text)) return pathLink(text);
    return h('span', { class: 'yaml-scalar' }, linkify(text));
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
// How the experiments table can be ordered. "Activity" is the default and
// means the most recent moment anything is known to have happened to a
// contract -- its last run, or failing that its own commit.
const EXPERIMENT_SORTS = {
  activity: { label: 'latest activity', key: (e) => -(e.last_run || e.committed || 0) },
  runs: { label: 'most runs', key: (e) => -e.run_count },
  duration: { label: 'longest measured', key: (e) => -(e.total_seconds || 0) },
  approved: { label: 'date on the contract', key: (e) => -(asDate(e.dated)?.getTime() || 0) },
  id: { label: 'identifier', key: (e) => e.id },
};

async function viewExperiments(params) {
  setCrumb('experiments');
  const root = fill(view(), loading());
  if (!state.ready) return;
  const payload = state.experimentsPayload ??= await getJSON('experiments.json');
  state.experiments ??= payload.experiments;
  const timing = payload.timing || {};

  let only = params.get('only') || 'with-runs';
  let sort = EXPERIMENT_SORTS[params.get('sort')] ? params.get('sort') : 'activity';
  let text = params.get('q') || '';
  let expanded = null;                                   // one experiment's runs, open
  const host = h('div', { class: 'panel scroll-x' });
  const meta = h('div', { class: 'faint mono' });

  const runStatus = {};
  let runTotal = 0;
  for (const e of state.experiments) for (const r of e.runs) { runStatus[r.status] = (runStatus[r.status] || 0) + 1; runTotal += 1; }
  const withRuns = state.experiments.filter((e) => e.run_count).length;

  function rows() {
    const needle = text.trim().toLowerCase();
    const out = state.experiments.filter((e) => {
      if (only === 'with-runs' && !e.run_count) return false;
      if (only === 'no-runs' && e.run_count) return false;
      if (only === 'ecc' && !e.ecc) return false;
      if (only === 'timed' && !e.runs_timed) return false;
      return !needle || `${e.id} ${e.title} ${e.status} ${e.hypothesis_id}`.toLowerCase().includes(needle);
    });
    const key = EXPERIMENT_SORTS[sort].key;
    return out.sort((a, b) => {
      const ka = key(a); const kb = key(b);
      return (ka < kb ? -1 : ka > kb ? 1 : 0) || a.id.localeCompare(b.id);
    });
  }

  /** The runs of one contract, each with whatever time it actually has. */
  function runTable(e) {
    return h('tr', { class: 'run-detail' }, h('td', { colspan: '8' },
      h('div', { class: 'stack', style: 'gap:8px' },
        h('div', { class: 'row faint', style: 'font-size:11.5px' },
          `${e.run_count} run${e.run_count === 1 ? '' : 's'}`,
          e.runs_timed ? h('span', {}, `· ${e.runs_timed} report a start time`) : null,
          e.runs_measured ? h('span', {}, `· ${e.runs_measured} report a duration`) : null,
          h('span', {}, '· "committed" is when git first saw the run’s artifacts, not when it started')),
        h('div', { class: 'scroll-x' }, h('table', { class: 'dense' },
          thead(['run', 'status', { label: 'started', title: 'declared by the run manifest' },
            { label: 'finished', title: 'declared by the run manifest' },
            { label: 'duration', title: 'declared, or measured from start and finish' },
            { label: 'committed', title: 'observed: when git first saw this run’s artifacts' }]),
          h('tbody', {}, e.runs.map((r) => h('tr', {},
            h('td', { class: 'mono' }, r.id),
            td(statusTag(r.status) || h('span', { class: 'faint' }, '—')),
            td(timeEl(r.started, { label: 'started (declared)' })),
            td(timeEl(r.finished, { label: 'finished (declared)' })),
            td(r.duration_seconds !== null && r.duration_seconds !== undefined
              ? h('span', { class: 'mono' }, fmtDuration(r.duration_seconds))
              : h('span', { class: 'faint' }, '—')),
            td(timeEl(r.committed, { label: 'first committed' }))))))))));
  }

  function draw() {
    const list = rows();
    meta.textContent = `${list.length} of ${state.experiments.length} experiments`;
    fill(host, list.length ? h('table', { class: 'dense' },
      thead(['id', 'status', 'runs',
        { label: 'contract date', title: 'the date the contract itself declares, under its own field name' },
        { label: 'committed', title: 'observed: when git first saw the specification' },
        { label: 'last run', title: 'the most recent moment any run of this contract is known at' },
        { label: 'measured', title: 'total wall-clock across runs that report a duration' },
        'title']),
      h('tbody', {}, list.flatMap((e) => {
        const open = expanded === e.id;
        const row = h('tr', { class: e.run_count ? 'clickable-row' : '', onclick: e.run_count
          ? () => { expanded = open ? null : e.id; draw(); } : null },
          td(idLink(e.id)),
          td(h('div', { class: 'row', style: 'gap:4px' },
            statusTag(e.status) || h('span', { class: 'faint' }, '—'),
            // A contract that is not `specification.yaml` is said so rather
            // than normalised away: an experiment whose protocol was never
            // committed machine-readably is a fact about the corpus.
            e.contract === 'specification.json'
              ? tag('json', 'info', 'the contract is specification.json') : null,
            e.contract === ''
              ? tag('no contract', 'warn',
                  'this directory holds runs but no machine-readable contract') : null)),
          td(e.run_count
            ? h('span', { class: 'row', style: 'gap:5px' }, runPills(e.runs),
                h('span', { class: 'faint mono', style: 'font-size:10px' }, open ? '▾' : '▸'))
            : h('span', { class: 'faint' }, 'never run')),
          td(e.dated
            ? h('span', { class: 'row', style: 'gap:5px' },
                timeEl(e.dated, { label: e.date_field, dateOnly: true, style: 'date' }),
                h('span', { class: 'faint mono', style: 'font-size:10px' },
                  (e.date_field || '').replace(/_/g, ' ')))
            : h('span', { class: 'faint', title: 'this contract declares no date of its own' }, '—')),
          td(timeEl(e.committed, { label: 'first committed', style: 'date' })),
          td(timeEl(e.last_run, { label: 'latest run activity' })),
          td(e.total_seconds
            ? h('span', { class: 'mono', title: `${e.runs_measured} of ${e.run_count} runs report a duration` },
                fmtDuration(e.total_seconds))
            : h('span', { class: 'faint' }, '—')),
          h('td', { style: 'max-width:460px;min-width:160px' },
            h('div', { class: 'clamp2' }, e.title || '—')));
        return open ? [row, runTable(e)] : [row];
      })))
      : h('div', { class: 'empty' }, 'no experiments match'));
    replaceRoute('#/experiments', { only: only === 'with-runs' ? '' : only,
      sort: sort === 'activity' ? '' : sort, q: text });
  }

  const timingPanel = panel('What is known about when',
    'declared by the records, and observed from git history',
    h('div', { class: 'panel-body stack', style: 'gap:10px' },
      h('div', { class: 'stat-row' },
        statCard(timing.runs?.toLocaleString() ?? '—', 'runs'),
        statCard(`${timing.runs_with_declared_start ?? 0}`, 'declare a start time',
          { title: 'run manifests carrying started_at' }),
        statCard(`${timing.runs_with_duration ?? 0}`, 'report a duration'),
        statCard(timing.total_measured_seconds ? fmtDuration(timing.total_measured_seconds) : '—',
          'total measured', { title: 'summed across only the runs that report one' }),
        statCard(`${timing.experiments_dated ?? 0}`, 'contracts self-dated',
          { title: `of ${timing.experiments ?? 0}; the rest are dated by their commit` })),
      timing.git?.available
        ? h('div', { class: 'row faint', style: 'font-size:11.5px' },
            'Run activity spans ', timeEl(timing.earliest, { label: 'earliest', style: 'date' }),
            ' to ', timeEl(timing.latest, { label: 'latest', style: 'date' }),
            h('span', {}, ` · commit dates from ${(timing.git.commits || 0).toLocaleString()} commits`))
        : h('div', { class: 'banner warn', style: 'font-size:11.5px' },
            h('div', {}, h('b', {}, 'Commit dates unavailable. '),
              timing.git?.error || 'git history could not be read',
              ' — only dates the records declare themselves are shown.'))));

  fill(root, h('div', { class: 'stack' },
    snapshotBanner(),
    h('div', { class: 'grid',
      style: 'grid-template-columns:repeat(auto-fit,minmax(340px,1fr));align-items:start' },
      timingPanel,
      panel('Runs by terminal status',
        `${runTotal.toLocaleString()} runs across ${withRuns} contracts · ${(state.experiments.length - withRuns).toLocaleString()} have never run`,
        h('div', { class: 'panel-body' }, distribution(runStatus, {})))),
    h('div', { class: 'spread' },
      choiceChips([['with-runs', 'with runs'], ['no-runs', 'never run'],
        ['timed', 'with a declared start'], ['ecc', 'ECC'], ['all', 'all']],
        only, (key) => { only = key; expanded = null; draw(); }),
      h('div', { class: 'row' }, meta,
        h('select', { class: 'mono field', title: 'sort order',
          onchange: (ev) => { sort = ev.target.value; draw(); } },
          Object.entries(EXPERIMENT_SORTS).map(([key, s]) =>
            h('option', { value: key, selected: key === sort }, s.label))),
        h('input', { class: 'mono field', placeholder: 'filter…', value: text,
                     oninput: (ev) => { text = ev.target.value; draw(); } }))),
    h('div', { class: 'faint', style: 'font-size:11.5px;margin-top:-4px' },
      'Click a contract with runs to see each run’s times. Hover any date for the exact instant in UTC.'),
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
              h('td', { class: 'mono' }, pathLink(u.path)),
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
    if (path === '/findings') return await viewFindings(params);
    if (path === '/goals') return await viewGoals();
    if (path === '/records') return await viewRecords(params);
    if (path === '/experiments') return await viewExperiments(params);
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
    state.overview = state.goals = state.experiments = state.findings = null;
    state.experimentsPayload = null;
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
      const p = new URLSearchParams(parseHash().path === '/records' ? parseHash().params : '');
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
