#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
arch=${ARCH_OVERRIDE:-$(uname -m 2>/dev/null || echo unknown)}
tmp_root_rel=.qruov-ci-$$
tmp_root=$repo_dir/$tmp_root_rel
tmp_nist_dir_rel=$tmp_root_rel/nist
tmp_nist_dir=$repo_dir/$tmp_nist_dir_rel
kat_ref_file=$repo_dir/test/KAT_SHA256SUMS.txt
param_choices="1q127L3 1q127L10 1q31L3 1q31L10 1q7L10"
param_choices="$param_choices 3q127L3 3q127L10 3q31L3 3q31L10 3q7L10"
param_choices="$param_choices 5q127L3 5q127L10 5q31L3 5q31L10 5q7L10"
prg_choices="aes shake"

trap 'rm -rf "$tmp_root"' EXIT

pick_make_cmd()
{
    if [ -n "${MAKE:-}" ]; then
        printf '%s\n' "$MAKE"
    elif command -v gmake >/dev/null 2>&1; then
        printf '%s\n' "gmake"
    else
        printf '%s\n' "make"
    fi
}

make_cmd=$(pick_make_cmd)

log_run()
{
    echo "==> $*"
    "$@"
}

usage()
{
    echo "usage: $0 [CI|RELEASE]" >&2
    exit 2
}

if [ "$#" -ne 1 ]; then
    usage
fi

mode=$1

have_x86_64()
{
    case "$arch" in
        x86_64|amd64) return 0 ;;
        *) return 1 ;;
    esac
}

have_valgrind()
{
    command -v valgrind >/dev/null 2>&1
}

run_test_case()
{
    impl=$1
    param=$2
    prg=$3
    build_dir=$tmp_root_rel/test/$impl/$param-$prg
    log_run "$make_cmd" BUILD_DIR="$build_dir" IMPL="$impl" PARAM="$param" PRG="$prg" test
}

run_test_sweep()
{
    impl=$1
    for prg in $prg_choices; do
        for param in $param_choices; do
            run_test_case "$impl" "$param" "$prg"
        done
    done
}

run_valgrind_case()
{
    impl=$1
    param=$2
    prg=$3
    build_dir=$tmp_root_rel/valgrind/$impl/$param-$prg
    log_run "$make_cmd" BUILD_DIR="$build_dir" IMPL="$impl" PARAM="$param" PRG="$prg" valgrind
}

sha256_cmd()
{
    if command -v sha256sum >/dev/null 2>&1; then
        printf '%s\n' "sha256sum"
    elif command -v shasum >/dev/null 2>&1; then
        printf '%s\n' "shasum -a 256"
    else
        echo "sha256sum/shasum not found" >&2
        exit 1
    fi
}

sha256_file()
{
    file=$1
    cmd=$(sha256_cmd)
    # shellcheck disable=SC2086
    set -- $cmd "$file"
    "$@" | awk '{print $1}'
}

run_check_kat_case()
{
    impl=$1
    param=$2
    prg=$3
    build_dir=$tmp_root_rel/check-kat/$impl/$param-$prg
    echo "==> check-kat IMPL=$impl PARAM=$param PRG=$prg"
    "$make_cmd" -B BUILD_DIR="$build_dir" IMPL="$impl" PARAM="$param" PRG="$prg" kat >/dev/null

    rsp=$(kat_rsp_file "$repo_dir/$build_dir")
    rsp_name=$(basename "$rsp")
    got_hash=$(sha256_file "$rsp")
    want_hash=$(awk '$2 == "'"$param-$prg/$rsp_name"'" { print $1 }' "$kat_ref_file")

    if [ -z "$want_hash" ] || [ "$got_hash" != "$want_hash" ]; then
        echo "KAT hash mismatch: IMPL=$impl PARAM=$param PRG=$prg" >&2
        exit 1
    fi
}

nist_leaf_dir()
{
    impl=$1
    case "$impl" in
        ref) printf '%s\n' "$tmp_nist_dir/Reference_Implementation/ref" ;;
        opt) printf '%s\n' "$tmp_nist_dir/Optimized_Implementation/opt" ;;
        avx2) printf '%s\n' "$tmp_nist_dir/Optimized_Implementation/avx2" ;;
        *)
            echo "unsupported impl: $impl" >&2
            exit 1
            ;;
    esac
}

kat_rsp_file()
{
    kat_dir=$1
    set -- "$kat_dir"/PQCsignKAT_*.rsp
    if [ "$#" -ne 1 ] || [ ! -f "$1" ]; then
        echo "expected exactly one KAT response file in $kat_dir" >&2
        exit 1
    fi
    printf '%s\n' "$1"
}

generate_nist_tree()
{
    rm -rf "$tmp_nist_dir"
    log_run "$make_cmd" NIST_SUBMISSION_DIR="$tmp_nist_dir_rel" generate-nist-submission
}

run_nist_kat_case()
{
    impl=$1
    param=$2
    prg=$3
    top_build_dir_rel=$tmp_root_rel/nist-top/$impl/$param-$prg
    top_build_dir=$repo_dir/$top_build_dir_rel
    leaf_dir=$(nist_leaf_dir "$impl")
    leaf_build_dir=$tmp_root/nist-leaf/$impl/$param-$prg

    echo "==> nist-kat IMPL=$impl PARAM=$param PRG=$prg"
    "$make_cmd" -B BUILD_DIR="$top_build_dir_rel" IMPL="$impl" PARAM="$param" PRG="$prg" kat >/dev/null
    "$make_cmd" -C "$leaf_dir" BUILD_DIR="$leaf_build_dir" PARAM="$param" PRG="$prg" >/dev/null
    (cd "$leaf_build_dir" && ./PQCgenKAT_sign >/dev/null)

    cmp -s "$(kat_rsp_file "$top_build_dir")" "$(kat_rsp_file "$leaf_build_dir")"
}

run_ci_mode()
{
    run_test_case ref 1q127L3 aes
    run_test_case opt 1q31L10 shake
    run_test_case opt 1q127L10 aes

    if have_x86_64; then
        run_test_case avx2 1q127L3 aes
        run_test_case avx2 1q127L10 aes
        run_test_case avx2 1q31L10 shake
    else
        echo "==> skip avx2 tests on arch=$arch"
    fi

    run_check_kat_case opt 1q127L3 aes
    run_check_kat_case opt 1q127L10 aes
    if have_x86_64; then
        run_check_kat_case avx2 1q127L10 aes
    fi

    generate_nist_tree
    run_nist_kat_case opt 1q31L3 shake
    run_nist_kat_case opt 1q127L10 aes
    if have_x86_64; then
        run_nist_kat_case avx2 1q31L3 shake
        run_nist_kat_case avx2 1q127L10 aes
    fi
}

run_release_mode()
{
    run_test_sweep ref
    run_test_sweep opt

    if have_x86_64; then
        run_test_sweep avx2
    else
        echo "==> skip avx2 test sweep on arch=$arch"
    fi

    run_check_kat_case ref 1q127L3 aes
    run_check_kat_case ref 1q127L10 aes
    run_check_kat_case opt 1q127L3 aes
    run_check_kat_case opt 1q127L10 aes
    if have_x86_64; then
        run_check_kat_case avx2 1q127L3 aes
        run_check_kat_case avx2 1q127L10 aes
    fi

    generate_nist_tree
    run_nist_kat_case ref 1q31L3 shake
    run_nist_kat_case ref 1q127L10 aes
    run_nist_kat_case opt 1q31L3 shake
    run_nist_kat_case opt 1q127L10 aes
    if have_x86_64; then
        run_nist_kat_case avx2 1q31L3 shake
        run_nist_kat_case avx2 1q127L10 aes
    fi

    if have_valgrind; then
        run_valgrind_case ref 1q127L3 aes
        if have_x86_64; then
            run_valgrind_case avx2 1q127L3 aes
            run_valgrind_case avx2 1q31L10 shake
        else
            echo "==> skip avx2 valgrind on arch=$arch"
        fi
    else
        echo "==> skip valgrind checks (valgrind not found)"
    fi
}

cd "$repo_dir"

rm -rf "$tmp_root"

case "$mode" in
    CI)
        run_ci_mode
        ;;
    RELEASE)
        run_release_mode
        ;;
    *)
        usage
        ;;
esac

echo "$mode checks passed"
