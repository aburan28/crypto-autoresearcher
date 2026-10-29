# Submission preparation, 2026-10-29 UTC

Owner request: publish the certificate bytes, expand the named-instance coverage
through n=45 and explore n=47..51, reconcile definitions and full primary
literature, and prepare an external expert review before ePrint/journal submission.
Conductor task: T-778. This is preparation, not submission or scientific promotion.

The owner's subsequent instruction defers external human review and prioritizes
the data. The active work is certificate retention/publication and the frozen
190-input panel. The manuscript, secondary PKM replication and Nagao note have
not been completed by this data campaign.

## Public data and reproduction

The additive public archive is the
[certificate release](https://github.com/isogeny-labs/crypto-autoresearcher/releases/tag/semaev-closure-certificates-20261029).
Each completed publication has four assets: `ID.D4.cert.gz`,
`ID.receipt.json`, `ID.evidence.tar.gz`, and `ID.publication.json`.
The receipt carries the exact field, curve, subspace, target, original
certificate digest and independent checker output. The evidence archive carries
the original attempt records and logs. Fresh-input evidence additionally carries
the exhaustive count and inference record. The publication acknowledgement
records anonymous HTTPS and canonical S3 download/hash checks. Files not yet
listed in the release are not claimed to be published.

The certificate header contains its degree. For example, after downloading
T33a's certificate and receipt, run this from the dossier's parent repository:

```sh
gunzip -k T33a.D4.cert.gz
python3 - T33a.receipt.json T33a.D4.cert <<'PY'
import hashlib, json, subprocess, sys
receipt = json.load(open(sys.argv[1]))
result = receipt['result']
assert hashlib.sha256(open(sys.argv[2], 'rb').read()).hexdigest() == result['certificate_sha256']
item = result['parameters']; r = item['record']
argv = [sys.executable, 'analysis/semaev-m2-last-fall-degree/verify/cert_check.py']
if item.get('chain'): argv.append('--t3')
argv += [sys.argv[2], str(r['n']), r['modulus_hex'], str(r['a2']), r['a6_hex'], r['z_hex'], *r['V_basis_hex']]
subprocess.run(argv, check=True)
PY
```

The checker uses the Python standard library. Rebuilding the producer requires
M4RI. This run used release-20240729 at
`d0a1ee18511714a2c33cc0920a068c05c1f0f8fb`, with its 15 tests passing.
The same release also hosts `runtime-source.tar.gz`, an exact Git archive of
the frozen execution source at `fdd9cb0b730b3f18ab64d745bd32aa57e4cd1103`,
and `runtime-binaries.tar.gz`. The latter preserves the native x86_64
executables used in this campaign; `runtime-provenance.json` records their
hashes, compiler and host architecture. Source is provided for rebuilding on
other platforms. See `runtime/publication.json` for download/readback hashes.
The native counter can be built on x86 with CLMUL/SSE4.1 as follows:

```sh
gcc -O3 -mpclmul -msse4.1 -Wall -Wextra -Werror count_by_sum.c -o count_by_sum
SEMAEV_COUNT_BIN=/absolute/path/count_by_sum \
SEMAEV_REFERENCE_COUNT_BIN=/absolute/path/s3count2 \
python3 -m unittest test_data_tools.py
```

`certificate_campaign.py` retains completed files and separate attempts;
`expand_instances.py` uses the frozen seeds, retains every outcome, and joins
checked codimension bounds with exact counts. `publish_certificates.py`
publishes only completed, hash-consistent evidence and never replaces a release
asset. `collect_progress.py` writes a fresh snapshot with pending cells explicit.
The active campaign commands, ownership and recovery caveats are in the S3
resume checkpoint. See `operational-deviations.md` for the checkpoint-gate
omission and unified-export limitation; neither is concealed by a passing test.

## Reconciliation before execution

The original checkout was at 2026-10-18. This work uses a separate sparse
worktree of current origin/main. The lab overview and local process inspection
found no active Semaev certificate producer. Historical certificates.txt lists
13 certificates. The legacy cert_batch.py deletes certificate files after
checking; new work must retain bytes and never overwrite earlier attempts.
HEAD of the canonical store object for T33a returned 404 on 2026-10-29.
This is evidence about that key only, not a search of every archive.

## Literature and claim boundary before implementation

Read the original theorem dossier, certificate producer/checker, the
2026-10-19 dimension correction, and
`problems/semaev-degree-two-fall-nonzero-bridge.md` at current main.
Read Kousidis--Wiemers in full at https://arxiv.org/html/1906.05594
(PDF https://arxiv.org/pdf/1906.05594, v1). Definitions 2.1--2.2 use a
span/top-form convention. Remark 3.3 attributes the m=2 value 2 to
Kosters--Yeo. Table 1 averages ten trials and already reports degree 5 at
n=37..48; section 4 also reports the polynomial-subspace transition at 45.
This work cannot claim first discovery of either observation. Their question
(4.1) concerns degree of regularity, not an interchangeable definition of LFD.

HKY 2015 full-text retrieval from both ePrint 2015/573 and the official IACR
archive returned HTTP 403. The accessible expanded paper
https://arxiv.org/pdf/1505.02532 is a different four-author publication;
reading it must not be represented as reading the blocked three-author paper.
Further primary-source retrieval remains required.

The dossier's Corollary 2.2 assumes all listed equations have degree exactly
two. Its nonzero-fall version additionally assumes ell_0 != 0. The later
finite review concerns a closure-filtration convention and is a mandatory
definition control, not automatic refutation of every other convention.
Upper bounds k+2 and (t-1)k+t are for unsatisfiable inputs. T33a/T33b use
trace-zero subspaces. A certificate proves W_D contained in ker(pi), hence
codim(W_D) >= nq, not equality. Nonmembership of 1 alone needs an independent
unsatisfiability argument to imply a last-fall lower bound.

Crypto PR #2795 merged at cca7d4fe08d49f6e63b8e8f37883eb1d181eb194.
Its prime-field (4,5) theorem assumes the inverse-guarded three-abscissa
presentation, rational lifts and an affine rational target. The binary
coefficient-field analogue has LFD 4 for split cube orbits, 5 otherwise.
Neither is the fully Boolean system's general degree-five ceiling.

## Work remaining and acceptance

1. Retain all 13 historical certificates, compare historical hashes, run the
   independent checker, archive by content hash, download and hash again.
   Private S3 custody is not anonymous public archive publication.
2. Freeze a sampling protocol before new draws: ten fresh instances at each
   integer n=33..45 and 47..51, with five polynomial and five random subspaces
   per n, plus a separately labelled trace-zero n=33 stratum. Preserve all
   outcomes. Report exact solution counts and certificates, not solver grades.
3. Degree-five closure is necessary to certify a lower bound of six. Apply
   prospective memory admission; an inadmissible matrix stays uncomputed.
4. Reconcile first-fall definitions, state hypotheses next to every theorem,
   and have an independent specialist inspect the proof packet. An AI review
   does not complete the requested external human review.
5. Prepare an anonymized manuscript and reviewer packet under papers/.
   The title must not imply unbounded LFD growth.
6. Preserve the PKM replication and Nagao note as secondary tracks. The
   not-recommended candidates are not new experiment authorizations.

No asymptotic growth, ECDLP attack-cost, timing advantage, submission, public
DOI, human review, or complete Lean formalization is claimed here.
