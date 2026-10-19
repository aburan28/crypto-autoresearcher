#!/bin/sh
# Receipt orchestration only. All mathematical work uses frozen native binaries.
set -u
mode=$1
run_dir=$2
binary=/Volumes/SSD990-2/crypto/isogeny-degree-challenge-builds-20261015/release-publication/pr1940/installed-pr1940/isogeny
controls=/Volumes/SSD990-2/crypto/isogeny-degree-challenge-builds-20261015/cli/release/deps/challenge_cli-5eec4db822083ae4
if [ "$mode" = check ]; then
  test -s "$run_dir/manifest.yaml" && test -s "$run_dir/raw-result.json" || exit 1
  if [ -f "$run_dir/native/entry.json" ]; then
    cmp "$run_dir/native/entry.json" "$run_dir/raw-result.json" || exit 1
  else
    test -s "$run_dir/control-passed" || exit 1
  fi
  exit 0
fi
case "$mode" in control|candidate) ;; *) exit 64 ;; esac
# Refuse replacing or repeating a run. The caller creates the run directory.
test ! -e "$run_dir/manifest.yaml" && test ! -e "$run_dir/native" && test ! -e "$run_dir/controls" || exit 73
binary_hash=$(shasum -a 256 "$binary") || exit 74
case "$binary_hash" in 8e0ab524008d41098a816d117d563bbefa456959bb790a78e41efc41b05e6cc1' '*) ;; *) exit 74 ;; esac
if [ "$mode" = control ]; then
  controls_hash=$(shasum -a 256 "$controls") || exit 74
  case "$controls_hash" in ccf19b8fdb15fb055059f9e2db7412a11d44fa526b080ae09462dc659debb527' '*) ;; *) exit 74 ;; esac
  ISOGENY_CHALLENGE_BINARY="$binary" ISOGENY_CHALLENGE_EVIDENCE="$run_dir/controls" "$controls" --exact native_challenge_replays_maps_rejects_forgery_and_ranks_curves_separately --nocapture > "$run_dir/native.stdout.log" 2> "$run_dir/native.stderr.log"
  native_exit=$?
  printf '{"control_exit_code":%s,"native_test":"native_challenge_replays_maps_rejects_forgery_and_ranks_curves_separately","scientific_promotion":false}\n' "$native_exit" > "$run_dir/raw-result.json"
  if [ "$native_exit" -eq 0 ]; then printf 'Native positive and nine rejection controls completed.\n' > "$run_dir/control-passed"; fi
else
  "$binary" challenge run --curve p192 --ell 50341 --out "$run_dir/native" > "$run_dir/native.stdout.log" 2> "$run_dir/native.stderr.log"
  native_exit=$?
  if [ -f "$run_dir/native/entry.json" ]; then cp "$run_dir/native/entry.json" "$run_dir/raw-result.json"; else printf '{"native_exit_code":%s,"status":"INCOMPLETE","score":null}\n' "$native_exit" > "$run_dir/raw-result.json"; fi
fi
printf 'receipt_kind: native_command_observation\nmode: %s\nnative_exit_code: %s\nbinary_sha256: 8e0ab524008d41098a816d117d563bbefa456959bb790a78e41efc41b05e6cc1\nscientific_promotion: false\n' "$mode" "$native_exit" > "$run_dir/manifest.yaml"
# A censored native entry is a complete observation, never a negative theorem.
if [ "$mode" = candidate ] && [ -f "$run_dir/native/entry.json" ]; then exit 0; fi
exit "$native_exit"
