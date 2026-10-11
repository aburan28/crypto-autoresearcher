# MeaningHash — experimental verifiable semantic fingerprint

Dependency-free Python prototype. Generates deterministic 256-bit weighted-feature SimHash, conservative rule-based canonical propositions, SHA-256 commitments, verification witnesses, ordered Merkle roots, and an 8-band SQLite candidate index.

```bash
cd research/meaninghash
python meaninghash.py hash 'GPU faster than CPU'
python meaninghash.py --db research.db add 'GPU faster than CPU'
python meaninghash.py --db research.db query 'GPU is faster than CPU'
python -m unittest discover -v
```

**Safety:** Not a trained semantic encoder. Canonicalization only recognizes a few English patterns. An accepted witness verifies equality under the limited parser, NOT natural-language equivalence or entailment. Do not authorize automatic research-result reuse with this prototype.

**Performance:** 256-bit codes require 32 raw bytes; SQLite rows and indexes cost more. Hashing is Python-level and not SIMD-optimized. The eight-band index is approximate and may miss close candidates; use `full_scan=True` for exact top-k. Benchmarks, adversarial accuracy validation, native implementation, and encoder training remain future work.
