#!/bin/sh
# Use the locally built Sage, with all runtime caches in this research scope.
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
sage_root=/Volumes/SSD990/cryptanalysis/third_party/sage-binary
mkdir -p "$here/scratch/sage" "$here/scratch/tmp"
export DOT_SAGE="$here/scratch/sage"
export TMPDIR="$here/scratch/tmp"
export PATH="$sage_root/local/bin:/opt/homebrew/bin:$PATH"
script=evaluate_candidates.py
if [ "${1:-}" = "--script" ]; then
    shift
    script=${1:?missing script name}
    shift
    case "$script" in
        evaluate_candidates.py|evaluate_family_fast.py|evaluate_x9_remaining.py|check_x9_evaluator_controls.py|certify_prime_orders.py|certify_p192_skips.py|certify_binary_orders.py|certify_all_binary_skips.py|certify_family_prefix.py|certify_full_prime_census.py|certify_all_prime_survivors.py|screen_prime_2torsion.py|screen_prime_3torsion.py) ;;
        *) echo "unsupported script: $script" >&2; exit 2 ;;
    esac
fi
exec "$sage_root/sage" -python "$here/$script" "$@"
