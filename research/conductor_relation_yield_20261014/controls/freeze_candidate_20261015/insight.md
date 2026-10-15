# Source-freeze candidate controls

- **Question:** Do the current 20-arm matrix, deterministic preparer, fixed-panel identity checker, seed-custody source list, and execution-script syntax agree before any scientific seed is drawn?
- **Workload:** Six archived endpoint models; all four arm constructions checked with eight public fixed test targets each; the 20-arm formal matrix checked separately; no random seed issue and no full endpoint relation collection.
- **Controls and raw evidence:** [receipt.json](receipt.json) binds the current plan and source hashes, exact commands, timings, versions and raw RSS field. [Preparer stdout/stderr](0.stdout), [panel checker stdout/stderr](1.stdout), [custody matrix stdout/stderr](2.stdout), and [syntax stdout/stderr](3.stdout) are retained. Every command exited 0. Earlier preparer and panel control attempts remain in their own directories.
- **Interpretation:** This is an implementation source-freeze candidate, not an approved or published experimental freeze. The canonical experiment, admission, post-freeze seed issue and commitment, 20 full-size outputs, independent completeness results, and post-seal reveal remain outstanding.

The preparer was amended afterward to retain each rejected target and random-base draw. A separate [amendment receipt](rejections_receipt.json), [stdout](rejections.stdout), and [stderr](rejections.stderr) bind the passing control for that source version. The original receipt remains unchanged.
