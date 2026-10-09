# Research vault CLI — experimental macOS implementation

**Security status: prototype, NOT production ready.** Requires macOS with Secure Enclave and Swift CryptoKit. Not built or executed in CI in this PR.

Build: `swiftc tools/research_vault/Vault.swift -o vault`.

Commands:
```
./vault init /path/to/private-vault
./vault encrypt /path/to/private-vault input.txt input.vault
./vault decrypt /path/to/private-vault input.vault restored.txt
./vault recover /path/to/private-vault input.vault restored-by-seed.txt
bash tools/research_vault/test.sh
```

The generated recovery secret is **64 hexadecimal characters**, not a 24-word mnemonic. This is a temporary interface; do not call it BIP-39. The implementation uses CryptoKit Secure Enclave P-256 ECDH, HKDF-SHA256, and AES-GCM with independent random per-file keys and separate device/recovery key wraps.

**Important limitations:**
- `init` creates `recovery.hex` inside the vault directory; this is a serious operational exposure. Keep the directory private and OFFLINE, and do not use this prototype with sensitive research. Encrypt currently needs the recovery secret present, so simply moving it away prevents subsequent encryption. A production implementation must instead provision a persistent device-unlocked recovery wrapping key, and make recovery secret input a local interactive, one-time operation.
- No user-presence/Touch ID policy, device attestation, Keychain integration, mnemonic encoding, key rotation, streaming, symlink protection, rollback protection, or agent authorization broker yet.
- No directory-wide or Git-history encryption. Existing plaintext copies remain accessible.
- No formal audit. Test on disposable data only. Secure Enclave functionality cannot be verified on a Linux CI host.

Next gate: implement proper local Keychain access-control and offline recovery enrollment, stream large files, add authenticated manifests, execute hardware-backed tests on a real Mac, and independently review before handling sensitive data.
