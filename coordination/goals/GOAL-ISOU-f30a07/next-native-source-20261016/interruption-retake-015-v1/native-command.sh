#!/bin/sh
# Thin launcher for one existing pure-logging unit test per arm. No mathematics.
set -eu
export LC_ALL=C
out=$1
case "$out" in /*) ;; *) echo 'absolute fresh output required' >&2; exit 64;; esac
[ ! -e "$out" ] || exit 65
mkdir "$out"
exe='/Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/clean-retake-v1/reference/target/release/deps/isogeny-8734bd11e3dad22d'
expected='bf48ea22df2d8e1c2b94f1462cde3d1c4f64737d4cf6d3bca4623d5b4bef0a9c'
actual=$(/usr/bin/shasum -a 256 "$exe")
[ "${actual%% *}" = "$expected" ] || exit 66
armout="$out/reference"
mkdir "$armout"
printf '%s\n' "$actual" > "$armout/executable-before.sha256"
printf '%s\n' '015fa7bb504ef63953e0e04e464bb266f4f207bf' > "$armout/source-commit.txt"
printf '%s\n' '--no-default-features' > "$armout/build-features.txt"
printf '%s\n' 'ISOGENY_TRACE_UNIT_EVIDENCE='"$armout/retained" > "$armout/environment.txt"
printf '%s\n' "$exe --exact replay_trace::tests::flushed_begin_survives_bounded_child_interruption --nocapture --test-threads=1" > "$armout/native-argv.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$armout/started-at.txt"
set +e
/opt/homebrew/bin/gtimeout --kill-after=5s 20s /usr/bin/time -l -o "$armout/os-time.txt" /usr/bin/env -u ISOGENY_TRACE_CONTROL_CHILD -u ISOGENY_REPLAY_TRACE ISOGENY_TRACE_UNIT_EVIDENCE="$armout/retained" "$exe" --exact replay_trace::tests::flushed_begin_survives_bounded_child_interruption --nocapture --test-threads=1 > "$armout/parent.stdout.log" 2> "$armout/parent.stderr.log"
code=$?
set -e
printf '%s\n' "$code" > "$armout/exit-code.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$armout/finished-at.txt"
/usr/bin/shasum -a 256 "$exe" > "$armout/executable-after.sha256"
cmp "$armout/executable-before.sha256" "$armout/executable-after.sha256" || exit 67
[ "$code" -eq 0 ] || exit "$code"
exe='/Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/clean-retake-v1/candidate/target/release/deps/isogeny-091b88e44789ba98'
expected='cdb325a657f6da2d77bb4be8d8084b4d25f3552ba891bb622bf3fdff4e4f457e'
actual=$(/usr/bin/shasum -a 256 "$exe")
[ "${actual%% *}" = "$expected" ] || exit 66
armout="$out/candidate"
mkdir "$armout"
printf '%s\n' "$actual" > "$armout/executable-before.sha256"
printf '%s\n' '015fa7bb504ef63953e0e04e464bb266f4f207bf' > "$armout/source-commit.txt"
printf '%s\n' '--no-default-features --features cached-fixed-modulus-reduction' > "$armout/build-features.txt"
printf '%s\n' 'ISOGENY_TRACE_UNIT_EVIDENCE='"$armout/retained" > "$armout/environment.txt"
printf '%s\n' "$exe --exact replay_trace::tests::flushed_begin_survives_bounded_child_interruption --nocapture --test-threads=1" > "$armout/native-argv.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$armout/started-at.txt"
set +e
/opt/homebrew/bin/gtimeout --kill-after=5s 20s /usr/bin/time -l -o "$armout/os-time.txt" /usr/bin/env -u ISOGENY_TRACE_CONTROL_CHILD -u ISOGENY_REPLAY_TRACE ISOGENY_TRACE_UNIT_EVIDENCE="$armout/retained" "$exe" --exact replay_trace::tests::flushed_begin_survives_bounded_child_interruption --nocapture --test-threads=1 > "$armout/parent.stdout.log" 2> "$armout/parent.stderr.log"
code=$?
set -e
printf '%s\n' "$code" > "$armout/exit-code.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$armout/finished-at.txt"
/usr/bin/shasum -a 256 "$exe" > "$armout/executable-after.sha256"
cmp "$armout/executable-before.sha256" "$armout/executable-after.sha256" || exit 67
[ "$code" -eq 0 ] || exit "$code"
exit 0
