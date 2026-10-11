# Research Vault: Mac-rooted encryption implementation contract

Status: DESIGN ONLY. No existing repository data is encrypted by this change.

## Threat model
Protect unpublished research from Git hosting compromise, stolen cloud backups, leaked object stores and unauthorized remote agents. Does not protect data already committed in plaintext, captured by malicious agent prompts, displayed to remote model providers, or read from an unlocked/compromised endpoint.

## Architecture
- macOS companion service uses CryptoKit SecureEnclave.P256.KeyAgreement.PrivateKey and Keychain; hardware private key never exported. Secure Enclave supports P-256 key agreement, **not** arbitrary symmetric bulk encryption.
- Generate random 256-bit per-project data encryption keys (DEKs); wrap DEKs to Secure Enclave recipient via authenticated ECDH+HKDF envelope; encrypt objects with AES-256-GCM and unique random 96-bit nonces, binding project ID, object ID, version and classification as authenticated associated data. Use a vetted envelope library and versioned formats; never invent crypto primitives.
- Encrypted artifacts live in content-addressed object storage; store ciphertext, versioned envelope metadata, and hashes. Keep public source code distinct from classified-by-owner research data. Git history, filenames, commit messages and sizes can leak metadata; evaluate git-crypt/sops/age for selected files, but prefer an encrypted artifact vault outside Git for bulk datasets.
- Decryption broker runs on Mac, authorizes a scoped lease per agent/task/object, logs each request, limits expiry and output volume. Agents receive plaintext only within a restricted execution environment; never place master keys in environment variables, prompts, GitHub Actions, CI, or cloud workers.
- Remote workers need an explicit trust decision: client-side decrypt and provision a task-specific secret to an attested trusted worker, or keep decryption local. Never describe an ordinary cloud worker as zero-knowledge.
- Recovery: create and offline-test a separate recovery recipient before migrating any data. Secure Enclave keys are device-bound; losing the Mac without recovery otherwise loses data.
- Rotation: rotate DEKs per project, revoke agent leases, rewrap or re-encrypt as needed. Revocation does not erase already disclosed plaintext.

## Migration phases
1. Inventory repository and history, LFS, issues, actions, logs, artifacts, S3, database snapshots, and agent transcripts. Mark sensitivity and leakage paths. No destructive edits.
2. Build Mac key manager + test vectors; prove encrypt/decrypt, wrong-key, tamper, nonce uniqueness, restart, and offline recovery behavior.
3. Build artifact encrypt/decrypt CLI, atomic writes, dry-run, immutable manifest and round-trip verification. Fail closed on decryption errors.
4. Add authorization broker, audit logs, per-agent scopes, and CI tests with ephemeral test keys.
5. Migrate **copies** of selected datasets, verify, then explicitly approve cutover. Existing Git plaintext history and forks require separate remediation; deleting files in a later commit does not erase history.
6. Document model-provider data boundaries and prompt redaction. Client-side encryption at rest cannot prevent plaintext sent to an AI API.

## Required acceptance criteria
- Hardware-backed key never exportable; independent recovery works on another machine.
- No secrets or plaintext in commits, CI logs, temporary files, crash reports, or prompts in integration tests.
- Tampered ciphertext fails authentication; metadata substitution fails.
- Every access is authorized, scoped, time-limited and logged.
- Full restore from encrypted backups demonstrated before production cutover.
- Rollout cannot silently encrypt existing data or delete originals.
