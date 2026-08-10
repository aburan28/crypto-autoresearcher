---
id: KN-LIT-4fa25d
type: literature
title: "Classic McEliece: conservative code-based cryptography: what plaintext confirmation means"
authors: []
authors_note: >-
  No author list on the title page; issued by the Classic McEliece team. NOT
  filled in from recall.
year: 2022
venue: "Classic McEliece round-4 NIST PQC submission, document dated 23 October 2022"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://classic.mceliece.org/mceliece-pc-20221023.pdf"
  sha256: "9894108c16c2d38de2bac9a9d9f228fe25602acfe9214aba279669f353d2ed99"
tags: [code-based, mceliece, plaintext-confirmation, kem, fujisaki-okamoto, primary-source]
confidence: reported
citation_verified: web
citation_verified_note: >-
  NOT `read`. This one-page document was retrieved and read by
  TASK-20260803-f3aece (BATCH-001) on 2026-08-03 — HTTP 200, 96835 bytes,
  sha256 9894108c…, 1 page, `source_access_log.yaml` seq 15.
  TASK-20260808-f9374d, which files this entry, performed NO retrieval and read
  no PDF. Per RQ-MCE-e65b3c's inherited caution from KN-OPEN-3f7a21, a `read`
  this task cannot attest is not claimed. UPGRADE PATH: re-fetch, compare
  against the sha256 above, transcribe under TASK-20260808-a9f648's convention.
  This one is CHEAP — the document is a single page — and it is the natural
  first candidate if the family is ever to be raised to `read`.
added: "2026-08-08"
superseded_by: null
---

## Contribution

One-page document defining the `pc` (plaintext confirmation) variants as a list
of changes to the cryptosystem specification ([[KN-LIT-84b674]]). It states that
it *"defines exactly the same KEM as the round-3 Classic McEliece submission"*.

## Key claims (as reported)

Provenance for all three: `TASK-20260803-f3aece/parameter_sets.md` §6, a
committed transcription of this document at sha256 `9894108c…`. Not re-read in
this environment.

- Encapsulation gains a step computing a second ciphertext component from a hash
  of the error vector, and sets the ciphertext to the pair. Decapsulation gains a
  re-computation and comparison of that component, falling back to the private
  random string on mismatch.
- The ciphertext becomes the concatenation of a `ceil(mt/8)`-byte first component
  and a `ceil(l/8)`-byte second component. With `l = 256` from the specification's
  Section 6.1, **`pc` ciphertexts are 32 bytes longer than non-`pc` ciphertexts.**
- **The document introduces NO new (m, n, t) values.** The `pc` parameter sets
  share the parameters, and therefore the code rate k/n, of their base sets.

**Deliberately not quoted here.** The passage of this document that states the
ciphertext's two components is precisely the one
`transcription_convention.md` §12 records as **V-1**: `parameter_sets.md` §6
presents it inside a block labelled verbatim after silently restoring
extraction-flattened superscripts. The restoration was confirmed unambiguous and
correct and no number was affected — and reproducing that block here would
propagate an undisclosed editorial step into a second document, which is the
error V-1 exists to stop. The claim is therefore stated in prose above and
**no verbatim block from that passage appears in this entry.** A reader wanting
the exact printed symbols must render the PDF at sha256 `9894108c…`.

## Relevance to this program

Load-bearing for `GOAL-MCE-001`'s scoping, and for a narrow reason: the ISO
standard's parameter list includes `pc` and `pcf` sets that **do not appear in
the specification's Section 7**, so without this document the standardized set
list cannot be mapped onto transcribed parameters at all.

Because `pc` changes no code parameter, the rate table in [[KN-LIT-84b674]]
applies unchanged to the `pc` variants. That is the useful consequence: the
rate side of any comparison against the distinguisher line ([[KN-LIT-3c9f21]],
[[KN-LIT-a4d70e]], [[KN-LIT-6b1fc8]], [[KN-LIT-4c8135]]) does not fork over
`pc`.

## Not verified here

- **This task read nothing** and computed nothing.
- The security argument for plaintext confirmation was not evaluated by anyone
  here. The `fujisaki-okamoto` tag reflects the construction's family, not a read
  of a security proof.
- The separate *"advantages and disadvantages"* statement
  (`nist/mceliece-mods3-20221023.pdf`) was **not fetched** by any task of this
  program.
- **No `pc` numeric size table exists in anything this program has read.** The
  `pc` ciphertext sizes in this program's task artifacts are **computed from the
  sources' formulas, not transcribed**, and `parameter_sets.md` §6 marks them as
  such and states outright that a reviewer wanting a transcribed `pc` size table
  should treat it as **not obtained**. That posture is inherited here unchanged.

## Local copies

None. Third-party copyrighted material, deliberately not committed. The `sha256`
in `identifiers` is the integrity anchor.
