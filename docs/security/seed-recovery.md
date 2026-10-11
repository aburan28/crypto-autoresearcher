# Seed-based vault recovery contract

Status: design only; no live keys generated and no existing data encrypted.

## Intended behavior
- On first initialization, generate 256 bits of entropy using the operating system CSPRNG **on the owner's Mac**. Optionally encode as a 24-word BIP-39 mnemonic with checksum; this is an encoding, not additional entropy.
- Derive a recovery wrapping key from the decoded entropy with HKDF-SHA-256 using a random stored salt and explicit versioned domain separator `crypto-autoresearcher/vault-recovery/v1`. A separate optional user passphrase can be mixed with Argon2id, with documented memory/time settings; do not imply Argon2id adds entropy to a randomly generated seed.
- Generate independent random project data-encryption keys. Wrap each under a recovery key using vetted AEAD; independently wrap for the Mac Secure Enclave public recipient. Never reuse a nonce with the same key.
- Use authenticated encryption for every object; include object identity, project identity, format version, and content type in associated data. Reject substitution, corruption and rollback according to an authenticated manifest policy.
- Daily unlock: Keychain and Secure Enclave, optional user-presence requirement. Disaster recovery: mnemonic entered **locally** on trusted replacement machine, verify recovery against a fixture, then enroll a new device recipient.
- Never submit mnemonic or plaintext keys to Git, CI, model APIs, telemetry, or remote workers. Agents receive short-lived task-scoped access via broker. Offline Mac means no decryption unless a separately approved trusted remote recipient exists.
- Offer an optional advanced mode for externally supplied uniformly random secret bytes, validated for length/format, but warn against user-chosen phrases and low-entropy passwords.
- True one-time pad mode is deliberately **not** the default: it requires an independent uniformly random pad at least as long as each plaintext, no pad reuse, and secure pad distribution/storage. It is unsuitable for continuously updated repository artifacts.

## Required tests
1. Deterministic mnemonic encoding/decoding fixtures and checksum rejection.
2. Recovery on second device from only mnemonic plus encrypted backup metadata.
3. Wrong seed, wrong passphrase, modified ciphertext and swapped object metadata all fail authentication.
4. Rotating a project key does not invalidate offline recovery.
5. Test accidental plaintext leakage in logs, manifests and temporary paths.
6. Never delete plaintext originals before a separately approved migration and verified recovery.
