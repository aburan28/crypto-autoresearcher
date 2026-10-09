#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
swiftc Vault.swift -o /tmp/crypto-research-vault-test-$$
BIN=/tmp/crypto-research-vault-test-$$
ROOT=$(mktemp -d)
trap 'rm -rf "$ROOT" "$BIN"' EXIT
"$BIN" init "$ROOT/vault"
printf 'known plaintext\n' > "$ROOT/plain"
"$BIN" encrypt "$ROOT/vault" "$ROOT/plain" "$ROOT/encrypted"
"$BIN" decrypt "$ROOT/vault" "$ROOT/encrypted" "$ROOT/device"
cmp "$ROOT/plain" "$ROOT/device"
"$BIN" recover "$ROOT/vault" "$ROOT/encrypted" "$ROOT/recovered"
cmp "$ROOT/plain" "$ROOT/recovered"
if "$BIN" encrypt "$ROOT/vault" "$ROOT/plain" "$ROOT/encrypted"; then echo 'overwrite allowed' >&2; exit 1; fi
printf '00%.0s' {1..32} > "$ROOT/vault/recovery.hex"
if "$BIN" recover "$ROOT/vault" "$ROOT/encrypted" "$ROOT/bad"; then echo 'wrong recovery succeeded' >&2; exit 1; fi
test ! -e "$ROOT/bad"
echo 'Round-trip, recovery, overwrite and wrong-secret checks passed'
