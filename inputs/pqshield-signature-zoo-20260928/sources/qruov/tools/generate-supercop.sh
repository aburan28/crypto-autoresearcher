#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

: "${SUPERCOP_SUBMISSION_DIR:?}"
: "${SUPERCOP_PARAM_CHOICES:?}"
: "${SUPERCOP_PRG_CHOICES:?}"
: "${SUPERCOP_IMPL_CHOICES:?}"
: "${SUPERCOP_CC:?}"
: "${SUPERCOP_CFLAGS:?}"
: "${SUPERCOP_PRG_CFLAGS_AES:?}"
: "${SUPERCOP_PRG_CFLAGS_SHAKE:?}"

case "$SUPERCOP_SUBMISSION_DIR" in
    /*) out_dir=$SUPERCOP_SUBMISSION_DIR ;;
    *) out_dir=$repo_dir/$SUPERCOP_SUBMISSION_DIR ;;
esac

if [ -e "$out_dir" ]; then
    echo "error: $SUPERCOP_SUBMISSION_DIR already exists" >&2
    exit 1
fi

tmpdir=$(mktemp -d /tmp/qruov-supercop-XXXXXX)
trap 'rm -rf "$tmpdir"' EXIT

mkdir -p "$out_dir/crypto_sign"

meta_bin_for()
{
    param=$1
    prg=$2
    bin=$tmpdir/print-scheme-meta-$param-$prg

    case "$prg" in
        aes) prg_cflags=$SUPERCOP_PRG_CFLAGS_AES ;;
        shake) prg_cflags=$SUPERCOP_PRG_CFLAGS_SHAKE ;;
        *)
            echo "error: unsupported PRG '$prg'" >&2
            exit 1
            ;;
    esac

    # print-scheme-meta only needs the scheme configuration, not an implementation build.
    # shellcheck disable=SC2086
    $SUPERCOP_CC $SUPERCOP_CFLAGS $prg_cflags -DQRUOV_PARAM_$param -Isrc \
        "$repo_dir/tools/print-scheme-meta.c" -o "$bin"

    printf '%s\n' "$bin"
}

load_scheme_meta()
{
    param=$1
    prg=$2
    bin=$(meta_bin_for "$param" "$prg")
    meta_file=$tmpdir/meta-$param-$prg
    "$bin" > "$meta_file"
    {
        IFS= read -r CRYPTO_SECRETKEYBYTES
        IFS= read -r CRYPTO_PUBLICKEYBYTES
        IFS= read -r CRYPTO_BYTES
        IFS= read -r CRYPTO_ALGNAME
    } < "$meta_file"
}

copy_common_sources()
{
    leaf_dir=$1

    for path in "$repo_dir"/src/*.[ch]; do
        base=$(basename "$path")
        case "$base" in
            api.h|rng.c|PQCgenKAT_sign.c)
                continue
                ;;
        esac
        cp "$path" "$leaf_dir/$base"
    done
}

copy_impl_sources()
{
    impl=$1
    leaf_dir=$2

    for path in "$repo_dir"/src/"$impl"/*; do
        base=$(basename "$path")
        cp "$path" "$leaf_dir/$base"
    done
}

patch_supercop_sources()
{
    impl=$1
    leaf_dir=$2
    param=$3
    prg=$4
    prg_is_aes=0
    aes_backend_define=

    case "$impl" in
        avx2) aes_backend_define='#define PRIM_AES_BACKEND_X86AESNI 1' ;;
    esac

    case "$prg" in
        aes) prg_is_aes=1 ;;
        shake) prg_is_aes=0 ;;
        *)
            echo "error: unsupported PRG '$prg'" >&2
            exit 1
            ;;
    esac

    {
        IFS= read -r line
        printf '%s\n' "$line"
        IFS= read -r line
        printf '%s\n' "$line"
        printf '#define QRUOV_PARAM_%s\n' "$param"
        printf '#define PRG_IS_AES %s\n' "$prg_is_aes"
        if [ -n "$aes_backend_define" ]; then
            printf '%s\n' "$aes_backend_define"
        fi
        cat
    } < "$leaf_dir/qruov_param.h" > "$leaf_dir/qruov_param.h.tmp"
    mv "$leaf_dir/qruov_param.h.tmp" "$leaf_dir/qruov_param.h"

    sed 's/#include "rng.h"/#include "randombytes.h"/' \
        "$leaf_dir/sign.c" > "$leaf_dir/sign.c.tmp"
    mv "$leaf_dir/sign.c.tmp" "$leaf_dir/sign.c"

    sed 's/#include "qruov.h"/#include "qruov.h"\n#include "crypto_sign.h"/' \
        "$leaf_dir/sign.c" > "$leaf_dir/sign.c.tmp"
    mv "$leaf_dir/sign.c.tmp" "$leaf_dir/sign.c"
}

generate_api_h()
{
    leaf_dir=$1

    cat > "$leaf_dir/api.h" <<EOF
#ifndef api_h
#define api_h

#define CRYPTO_SECRETKEYBYTES $CRYPTO_SECRETKEYBYTES
#define CRYPTO_PUBLICKEYBYTES $CRYPTO_PUBLICKEYBYTES
#define CRYPTO_BYTES $CRYPTO_BYTES
#define CRYPTO_ALGNAME "$CRYPTO_ALGNAME"

int
crypto_sign_keypair(unsigned char *pk, unsigned char *sk);

int
crypto_sign(unsigned char *sm, unsigned long long *smlen,
            const unsigned char *m, unsigned long long mlen,
            const unsigned char *sk);

int
crypto_sign_open(unsigned char *m, unsigned long long *mlen,
                 const unsigned char *sm, unsigned long long smlen,
                 const unsigned char *pk);

#endif /* api_h */
EOF
}

generate_scheme_metadata()
{
    scheme_dir=$1

    cat > "$scheme_dir/description" <<EOF
QR-UOV digital signature
EOF
}

generate_impl_metadata()
{
    impl=$1
    leaf_dir=$2

    case "$impl" in
        avx2)
            cat > "$leaf_dir/architectures" <<EOF
amd64
EOF
            ;;
    esac
}

for prg in $SUPERCOP_PRG_CHOICES; do
    for param in $SUPERCOP_PARAM_CHOICES; do
        load_scheme_meta "$param" "$prg"
        scheme_dir=$out_dir/crypto_sign/$CRYPTO_ALGNAME
        mkdir -p "$scheme_dir"
        generate_scheme_metadata "$scheme_dir"
        for impl in $SUPERCOP_IMPL_CHOICES; do
            leaf_dir=$scheme_dir/$impl
            mkdir -p "$leaf_dir"
            copy_common_sources "$leaf_dir"
            copy_impl_sources "$impl" "$leaf_dir"
            patch_supercop_sources "$impl" "$leaf_dir" "$param" "$prg"
            generate_api_h "$leaf_dir"
            generate_impl_metadata "$impl" "$leaf_dir"
        done
    done
done

echo "wrote $SUPERCOP_SUBMISSION_DIR"
