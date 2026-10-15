# Seed custody and arm execution order

No scientific seed has been issued for this study. `plan.json` prespecifies 20
prepared inputs: four arms on each of the four primary endpoints and native
plus random arms on P29 E2 and E3. All arms of an endpoint share its distinct,
nonidentity target vector; the two `u=2` arms transport those targets.

1. Commit the complete source and scientifically fixed `review_required`
   specification. A Coordinator preparation-only decision binds that snapshot
   (the 40-hex `source_freeze_commit`), the exact specification and plan hashes,
   the `scientific_contract.py` digest, and `execution_authorized: false`.
   Commit and publish the decision. `issue_seeds.py --preparation-decision ...`
   checks that every bound source and the specification still matches the
   earlier snapshot and that HEAD is the published decision commit supplied as
   `--freeze-commit`. The private seed files must be outside this repository.
   It draws two independent 256-bit OS seeds and writes only their SHA-256
   commitments and frozen source hashes to the v2 public file. No seed value
   appears on stdout. This decision authorizes preparation only; it grants no
   collector or reveal authority.
2. Commit and publish the public commitment. Prepare each of the 20 inputs
   with `prepare_input.py --commitment ... --target-seed-file ...
   --k-seed-file ... --endpoint ... --arm ... --output-dir ...`. Its CLI
   enforces the 32,768-target schedule and the frozen source hashes. It writes
   a write-once `prepared.txt` and `manifest.json` containing input, base,
   target-vector, source, and commitment digests, plus group and Q metadata.
   The two seed files remain private. Commit and publish all 20 prepared
   inputs and manifests before collection begins.
3. A read-only candidate check must validate the sealed 20-arm package and
   prospective commands. The Coordinator may then approve the scientific
   specification only if its scientific-contract digest still equals the
   preparation snapshot. Commit the final trial plan and dispatcher queue;
   require `newest_experiments --experiment ...` to report `ready` before
   dispatch. For each input, the runner must bind
   the approved admission, run `execute_prepared.py` once in a fresh output
   directory, and preserve all attempts. The wrapper runs the Rust collector,
   independent C++ ordered-count oracle, Python verifier and exact interval
   calculation under the total wall watchdog and memory controls. The
   repository runner's admission, ownership and resource checks remain in
   force. Commit and publish run records before a report.
4. Build a `arity3-sealed-output-index/v1` JSON file with one entry per arm:
   `endpoint`, `arm`, `run_dir`, `input_manifest`, and `receipt_sha256`.
   Commit and publish that index with all 20 completed run receipts and raw
   output files. `reveal_seeds.py` then requires the exact arm set, matching
   source/seed/input/phase digests, the historical preparation-spec hash, the
   unchanged scientific-contract digest of the now approved spec, completed
   admitted receipts, and clean tracked local artifacts before writing a
   write-once reveal record. Publish
   the reveal after the outputs are sealed. Replay target generation from the
   revealed seeds and compare each prepared-input and target-vector SHA-256.

The commitment, preparation and reveal programs have bounded implementation
controls but have not been used with scientific seeds. A local source commit
alone does not authorize seed issue; preparation needs the committed
Coordinator decision, and collection separately needs the approved published
contract and admitted dispatch.
