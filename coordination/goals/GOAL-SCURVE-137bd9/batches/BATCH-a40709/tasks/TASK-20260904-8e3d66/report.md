# S2 — TASK-20260904-8e3d66 — execution report

**Task** TASK-20260904-8e3d66 (slot S2) · **Batch** BATCH-a40709 · **Goal** GOAL-SCURVE-137bd9
**Experiment** EXP-SCURVE-3f87f6 · **Lane** L0 · **Role** executor
**Produced** 2026-09-05, at repository commit `816fa7c8e9704e9316bc534b57c2629061a069e9`
**Archived by** TASK-20260904-fa10f7 (slot S4). Nothing here is staged or committed by this slot.

## Approval pointer (condition C-2 of DEC-20260904-5216dd)

EXP-SCURVE-3f87f6 **is approved with conditions** by **DEC-20260904-5216dd**, committed at
`359b70177`. **The contract file itself still reads `status: draft` and `approved_by: null`, and
always will** — its bytes are hash-bound by the completed TASK-20260904-850ff6 snapshot archive
(`path_sha256` at commit `b012132b2`), so writing `approved_by` into it would permanently break that
archive. A reader who checks only the contract file will wrongly conclude no approval exists. This
pointer is reproduced in all four YAML artifacts of this slot as well as here.

## Claim ceiling, restated before anything else

- Claim tier **`analyzed` at best**, never `supported`.
- **No statement is made anywhere in these artifacts that any curve is or is not safe, unsafe,
  vulnerable or secure.** Those words appear in this package only inside verbatim quotations of
  retrieved sources (SafeCurves prose and the `verify.sage` listing, which uses identifiers such as
  `safefield` and `safecurve`). Reproducing a source's own tokens is transcription.
- **No criterion cell is adjudicated**, for NIST P-224 or any other curve. Comparing a measured
  quantity against a threshold belongs to slot S7 alone, behind a gate this slot does not open.
- **No arithmetic was performed.** Not one integer operation on any curve quantity. CAP-2 was not run
  and is not relied upon.
- **A retrieved page is a SOURCE, not a certificate.** Retrieval establishes what a source says. It
  establishes nothing about any curve.

## CAP-1, re-probed in this session

The driving session recorded a CAP-1 PASS at 2026-09-05T00:12:04Z. **Reachability is per-session,
never per-repository**, so it was re-probed here before being relied on: all ten named L0 targets
returned **HTTP 200** between 00:19:55Z and 00:19:58Z. The probe response bodies *are* the stored
pages, so the probe and the retrieval are the same bytes. No impediment was raised.

Recorded as an observation and not as proof of anything: the ten byte counts measured here are
identical to the ten in `capability-checks/CAP-1-20260905T001204Z.yaml`. Equal length is not equal
content; the sha256 of every stored page is in the manifest so content can be checked directly.

CAP-4 (label gotcha) re-checked on the stored index bytes: the lowercase token `nistp224` occurs
**0** times (0 case-insensitively); the label form `NIST P-224` occurs **2** times.

## What was retrieved

21 pages, every attempt HTTP 200 on first request, no retries, nothing omitted. Per-page URL, fetch
timestamp, retrieved byte length and sha256 are in `retrieved-pages/manifest.yaml`; every attempt is
also in the attempt table of `retrieval-log.yaml`.

| group | count | pages |
| --- | --- | --- |
| named L0 targets | 10 | index, rho, transfer, disc, rigid, ladder, twist, complete, ind, verify |
| remaining criterion pages | 3 | field, equation, base |
| control-curve sources | 8 | RFC 5114, RFC 7748, RFC 8032, four neuromancer.sk pages, SEC 2 v2 PDF |

The three extra SafeCurves pages were fetched because three of the eleven criteria — `field`,
`equation`, `base` — have their own pages that are not among the ten named targets, and every
threshold had to be quotable from bytes fetched in this session rather than recalled.

No mirror and no cached copy was used. Every byte came from the URL recorded beside it.

## What was transcribed

**Eleven of eleven criterion cells are RETRIEVED. Zero are UNRETRIEVED.** The cell list —
`field, equation, base, rho, transfer, disc, rigid, ladder, twist, complete, ind` — is read off the
criterion column headers of the retrieved index page, not from memory.

`threshold-table.yaml` carries **52 direct quotations** across the eleven cells. Each quotation names
the stored page it came from, the source URL, the fetch timestamp and that page's sha256. Each cell
is quoted both from its prose page and, where the retrieved `verify.sage` listing states a
machine-checkable form, from `verify.html` as well.

**Every one of the 52 quotations was verified locatable inside the stored bytes** by automated
substring match after whitespace normalisation. A quotation that could not be located was not
recorded; none failed.

`control-curve-capsule.yaml` carries **39 fields across 6 curves**, each with per-field provenance
and an explicit per-field two-source-agreement statement:

| curve | role in the plan | sources retrieved |
| --- | --- | --- |
| NIST P-192 | parameter-matched negative 1/2 | RFC 5114 §2.4, neuromancer.sk |
| NIST P-256 | parameter-matched negative 2/2 | RFC 5114 §2.6, neuromancer.sk, SafeCurves |
| secp256k1 | D3 positive control | neuromancer.sk, SafeCurves |
| Curve25519 | Montgomery positive control | RFC 7748 §4.1, SafeCurves |
| Curve1174 | Edwards positive control | SafeCurves, neuromancer.sk |
| edwards25519 / Ed25519 | the alternative Edwards positive control the audit plan permits | RFC 7748 §4.1, RFC 8032 §5.1 |

Two-source agreement was **obtained on 26 of the 39 fields**, by textual comparison only. Where it
was not obtained the capsule says so per field with the reason, which is always one of three:

- the two sources publish the field in **different bases** (reconciling them is base conversion,
  which is arithmetic, which this slot may not do) — both values are recorded verbatim so a slot that
  may compute can settle it;
- the two sources publish **different curve models** (Curve1174: SafeCurves gives the Edwards model,
  neuromancer a short Weierstrass model, so only `p` is comparable without a model conversion);
- **only one source was obtained** for that field.

One caveat is flagged in the capsule and repeated here because it is easy to miss: for
edwards25519 / Ed25519 the **second source is not independent of the first**. RFC 8032 §5.1 states
each parameter by explicit reference to RFC 7748 ("p of edwards25519 in [RFC7748]"). It does repeat
the numerals, so the textual check is real, but it is not two independent derivations and must not be
counted as one.

## What failed

Nothing mathematical. Two tooling absences and one caught defect, all in `retrieval-log.yaml`:

- **OBS-2** — the SEC 2 v2 PDF retrieved (HTTP 200, 306784 bytes) and is stored, but **no PDF text
  extractor exists in this session** (`pdftotext` absent; `pypdf` and `PyPDF2` not importable), so it
  was **not transcribed and is quoted nowhere**. What this blocks is a *third* source for three
  curves; the capsule already carries two for those fields. Clears when a session with a PDF
  extractor runs the transcription against the stored file, whose sha256 is in the manifest.
- **OBS-3** — **no `search_knowledge` tool is present in this subagent's tool surface**, so no query
  was issued and none is reported as issued. The query strings that would have been issued are
  recorded. This licenses no inference of any kind: it is a fact about the session, not about the
  index and not about what this program has tried. Nothing in this package asserts that any quantity
  has or has not previously been computed here, so the obligation's trigger was never reached.
- **OBS-6** — four RFC 8032 values failed the first locatability check, because that RFC states them
  inside an ASCII table whose values wrap across pipe-bordered cells. The normaliser was widened to
  strip pipes and all four then located. **No value was recorded on a failed check.** Recorded
  because it happened.

## Anomaly for the Coordinator

**OBS-4.** The adapter binds `executor-implementation` to `anthropic:claude-sonnet-5` (effort
`medium`); the model that actually answered this task is **claude-opus-5**. Under this runtime,
per-role *model* selection is process-level (CLAUDE.md, "Model policy note") — the subagent inherits
the session's model and cannot choose one. No fallback path was taken, no stated requirement was
degraded, and the requested policy was honoured in role, authority, tool surface and effort. It is
recorded rather than resolved here because an Executor may not alter its own model or reasoning level
(AGENTS.md core rule 11). The retrieved content does not depend on it: it is bytes from named URLs
with recorded digests.

No probe-verification of the resolved model was performed in this subagent
(`adapter doctor --probe` was not run), so `model_verified` is recorded as not probe-verified.

Bedrock was not used and not probed. No provider, backend, endpoint, fallback or model identifier
containing `bedrock` was selected or contacted; all retrieval was plain HTTPS via curl.

## Budget

| limit | allowed | used |
| --- | --- | --- |
| wall clock | 1800 s | about 960 s, measured from recorded command timestamps |
| runs (external-retrieval invocations) | 12 | 4 (N1–N4) |
| memory | 2 GB | no step held more than a few MB; peak RSS was not measured and is not reported as if it were |

## Left for others, deliberately

- **The retrieved-versus-recalled definition comparison** for the three definition-sensitive cells
  (`ladder`, `complete`, `ind`) that batch.yaml flags in advance. The retrieved `verify.sage` text for
  all three is quoted in full in `threshold-table.yaml` so S7 can do it. **This slot asserts no
  difference and no agreement** between the retrieved definitions and any definition a lane was
  drafted against.
- **Every criterion cell**, for every curve. Open and unattempted, here by construction.
- The published per-curve True/False assessment table on the retrieved index page was **not
  transcribed into any cell** of these artifacts. It is present in the stored bytes for whoever is
  authorised to read it as a preregistered comparison target; reproducing it here would have been a
  cell rendered by a slot that may not render cells.

## Artifacts

All five under `coordination/goals/GOAL-SCURVE-137bd9/batches/BATCH-a40709/tasks/TASK-20260904-8e3d66/`:

- `retrieved-pages/manifest.yaml` — 21 pages, per page URL, fetch timestamp, HTTP status, byte
  length, sha256, role
- `threshold-table.yaml` — eleven cells, 52 quotations, per-quotation provenance
- `control-curve-capsule.yaml` — 6 curves, 39 fields, per-field provenance and agreement status
- `retrieval-log.yaml` — every attempt with status and time, CAP-1 and CAP-4, session and inference
  provenance, run ledger, budget, six operational observations
- `report.md` — this file

Also present, not a declared artifact: `retrieved-pages/*` (the stored bytes themselves) and
`logs/run-R2-cap1.log` (the raw CAP-1 probe transcript).

All four YAML files were parse-checked by loading them with a YAML parser after writing.
