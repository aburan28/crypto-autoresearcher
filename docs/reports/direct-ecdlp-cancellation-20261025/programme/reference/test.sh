#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
validation_tmp=$(mktemp -d "${TMPDIR:-/tmp}/tagged-reference.XXXXXXXX")
trap 'rm -rf "$validation_tmp"' EXIT
validation_flags=(-std=c++20 -Wall -Wextra -Wconversion -Wsign-conversion -Wpedantic -Werror)
case "${1:-normal}" in
  normal) validation_flags+=(-O2) ;;
  ubsan) validation_flags+=(-O1 -g -fno-omit-frame-pointer -fsanitize=undefined) ;;
  asan-ubsan) validation_flags+=(-O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined) ;;
  *) echo 'usage: test.sh [normal|ubsan|asan-ubsan]' >&2; exit 2 ;;
esac
g++ "${validation_flags[@]}" tagged_reference.cpp -o "$validation_tmp/tagged-reference"
"$validation_tmp/tagged-reference" --self-test
