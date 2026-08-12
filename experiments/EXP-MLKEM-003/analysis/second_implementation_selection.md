# Second implementation selection (EXP-MLKEM-003)

- **Chosen:** liboqs
- **Repository:** https://github.com/open-quantum-safe/liboqs
- **Tag:** 0.12.0
- **Resolved commit:** `f4b96220e4bd208895172acc4fedb5a191d9f5b1`
- **Reason:** First preference in frozen order; built offline within build_select_and_anchor budget; both ciphertext verify symbols and OQS_KEM_decaps reachable.

## Preference order outcomes

1. **liboqs** — selected (built successfully).
2. **PQClean** — not attempted; higher-preference candidate succeeded.
3. **BoringSSL** — not attempted; higher-preference candidate succeeded.
4. **pq-crystals reference** — not attempted; higher-preference candidate succeeded.

No higher-preference candidate was rejected for build failure; liboqs was first and available.
