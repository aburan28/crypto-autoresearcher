# EXP-CERTBIN-e94b27 certificate verifier

`verify_cert.py` checks the unsatisfiability certificates of RUN-CERTBIN-c417e0
(controls C-CERT and C-VERIFIER). It is run as a separate process after all
closures:

```sh
python3 experiments/EXP-CERTBIN-e94b27/verifier/verify_cert.py \
  --certs experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/certificates.jsonl.gz \
  --source-run experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05 \
  --out experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/certificate-verification.json
```

Independence: imports only the standard library and numpy; nothing from
`impl/` or from `EXP-CERTBIN-4e92d7/impl/`. It reads instance data directly
from the archived source run (curve.json, targets-F-S3/F-AFF-1 for x_R,
p1-instances.json.gz for the null coefficients) and rebuilds f_0..f_16 itself:
for F-S3 by evaluating S_3(x_1, x_2, x_R) at all 2^18 Boolean points with its
own vectorised schoolbook F_{2^17} arithmetic and taking the algebraic normal
form of each coordinate (Moebius transform); for F-AFF-1 as A0 XOR (XOR of Aj
over the bits of r); for F-NULLF2 from E_hex. From `instance-sets.json` next to
the certificates it reads only which (family, idx) are curve-algebra instances
and the engine's E_hex, to report construction agreement (C-VERIFIER).

A certificate (list of pairs [mu, k]) is accepted iff it is well formed, has
no repeated pair, and sum mu*f_k in B = F_2[v_0..v_17]/(v_i^2 + v_i) is
exactly the constant 1.

The same executor wrote this verifier and the closure engine: the
independence is code-level, not author-level (EX-10). The author-independent
verification is the review round's.
