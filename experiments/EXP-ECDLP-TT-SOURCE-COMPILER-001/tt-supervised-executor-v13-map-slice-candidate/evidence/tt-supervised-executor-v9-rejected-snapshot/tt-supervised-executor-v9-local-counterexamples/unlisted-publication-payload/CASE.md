# Unlisted Publication Payload

The independent Red Team added a payload originally named
`._UNLISTED-PAYLOAD`. It is preserved here as `UNLISTED-PAYLOAD.bin` so routine
AppleDouble cleanup cannot delete the evidence.

The original top manifest remained byte-identical:

```text
b5426daa7d9ebf66db356ae2080780712e8318f03bec04c37d12b45580bd2b1c  SHA256SUMS
```

All listed members still passed and the unchanged verifier retained its original
PASS receipt. V9 checks listed-member integrity but not directory closure.
