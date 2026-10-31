# R35a publication readback and claim boundary, 2026-10-31

This is a read-only custody and certificate audit of the named R35a degree-4 Boolean closure result, selected as a concrete candidate for the [finite-profile problem](../../../problems/lastfall-finite-profile-completeness.md). It does not rerun the closure producer, the unsatisfiability count, or the branching upper-bound check.

The [evidence diagram](custody.svg) and [one-page PDF](report.pdf) show the verified custody and checker chain separately from the open exact-degree obligations. The PDF was generated from [report.typ](report.typ) with Typst 0.15.0, rendered to an image, visually inspected at page scale, and text-extracted before publication. Its 44,161 bytes are below the repository's 64 KiB direct-file threshold.

## Inputs and reproducible check

- Repository records: [R35a publication](../../../analysis/semaev-m2-last-fall-degree/submission-20261029/archive/R35a.publication.json) and [R35a receipt](../../../analysis/semaev-m2-last-fall-degree/submission-20261029/archive/R35a.receipt.json), whose source commit is `a084a6417cdd4bed187f07479333aa4285547c1b` and producer binary SHA-256 is `f7f920e697b263129e91b44814e18c32b228392496770c29869ab4d00a9e6f04`.
- Public release: `semaev-closure-certificates-20261029`, assets `R35a.D4.cert.gz`, `R35a.evidence.tar.gz`, `R35a.receipt.json`, and `R35a.publication.json`.
- Download command: `gh release download semaev-closure-certificates-20261029 --repo isogeny-labs/crypto-autoresearcher --dir RELEASE_DIR --pattern 'R35a.*'`.
- Offline verification: `python3 docs/reports/2026-10-31-r35a-readback/verify_readback.py RELEASE_DIR > readback.json`. The committed [readback record](readback.json) is the output of this exact check on 2026-10-31 UTC.
- Certificate replay after admission: decompress the SHA-checked `R35a.D4.cert.gz` to `certificate.bin`, then run `python3 docs/reports/2026-10-31-r35a-readback/replay_certificate.py certificate.bin docs/reports/2026-10-31-r35a-readback/replay`. The [replay script](replay_certificate.py) checks the certificate and pinned checker source hashes before execution.

All three assets listed inside the tracked publication record matched its lengths and SHA-256 values. The downloaded receipt and publication record were byte-identical to the tracked copies. Streaming decompression of the 39,637,109-byte certificate asset produced 44,830,496 bytes matching the receipt's `certificate.bin` SHA-256 `762d296afb38710b582cbb1d3619b591d45e593024a21683bcb864cdb999759c`. Every receipted small evidence member in the release tar matched its length and hash. The tar also contains `attempt/result.json`, which is not individually listed in the certificate receipt but is covered by the release tar's SHA-256.

The verifier produced byte-identical JSON under ordinary Python and `python3 -O`. A one-byte receipt mutation was rejected under `python3 -O` with `ValueError: R35a.receipt.json`; this checks that validation does not depend on Python assertions being enabled.

## Claim boundary

The historical receipt reports `certificate_verified`, a zero exit from its independent checker, `1 not in W_4`, and a **codimension lower bound** of 5,287. A fresh [bounded replay](replay/replay.json) of the pinned checker source (`13d926240a99de4b3eede374932fe245d62e7de65102a4fdf2cccfb0e4463877`) on the SHA-matched decompressed certificate exited zero in 23.166 seconds. Its [stdout](replay/checker.stdout.txt) confirms C0, C1, C2 and C3 on 66,712 monomials, 35 equations and all 36 variables; stderr is empty. All 13 substantive lines match the historical receipt after removing timing annotations. The replay used a 12 GiB virtual-memory limit, admitted 39,855,042,560 available physical bytes, held `/tmp/crypto-bench.lock`, and stopped if a competing compiler appeared or the 16 GiB reserve fell away. It was not stopped.

The certificate establishes `W_4` is contained in the kernel of its dual map; it does not prove equality with that kernel or the producer's exact dimension. The [dated correction](../../../analysis/semaev-m2-last-fall-degree/results/verification-correction-20261019.md) makes this distinction explicitly and retains a counterexample to the equality shortcut.

The receipt's own `d_ref_exact` field is null and its `d_ref_lower_bound` is 5. The broader [verification record](../../../analysis/semaev-m2-last-fall-degree/results/verification.md) separately describes an unsatisfiability count and two degree-4 restricted refutations to obtain the upper bound at degree 5. This audit has not independently replayed those separate steps. It therefore validates the named lower-bound certificate, not an exact `d_F=5` conclusion.

The next gate is separate verification of unsatisfiability, both restricted refutations, and the Boolean-to-polynomial closure bridge. The source receipt's conservative checker planning bound was 4,016,352,301 bytes and its 40 GiB virtual-memory limit was **not a measured RSS**. No new scientific run or cloud worker was started for this audit.
