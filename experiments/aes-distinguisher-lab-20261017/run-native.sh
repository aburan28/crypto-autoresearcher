#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 3 ]; then
  echo 'usage: bash run-native.sh ENGINE-REPO AES-DISCOVER-BINARY NEW-OUTPUT-DIRECTORY' >&2
  exit 2
fi
engine=$(realpath -- "$1")
binary=$(realpath -- "$2")
output=$(realpath -m -- "$3")
card="$engine/experiments/aes-distinguisher-lab-20261017/run.sh"
test -f "$card"
test -x "$binary"
test ! -e "$output"
exec bash "$card" "$binary" "$output"
