# RUN-MLKEM-015-001 summary

Pinned lattice-estimator `3e48ef421ec256afddb3e7d2249a77eab6e9ba12`

| scheme | NIST | primal_bdd MATZOV | dual_fft MATZOV | best | margin vs NIST | Carrier claim | MATZOV22 claim | coreSVP primal ADPS16 | Kyber.py primal |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|
| Kyber512 | 143 | 140.20 | 143.79 | primal_bdd/MATZOV | 2.80 | 139.5 | 137.5 | 118.55 | 118 |
| Kyber768 | 207 | 200.96 | 203.79 | primal_bdd/MATZOV | 6.04 | 195.1 | 193.5 | 182.21 | 183 |
| Kyber1024 | 272 | 270.72 | 273.82 | primal_bdd/MATZOV | 1.28 | 259.7 | 257.8 | 255.21 | 256 |

## Key findings
- Under RC.MATZOV, the cheapest attack among {primal_usvp, primal_bdd, dual_hybrid±fft} is primal_bdd for all three Kyber sets.
- dual_hybrid+fft under MATZOV does not beat primal_bdd (gaps +3.6/+2.8/+3.1 bits).
- Carrier (KN-LIT-7617) claimed dual costs are 4.3/8.7/14.1 bits below our dual_hybrid+fft MATZOV estimates — not reproduced by lattice-estimator matzov dual.
- MATZOV 2022 claimed dual costs are 6.3/10.3/16.0 bits below our dual_hybrid+fft MATZOV estimates.
- Nonetheless primal_bdd under MATZOV sits 2.8/6.0/1.3 bits below NIST classical cutoffs 143/207/272.
- ADPS16/core-SVP primal reproduces pq-crystals Kyber.py classical column within ~0.5–1 bit (118.6 vs 118; 182.2 vs 183; 255.2 vs 256).
