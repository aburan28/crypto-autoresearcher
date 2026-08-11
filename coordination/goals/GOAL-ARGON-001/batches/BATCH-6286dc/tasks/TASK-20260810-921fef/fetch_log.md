# Fetch log — TASK-20260810-921fef (RFC 9106 primary text)

Context: prior attempts via the WebFetch/WebSearch tools failed identically
with a backend-model infrastructure error, unrelated to network access. The
independent Validator run (TASK-20260809-28c68e) demonstrated a raw HTTP
`curl` fetch works in this environment. This task repeats that route directly
via the Bash tool.

## Attempt 1: `.txt` route

Command:

```sh
curl -s -o /tmp/rfc9106_1.txt -w "HTTP_CODE:%{http_code} SIZE:%{size_download}\n" \
  --max-time 20 https://www.rfc-editor.org/rfc/rfc9106.txt
```

Outcome: **SUCCESS**

- `HTTP_CODE:200`
- `SIZE:37228` bytes
- File confirmed on disk: `wc -c /tmp/rfc9106_1.txt` → `37228`
- Content opens with the expected RFC 9106 header block ("Internet Research
  Task Force (IRTF) ... Request for Comments: 9106 ... Argon2 Memory-Hard
  Function for Password Hashing and Proof-of-Work Applications").

No further routes (`.html`, bare `/rfc/rfc9106`) were needed since the first
attempt succeeded on the first try.

## Full-text read

The entire 976-line plaintext file was read in full via the Read tool
(`/tmp/rfc9106_1.txt`, single pass, no truncation — the file is well under
any read-size limit). Sections read in full include:

- Abstract, Status of This Memo, ToC
- Section 1 Introduction, 1.1 Requirements Language
- Section 2 Notation and Conventions
- Section 3 Argon2 Algorithm: 3.1 Inputs/Outputs, 3.2 Operation, 3.3 H',
  **3.4 Indexing (3.4.1 J1/J2 computation for Argon2d/Argon2i/Argon2id,
  3.4.2 mapping to reference block index)**, 3.5 Compression Function G,
  3.6 Permutation P
- **Section 4 Parameter Choice** (recommended settings + the two
  FIRST/SECOND RECOMMENDED option table and the 11-step selection
  procedure)
- Section 5 Test Vectors (5.1 Argon2d, 5.2 Argon2i, 5.3 Argon2id — headers
  and structure, not transcribed verbatim into the KN-LIT entry since raw
  test-vector bytes are not needed for a literature citation)
- Section 6 IANA Considerations
- Section 7 Security Considerations (7.1–7.4, including the trade-off
  attack reduction factors and recommendations)
- Section 8 References (8.1 Normative, 8.2 Informative)
- Acknowledgements, Authors' Addresses

No section was skipped or summarized-without-reading. This log documents
that Section 3.4 and Section 4 in particular — the two sections the handoff
named as required for precise transcription — were read directly from the
fetched primary text, not reconstructed from memory or from the prior
Validator's 7-claim spot-check table.
