# PDF text extraction — unblock log

**Task:** `TASK-20260805-c89efb` (REC-2) · **Goal:** `GOAL-SSIQ-001` · **Batch:** `BATCH-002`
**Date (UTC):** 2026-08-05 · **Repo commit:** `ab8e3ad8f93b84f197aef647746a36ef0d7cd359` (clean)

**Result: UNBLOCKED. Four independent routes now work in this environment.**
The blocker was diagnosed to root cause and is a one-package fix.

Written so the next batch does not repeat any of this. Every route attempted is
listed, including the ones that failed and the one that was not attempted.

---

## 1. Environment as found

| item | value |
|---|---|
| OS | Ubuntu 24.04.4 LTS |
| Python | 3.11.15 (`/usr/local/bin/python3`), GCC 13.3.0 |
| `sys.path` order | `/root/.local/lib/python3.11/site-packages` → `/usr/local/lib/python3.11/dist-packages` → `/usr/lib/python3/dist-packages` |
| PDF libraries present | `pypdf` 6.14.2 only (`/usr/local/lib/python3.11/dist-packages`) |
| PDF binaries present | **none** — `pdftotext`, `mutool`, `gs`, `qpdf`, `pdftk` all absent |
| package manager | `apt-get` present; `pip` present |
| `cryptography` | present but **distro-packaged**, at `/usr/lib/python3/dist-packages/cryptography` |
| `cffi` / `_cffi_backend` | **ABSENT** |

## 2. Route R0 — baseline reproduction of the reported failure

Command: `python3 -c "import pypdf"`

Outcome: **FAILS**, exactly as reported in `BATCH-002-OPENING.md` § 4. Trace tail:

```
ModuleNotFoundError: No module named '_cffi_backend'
thread '<unnamed>' panicked at /usr/share/cargo/registry/pyo3-0.20.2/src/err/mod.rs:788:5:
Python API call failed
...
  File ".../pypdf/_crypt_providers/__init__.py", line 31, in <module>
    from pypdf._crypt_providers._cryptography import (
  File ".../pypdf/_crypt_providers/_cryptography.py", line 31, in <module>
    from cryptography.hazmat.primitives.ciphers.algorithms import AES
  File "/usr/lib/python3/dist-packages/cryptography/exceptions.py", line 9, in <module>
    from cryptography.hazmat.bindings._rust import exceptions as rust_exceptions
pyo3_runtime.PanicException: Python API call failed
```

### 2.1 Root cause (this is the useful part)

**The panic has nothing to do with pypdf, with PDF parsing, or with any PDF file.**
It happens at `import pypdf`, before any document is opened.

Chain: `pypdf` → `pypdf._crypt_providers._cryptography` → distro `cryptography`
→ `cryptography.hazmat.bindings._rust` (a **pyo3 0.20.2** extension) → that module
imports `_cffi_backend` → **`cffi` is not installed** → `ModuleNotFoundError` is
raised *inside* a pyo3 boundary, which converts the Python error into a Rust
`PanicException` and prints a backtrace.

So the `pyo3_runtime` panic is a **missing transitive dependency of the
distro-packaged `cryptography`**, surfaced with an unhelpful message. It is
environment breakage, not a library bug and not a defect of any source PDF.

## 3. Routes attempted, in order

| # | route | command | outcome | version installed |
|---|---|---|---|---|
| **R0** | `pypdf`, as found | `python3 -c "import pypdf"` | **FAIL** — `pyo3_runtime.PanicException` at import (§ 2) | pypdf 6.14.2 (pre-existing) |
| **R1** | **fix the root cause: install `cffi`** | `python3 -m pip install cffi` | **WORKS.** After it, `import pypdf` succeeds and `PdfReader(...).pages[i].extract_text()` extracts the 53-page arXiv PDF (119 626 chars) and the 30-page proceedings PDF | **cffi 2.1.1** |
| **R2** | poppler `pdftotext`, no index refresh | `apt-get install -y poppler-utils` | **FAIL** — `E: Failed to fetch …poppler-utils_24.02.0-1ubuntu9.8_amd64.deb 404 Not Found`; exit 100. Stale apt index pinned a superseded version | — |
| **R3** | poppler `pdftotext`, after index refresh | `apt-get update && apt-get install -y poppler-utils` | **WORKS.** `pdftotext -layout in.pdf out.txt` | **poppler-utils 24.02.0-1ubuntu9.9**, `libpoppler134` 24.02.0-1ubuntu9.9 (binary reports `pdftotext version 24.02.0`) |
| **R4a** | `pdfminer.six` via module runner | `python3 -m pdfminer.high_level file.pdf > out.txt` | **FAIL, SILENTLY** — exit 0, **0 bytes** written. `pdfminer.high_level` is not a CLI entry point; it succeeds at doing nothing. Do not use this invocation | pdfminer.six 20260107 |
| **R4b** | `pdfminer.six` via its script | `pdf2txt.py file.pdf -o out.txt` | **WORKS.** 5.4 s for 53 pages, 132 461 chars | **pdfminer.six 20260107** |
| **R5** | PyMuPDF (MuPDF bindings; covers the "mutool" suggestion in-process) | `pip install pymupdf`, then `pymupdf.open(f)` + `page.get_text()` | **WORKS.** Fastest and cleanest Unicode of the four | **PyMuPDF 1.28.0 / MuPDF 1.29.0** |
| **R6** | standalone `mutool` binary | — | **NOT ATTEMPTED.** Four routes already worked; recorded as *untried*, not as known-broken, so a later session does not mistake absence for failure | — |
| **R7** | pure-Python zlib/Flate fallback decoder | — | **NOT ATTEMPTED**, same reason as R6. It remains the correct last resort if every packaged route is ever unavailable | — |

### 3.1 Minimal recipe for the next batch

```sh
python3 -m pip install cffi          # fixes the pyo3_runtime panic; pypdf then works
apt-get update && apt-get install -y poppler-utils   # pdftotext -layout
python3 -m pip install pdfminer.six pymupdf          # two more independent routes
```

Installing `cffi` alone is sufficient to unblock `pypdf`. The other three are worth
having because they fail differently (see § 5), which is what makes cross-checking
a quotation meaningful.

## 4. Packages installed by this task

Recorded per the task constraint "installing a package is permitted for extraction
only; record exactly what was installed and its version".

- pip: **`cffi` 2.1.1** (also pulled `pycparser`)
- pip: **`pdfminer.six` 20260107** (also pulled `charset-normalizer`)
- pip: **`pymupdf` 1.28.0** (MuPDF 1.29.0)
- apt: **`poppler-utils` 24.02.0-1ubuntu9.9**, **`libpoppler134` 24.02.0-1ubuntu9.9** (+ their apt-resolved dependencies)

Nothing was removed, downgraded, or pinned. No repository file outside this task's
write scope was touched. These are environment changes and are **not** committed
artifacts; they must be reinstalled in a fresh container using § 3.1.

## 5. Extraction fidelity — cross-check, and a hazard that matters for exponent work

All four working routes were run on the same file (EUROCRYPT 2024 proceedings
chapter, SHA-256 `55c054a8…`) and compared on the passages quoted in
`cascade_cost_note.md`.

**Agreement:** all four reproduce the wording of Theorem 7.2 and Proposition 8.5
identically. That three-way agreement (poppler / pdfminer.six / PyMuPDF) is the
basis on which those statements are quoted as verbatim.

**Divergences observed:**

| symptom | poppler `pdftotext -layout` | `pypdf` | `pdfminer.six` | PyMuPDF |
|---|---|---|---|---|
| the letter `ℓ` | **DROPPED** — "reduces to -IsogenyPath" | correct `ℓ` | **`(cid:2)`** | correct `ℓ` |
| word spacing in theorem headers | correct | mangled — "Proposition 8.5 ( Isogeny reducesto EndRing)" | correct | correct |
| two-column / displayed-math layout | best with `-layout` | poor | good | good |

**HAZARD — superscripts and subscripts are flattened by every route.** In all four
extractions, Eq. (1) of `[35]` comes out as

```
[End(E) : R1] ≤ 23k1 λ(log p)+2 /p = 2O(log(p)·λ(log p))
```

whose actual meaning is `[End(E) : R_1] ≤ 2^{3k_1·λ(log p)+2}/p = 2^{O(log(p)·λ(log p))}`.
A reader or script that takes extracted text literally will read "23k1" as a number
and "2O(...)" as a product. **Any exponent read out of an extracted PDF must be
confirmed against the rendered page or by internal consistency before it is used in
exponent bookkeeping.** This is a live risk for exactly the kind of work
`GOAL-SSIQ-001` does, and it is why the § 4/§ 5 quotations in
`cascade_cost_note.md` were checked across three extractors rather than one.

## 6. Network notes for the next batch (details in `source_access_log.yaml`)

- `eprint.iacr.org` returns **HTTP 403 with a Cloudflare "Just a moment…" managed
  challenge** to plain `curl`, both with the default UA and with a browser UA. The
  agent proxy reported `recentRelayFailures: []`, so this is an **origin-side bot
  challenge, not an org egress denial**. Do not spend a batch on it. It was not
  retried further.
- Working substitutes, all HTTP 200 in this environment:
  `arxiv.org/pdf/<id>`; `api.archives-ouvertes.fr/search/` (HAL, JSON, excellent
  for locating author versions by title); `inria.hal.science|hal.science/<halId>/document`;
  and — notably — **`link.springer.com/content/pdf/<DOI>.pdf`, which returned the
  full 30-page EUROCRYPT chapter, not a preview**. Springer is the route that
  yielded the exact version `[35]` names.
- `api.semanticscholar.org` returned **404** for this DOI.
- `link.springer.com/content/pdf/10.1007/978-3-032-12296-4_9.pdf` (reference `[33]`)
  returned **HTTP 200 with `Content-Type: text/html`** — a landing page, not a PDF.
  A 200 is not evidence of a PDF; always check `file`/`Content-Type`.
- No ar5iv/HTML fallback was needed: primary PDFs were obtained for `[35]` (three
  renderings) and `[33]`. Consequently nothing in `cascade_cost_note.md` is
  labelled as HTML-rendering-sourced.
