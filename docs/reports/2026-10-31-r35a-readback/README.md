# R35a publication readback and claim boundary, 2026-10-31

This is a read-only custody audit of the named R35a degree-4 Boolean closure certificate, selected as a concrete candidate for the [finite-profile problem](../../../problems/lastfall-finite-profile-completeness.md). It does not rerun `cert_check.py`, the closure producer, the unsatisfiability count, or the branching upper-bound check.

## Inputs and reproducible check

- Repository records: [R35a publication](../../../analysis/semaev-m2-last-fall-degree/submission-20261029/archive/R35a.publication.json) and [R35a receipt](../../../analysis/semaev-m2-last-fall-degree/submission-20261029/archive/R35a.receipt.json), whose source commit is `a084a6417cdd4bed187f07479333aa4285547c1b` and producer binary SHA-256 is `f7f920e697b263129e91b44814e18c32b228392496770c29869ab4d00a9e6f04`.
- Public release: `semaev-closure-certificates-20261029`, assets `R35a.D4.cert.gz`, `R35a.evidence.tar.gz`, `R35a.receipt.json`, and `R35a.publication.json`.
- Download command: `gh release download semaev-closure-certificates-20261029 --repo isogeny-labs/crypto-autoresearcher --dir RELEASE_DIR --pattern 'R35a.*'`.
- Offline verification: `python3 docs/reports/2026-10-31-r35a-readback/verify_readback.py RELEASE_DIR > readback.json`. The committed [readback record](readback.json) is the output of this exact check on 2026-10-31 UTC.

All three assets listed inside the tracked publication record matched its lengths and SHA-256 values. The downloaded receipt and publication record were byte-identical to the tracked copies. Streaming decompression of the 39,637,109-byte certificate asset produced 44,830,496 bytes matching the receipt's `certificate.bin` SHA-256 `762d296afb38710b582cbb1d3619b591d45e593024a21683bcb864cdb999759c`. Every receipted small evidence member in the release tar matched its length and hash. The tar also contains `attempt/result.json`, which is not individually listed in the certificate receipt but is covered by the release tar's SHA-256.

The verifier produced byte-identical JSON under ordinary Python and `python3 -O`. A one-byte receipt mutation was rejected under `python3 -O` with `ValueError: R35a.receipt.json`; this checks that validation does not depend on Python assertions being enabled.

## Claim boundary

The historical receipt reports `certificate_verified`, a zero exit from its independent checker, `1 not in W_4`, and a **codimension lower bound** of 5,287. The certificate check establishes `W_4` is contained in the kernel of its dual map; it does not prove equality with that kernel or the producer's exact dimension. The [dated correction](../../../analysis/semaev-m2-last-fall-degree/results/verification-correction-20261019.md) makes this distinction explicitly and retains a counterexample to the equality shortcut.

The receipt's own `d_ref_exact` field is null and its `d_ref_lower_bound` is 5. The broader [verification record](../../../analysis/semaev-m2-last-fall-degree/results/verification.md) separately describes an unsatisfiability count and two degree-4 restricted refutations to obtain the upper bound at degree 5. This readback has not independently replayed those steps or the certificate algebra. It therefore verifies published bytes and historical claim labeling, not an exact `d_F=5` conclusion.

The next gate is an admitted, memory-bounded replay of the exact published certificate with `verify/cert_check.py`, followed by separate verification of unsatisfiability, both restricted refutations, and the Boolean-to-polynomial closure bridge. The source receipt's conservative checker planning bound is 4,016,352,301 bytes and its 40 GiB virtual-memory limit is **not a measured RSS**; a safe host slot must be checked live before replay. No new run or cloud worker was started for this readback.
