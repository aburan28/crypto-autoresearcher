# TASK-20260814-9081e8 -- Lane B corpus inventory

Written BEFORE any extraction, per this task's own completion gate and per
CORR-20260813-1a06db (the defect this task exists to not repeat: BATCH-973b49
asserted no resource-estimation paper had been filed, when one had been, and
the corpus was not searched before that assertion was made).

## Retrieval-index attempt and outcome (record first, per constraint 3)

`search_knowledge` (the crypto-kb MCP tool) is **not present in this session's
tool list at all** -- this executor session was launched without the
`crypto-kb` MCP server attached, so there was no `search_knowledge`,
`get_context`, `get_source` or `find_related` call available to invoke. This
is consistent with, but stronger than, the dispatching session's note that
`CRYPTO_KB_QDRANT_URL` was `:memory:`: here the retrieval tool itself was
unreachable, not merely empty-backed.

**THE CORPUS WAS NOT SEARCHED BY THE RETRIEVAL INDEX.** This is not a claim
that the corpus is empty or thin -- see below, it is neither. What was done
instead, per constraint 3's fallback: a `Grep` sweep of
`knowledge/literature/` and `knowledge/techniques/` for author names and
domain terms (`Gidney`, `Ekera`/`Ekerå`, `Litinski`, `Roetteler`, `Häner`/
`Haener`, `Jaques`, `surface code`, `magic state distillation`, `logical
qubit`, `resource estimat*`, `Toffoli`, `Shor`), followed by reading every
file the sweep returned. A first, broader sweep on generic terms (`quantum`,
`Toffoli`, `surface code`, `magic state`, `physical qubit`) hit the 250-file
`Grep` cap and was not usable as an inventory by itself (the corpus is large
and many hits are peripheral crypto papers that merely mention "quantum" in
passing); the narrower author/domain-term sweep below is what actually
enumerates the on-point set.

## Sources the queue's `filed_sources_inventory` named, re-confirmed present

- `KN-LIT-099` -- Roetteler, Naehrig, Svore, Lauter, ASIACRYPT 2017 (iacr:2017/598)
- `KN-LIT-771` -- Häner, Jaques, Naehrig, Roetteler, Soeken, arXiv:2001.09580 (2020)
- `KN-LIT-1882` -- Luo, Yang, Wang, Su, Li, arXiv:2604.02311 (2026)
- `KN-LIT-1222` -- "ECPM Cryptanalysis Resource Estimation" (iacr:2024/1767)
- `KN-TECH-037` -- reads KN-LIT-099's table; source_refs [KN-LIT-098, KN-LIT-099, KN-TECH-005]

All five are present and readable exactly as the queue described.

## Sources the sweep found THAT THE QUEUE'S INVENTORY DID NOT NAME

These are new to this task's sweep and belong at the top per constraint 2.

1. **`KN-LIT-7657`** -- Khajeian, "Resource Estimation of the Distributed
   Quantum Algorithm for the Elliptic Curve Logarithm Problem", IACR ePrint
   2026/1244. `citation_verified: web` (abstract-page only, not full-text
   read), `confidence: reported`. Directly on-topic (distributed-QPU ECDLP
   resource estimate at 256-bit), but every headline figure in the filed
   entry is explicitly **per-node**, not a total, and the entry's own "Not
   verified here" section says the total resource cost is not stated in the
   abstract it was read from. Not used as a reproduction target here: its
   filed body carries no full-pipeline total to reproduce, and per constraint
   6/8 this task does not fetch and reconstruct new tables from sources
   outside the three named identifiers without a stated reason to add one.
   **Flagged as a candidate for a future lane-B pass** if the Coordinator
   wants a third target and is willing to add its eprint identifier to the
   fetch list.

2. **`KN-LIT-1797`** -- garbled title/author metadata ("Optimized Point
   Addition Circuits for Elliptic" / authors listed as
   "Curve Discrete Logarithms"), iacr:2026/1128, arXiv:2606.02235. Bulk-seeded
   (2026-07-24 pass), abstract-level only. Its own filed body states it is a
   **survey/commentary** on other papers' resource reductions (Chevignard et
   al. CRYPTO 2024, Gidney 2025, Babbush et al. 2026 vs. Litinski 2023) rather
   than a primary resource-estimation paper with its own table. Recorded here
   as found, not extracted as a reproduction target: reproducing a survey's
   restatement of someone else's numbers would not satisfy criterion 1's
   "that paper's own stated inputs."

3. **`KN-LIT-1134`** -- Kim, Hong, "New Space-Efficient Quantum Algorithm for
   Binary Elliptic Curves using the Optimized Division Algorithm", arXiv:2303.06570
   (2023). Bulk-seeded, abstract-level only. On-topic (binary-field ECDLP
   qubit/Toffoli trade-off) but **binary-field**, not prime-field, so it is a
   different curve representation than GOAL-QRE-001's `scheme_context`
   (prime-field ECDLP). Not extracted; flagged for the record.

4. **`KN-LIT-3073`** -- Banegas, Bernstein, van Hoof, Lange, "Concrete quantum
   cryptanalysis of binary elliptic curves". Bulk-seeded, abstract-level only,
   no year/venue recorded. Binary-field, same scope objection as above. Its
   abstract-relayed closed forms (`7n + floor(log2 n) + 9` qubits,
   `48n^3 + ...` Toffoli) are recorded in the filed body but are explicitly
   not admissible per constraint 5 (bulk-seeded body, not full-text read by
   this task). Not extracted.

5. **`KN-LIT-6085`** / **`KN-LIT-126`** -- Jaques, Schanck, "Quantum
   Cryptanalysis in the RAM Model: Claw-Finding Attacks on SIKE" (two filed
   entries for the same paper, one bulk-seeded at CRYPTO 2019 venue metadata
   missing, one with fuller bibliographic verification). Isogeny/SIKE claw-
   finding, not ECDLP or RSA Shor-based factoring. Out of `scheme_context`
   scope for this goal; not extracted.

6. **`KN-LIT-679`** -- Jaques, Naehrig, Roetteler, "Implementing Grover
   oracles for quantum key search on AES and LowMC". Symmetric-key Grover
   search, not Shor-based ECDLP/RSA. Out of scope; not extracted.

7. **`KN-LIT-129`** -- Chavez-Saab et al., "The SQALE of CSIDH". CSIDH
   quantum security, explicitly a different problem family
   (`GOAL-QRE-001.non_duplication` reserves CSIDH quantum-cost reconstruction
   to `GOAL-CSIDH-001`). Not extracted; recorded for completeness only.

## Candidate reproduction targets carried forward to `source_extraction.yaml`

Three sources, all with full-text obtained by this task (see "How full text
was obtained" below) and all directly reporting a Shor-ECDLP resource
pipeline with a numeric table at named curve sizes including 256-bit:

1. `KN-LIT-099` -- Roetteler, Naehrig, Svore, Lauter 2017 (iacr:2017/598).
   THE SINGLE BEST-SUPPORTED TARGET: its filed entry already quotes the
   table numerically (`citation_verified: read`, no bulk-seed caveat), and
   this task independently re-fetched the ePrint PDF and confirmed the same
   numbers appear in the source text verbatim (see `source_extraction.yaml`).
2. `KN-LIT-771` -- Häner, Jaques, Naehrig, Roetteler, Soeken 2020
   (arXiv:2001.09580). Filed entry is bulk-seeded and carries no numeric
   table (per its own "Not verified here" section and CORR-20260813-1a06db's
   caveat). This task fetched the arXiv PDF full text directly and extracted
   its Table 1 (Shor-ECDLP resource estimates at 256/384/521-bit, three
   optimization strategies) and its asymptotic closed forms. Every number
   used from this source is tagged `from_fetched_fulltext`, never
   `from_filed_entry_text`, per constraint 5.
3. `KN-LIT-1882` -- Luo, Yang, Wang, Su, Li 2026 (arXiv:2604.02311). Same
   situation: filed entry bulk-seeded, no numeric table in the filed body.
   This task fetched the arXiv PDF full text and extracted Table 1 (modular-
   inversion qubit comparison), Table 2 (concrete per-curve logical-qubit
   comparison against RNSL17/HJN+20), Table 5/6 (Toffoli/CNOT breakdown) and
   the closed forms. Every number tagged `from_fetched_fulltext`.

`KN-LIT-1222` (ECPM Cryptanalysis, iacr:2024/1767) was READ (its filed body)
but not fetched in full text this pass: its filed entry is bulk-seeded,
abstract-level, and its own key claims describe "preliminary results" without
a numeric table in the relayed abstract text, so there was nothing concrete
to attempt to cross-check against a fetch within this task's declared scope
(the three named identifiers). It is recorded in `source_extraction.yaml` as
a fourth entry with every field `not_determinable`, per the completion gate's
"fewer with an explicit statement of why no more were obtainable." Its
eprint identifier (`iacr:2024/1767`) is available for a future fetch pass if
the Coordinator wants a fourth candidate target.

## How full text was obtained

`downloads/` is absent from this checkout, confirmed by direct filesystem
check (`ls downloads` → No such file or directory), matching the queue's
`local_pdf_availability` note. Per constraint 6, this task fetched the three
named identifiers directly:

- `https://eprint.iacr.org/2017/598.pdf` -- HTTP 200, 791174 bytes,
  sha256 `27c923cd3330dbaa69ee306d9ebcfa7a768f5c8a81ad03ba274c5dd28260d5d1`
- `https://arxiv.org/pdf/2001.09580` -- HTTP 200, 518891 bytes,
  sha256 `66fd5d283cbde6327d79cee5d5660ad31feac6db82d21b5dff620acee4a993b2`
- `https://arxiv.org/pdf/2604.02311` -- HTTP 200, 699569 bytes,
  sha256 `2991dd2ead2821e815893efc5d3b3db191d04e9d27ece1fc8e7ff02fea25c1f8`

Text was extracted with `pdfminer.six` (`extract_text`) run locally in the
scratchpad, not committed anywhere under this repository. The fetched PDFs
and extracted text live only in the session scratchpad
(`/tmp/claude-0/.../scratchpad/`), which is outside this task's write scope
and is not part of the reproduction package; the numbers pulled from them are
recorded in `source_extraction.yaml` with page/section pointers so a future
session can re-fetch and re-verify independently, which is exactly what the
Validator's provenance audit (TASK-20260814-8a9638) is instructed to do.

## Recommended supersessions (for the Coordinator; knowledge/ not written here)

1. **`KN-LIT-771` and `KN-LIT-1882`**: both should be superseded by a
   fully-verified entry that quotes their numeric tables directly (Table 1 of
   2001.09580; Tables 1/2/5/6 of 2604.02311), replacing the abstract-level
   bulk-seeded bodies. The numbers this task extracted in
   `source_extraction.yaml` are ready to seed that supersession; they should
   not be copy-pasted into the existing entries (knowledge entries are
   immutable) but used as the content of new superseding entries.
2. **`KN-LIT-1797`**: its title and author fields are corrupted
   ("Optimized Point Addition Circuits for Elliptic" / author field
   "Curve Discrete Logarithms" -- these are clearly a mis-split of one
   title). Recommend a superseding entry with corrected bibliographic
   metadata; this task did not fetch arXiv:2606.02235 to fix it, since fixing
   filed-entry metadata is outside lane B's extraction scope.
3. **`KN-LIT-7657`**: `citation_verified: web` only (abstract page, not
   full-text). If the Coordinator wants this distributed-QPU estimate as a
   future reproduction target, it needs a full-text fetch and verification
   pass first; its per-node/total qualifier distinction matters and cannot be
   resolved from the abstract alone (the filed entry says so itself).

No number from `KN-LIT-771`, `KN-LIT-1882`, `KN-LIT-1797`, `KN-LIT-1134`,
`KN-LIT-3073`, `KN-LIT-6085`, `KN-LIT-126`, `KN-LIT-7657` or `KN-LIT-1222`
was taken from a bulk-seeded or abstract-level filed-entry body and recorded
as `from_filed_entry_text` anywhere in this task's output. Where this task
uses a number from `KN-LIT-771` or `KN-LIT-1882` it is because that number
was independently re-derived from a fetched full-text PDF this task
downloaded itself, and is tagged accordingly.
