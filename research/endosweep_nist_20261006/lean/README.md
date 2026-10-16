# Generator for the NIST/Koblitz Lean certificates

`formal/CryptoResearch/Endosweep/NistCertificates.lean` and `Koblitz.lean`
carry data blocks (big integers) generated from this directory's parent
(`nist.json`, `factorizations.jsonl`) and the std-curves checkout pinned in
`nist.json` (commit `77fe6e3585ca2c2225b59d7df24b7c775437276f`):

```sh
python3 research/endosweep_nist_20261006/lean/gen_endosweep_lean.py . /path/to/std-curves
```

The generator recomputes every number and refuses to write if anything
disagrees, so a stale input fails here rather than in Lean. The proofs in the
templates (`*.lean.in`) are hand-written; only the data is generated.
