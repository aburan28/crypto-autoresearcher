# INC-20260725-EXFAT-02 — second checkpoint payload destruction

- **Window:** machine reboot ~2026-07-25T01:38Z (wiped /var/tmp + /tmp); worktree
  contents of the live checkpoint dir found deleted at inspection 04:58Z; the
  state dir mtime stamps the modification at **04:20:15Z** (≈40 min after reboot).
- **Lost:** all 16 RAWCARR1 carry payloads (cols 4,000–124,000 of the rebuilt
  cell), state.json, plus every untracked/non-current-branch experiment file in
  the worktree (rawbit instrument, codec gate artifacts, STATE-RESCUE.json,
  checkpoint-summary.json, analysis.md, ledger entry — all restored from git).
- **Survived on volume:** the 2 legacy pickle carries (cols 0–4,000), the
  adjacency cache, and the entire `.git` object store (both incidents).
- **Pattern:** identical to INC-20260724-EXFAT-01 — bulk payloads destroyed,
  small files and `.git` spared; directory listings stable afterward (not a
  transient flap at inspection time). Root cause still undetermined; the volume
  remains untrusted for sole-copy payloads.
- **Impact:** rebuilt cell rolled back from 124,000 to 4,000 verified columns.
  120,000 columns of turn-2 compute lost; ZERO mathematical loss (no rank
  claim existed; AGENTS rules 5–6).
- **Recovery (executed immediately):** state.json reconstructed from the
  committed 52,000-col snapshot truncated to the 2 sha256-verified surviving
  pickle carries; resume identity checks passed; cell resumed at 04:58Z+.
- **Countermeasure now in force:** after EVERY invocation, new carry payloads
  are written into the git object store (`hash-object -w`; content-addressed,
  survived both incidents) and logged in `mirror-log.json`; state.json mirrored
  per invocation. Payloads are recoverable even if the worktree is swept again.
