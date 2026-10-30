# Commands and execution record

This record reproduces the substantive commands and relevant tool outputs from
the blind review. The implementation was created with `apply_patch` directly in
the assigned directory. Shell commands used `login=false`.

## First filesystem read and hash verification

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib
p = Path('/var/tmp/binstd-round2-blind-20261027/statement.json')
b = p.read_bytes()
h = hashlib.sha256(b).hexdigest()
print('statement_sha256:', h)
assert h == '2bbf336b088ff099546bcc3b5f3612f439ba2b7aa69a5007c6d02fcdb590f664'
print(b.decode())
PY
```

Exit 0; verified hash:
`2bbf336b088ff099546bcc3b5f3612f439ba2b7aa69a5007c6d02fcdb590f664`.
The statement printed in full and was the only source read at this point.

## Claim

```bash
conductor task claim T-617
```

Exit 127: `/bin/bash: line 1: conductor: command not found`.
The coordinator then supplied the absolute path, without a filesystem search:

```bash
/home/ec2-user/.local/bin/conductor task claim T-617
```

Exit 0. Claimed `T-617 — BINSTD blind arithmetic prospective round`.
Lease `dddfc602-046b-4b62-b749-37fb1306031d`, epoch 1, expires 10:33PM UTC.
Holding directory was the assigned `reports/TASK-20261027-b17d02` directory.
No automatic session adoption was reported; release before expiry is required.

## Directory creation and exact arithmetic

```bash
mkdir -p /home/ec2-user/crypto-autoresearcher-binstd-formal-review-20261027/research/binstd_formal_review_round2_20261027/reports/TASK-20261027-b17d02
python3 /home/ec2-user/crypto-autoresearcher-binstd-formal-review-20261027/research/binstd_formal_review_round2_20261027/reports/TASK-20261027-b17d02/check_exact.py > /home/ec2-user/crypto-autoresearcher-binstd-formal-review-20261027/research/binstd_formal_review_round2_20261027/reports/TASK-20261027-b17d02/raw_output.txt
```

The arithmetic command was run twice, both exit 0. The second run followed the
addition of an explicit intermediate degree-16 product assertion and printout.
`raw_output.txt` and `results.json` contain the final run. No arithmetic checks
failed unexpectedly in either run. Three deliberately false target assertions
were caught as required negative controls in each run.

The final output records these results, with complete divisor rows in the file:

```
DEGREE16_PRODUCT 0x1ffff X^16+X^15+X^14+X^13+X^12+X^11+X^10+X^9+X^8+X^7+X^6+X^5+X^4+X^3+X^2+X+1
PRODUCT 0x20001 X^17+1
IRREDUCIBILITY factor8a tested=30 irreducible=True divisors=[]
IRREDUCIBILITY factor8b tested=30 irreducible=True divisors=[]
IRREDUCIBILITY false_X8_plus_1 tested=30 irreducible=False divisors=[3, 5, 15, 17]
NEGATIVE_CONTROL X^8+1 is irreducible: EXPECTED ASSERTION FAILURE
FALSE_FACTOR_WITNESS (X+1)^8 = X^8+1
IRREDUCIBILITY archived_modulus tested=510 irreducible=True divisors=[]
ARCHIVED_ORDER 17
ARCHIVED_MINPOLY 0x20001 X^17+1
GF2_ORDER 1
GF2_MINPOLY 0x3 X+1
NEGATIVE_CONTROL GF(2) Frobenius has order 17: EXPECTED ASSERTION FAILURE
NEGATIVE_CONTROL GF(2) Frobenius has minimal polynomial X^17+1: EXPECTED ASSERTION FAILURE
GF2_TARGET_POLYNOMIAL_ANNIHILATES True; MINIMALITY_FALSE
ALL_REQUIRED_EXACT_CHECKS_PASSED True
```

Only the reviewer's own `results.json` and `raw_output.txt` were read to inspect
these results. Python metadata was written to `runtime.json` using `sys.version`,
`sys.executable`, `sys.platform`, and `os.uname()`. It reports CPython 3.9.25,
Linux x86_64, and no third-party dependencies. The clock tool reported
`2026-10-27 22:25:50 UTC` during report preparation.

## Seal and release

Artifact SHA-256 values are recorded in `review_attestation.yaml` and
`seal.sha256`. The seal is computed after the report and attestation are written.
The operational release command is:

```bash
/home/ec2-user/.local/bin/conductor task release T-617 -note 'Blind J2 sealed: factors irreducible; canonical Frobenius order 17 and minpoly X^17+1; exact controls reject; report and attestation in TASK-20261027-b17d02.'
```

The release output is saved separately in `release_output.txt` after sealing;
it does not modify the sealed scientific artifacts. Its success is reported to
the coordinator directly.
