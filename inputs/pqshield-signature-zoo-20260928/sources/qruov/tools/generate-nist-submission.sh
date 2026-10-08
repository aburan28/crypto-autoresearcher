#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

: "${NIST_SUBMISSION_DIR:?}"
: "${PARAM_CHOICES:?}"
: "${PRG_CHOICES:?}"
: "${DEFAULT_PARAM:?}"
: "${DEFAULT_PRG:?}"
: "${NIST_IMPL_CFLAGS_REF?}"
: "${NIST_IMPL_CFLAGS_OPT?}"
: "${NIST_IMPL_CFLAGS_AVX2?}"
: "${NIST_KAT_SRCS_REF?}"
: "${NIST_KAT_SRCS_OPT?}"
: "${NIST_KAT_SRCS_AVX2?}"

case "$NIST_SUBMISSION_DIR" in
    /*) out_dir=$NIST_SUBMISSION_DIR ;;
    *) out_dir=$repo_dir/$NIST_SUBMISSION_DIR ;;
esac

nist_ref_dir=$out_dir/Reference_Implementation/ref
nist_opt_dir=$out_dir/Optimized_Implementation/opt
nist_avx2_dir=$out_dir/Optimized_Implementation/avx2

sed_escape()
{
    printf '%s' "$1" | sed 's/[&|]/\\&/g'
}

generate_leaf_makefile()
{
    impl=$1
    impl_cflags=$2
    srcs=$3
    out=$4

    sed \
        -e "s|@IMPL@|$(sed_escape "$impl")|g" \
        -e "s|@PARAM_CHOICES@|$(sed_escape "$PARAM_CHOICES")|g" \
        -e "s|@PRG_CHOICES@|$(sed_escape "$PRG_CHOICES")|g" \
        -e "s|@DEFAULT_PARAM@|$(sed_escape "$DEFAULT_PARAM")|g" \
        -e "s|@DEFAULT_PRG@|$(sed_escape "$DEFAULT_PRG")|g" \
        -e "s|@IMPL_CFLAGS@|$(sed_escape "$impl_cflags")|g" \
        -e "s|@SRCS@|$(sed_escape "$srcs")|g" \
        "$repo_dir/GNUmakefile.nist.in" > "$out"
}

if [ -e "$out_dir" ]; then
    echo "error: $NIST_SUBMISSION_DIR already exists" >&2
    exit 1
fi

mkdir -p "$nist_ref_dir" "$nist_opt_dir" "$nist_avx2_dir"
cp "$repo_dir/README.md" "$out_dir/README.md"
cp "$repo_dir"/src/*.[ch] "$nist_ref_dir"/
cp "$repo_dir"/src/*.[ch] "$nist_opt_dir"/
cp "$repo_dir"/src/*.[ch] "$nist_avx2_dir"/
cp "$repo_dir"/src/ref/* "$nist_ref_dir"/
cp "$repo_dir"/src/opt/* "$nist_opt_dir"/
cp "$repo_dir"/src/avx2/* "$nist_avx2_dir"/

generate_leaf_makefile ref "$NIST_IMPL_CFLAGS_REF" "$NIST_KAT_SRCS_REF" "$nist_ref_dir/GNUmakefile"
generate_leaf_makefile opt "$NIST_IMPL_CFLAGS_OPT" "$NIST_KAT_SRCS_OPT" "$nist_opt_dir/GNUmakefile"
generate_leaf_makefile avx2 "$NIST_IMPL_CFLAGS_AVX2" "$NIST_KAT_SRCS_AVX2" "$nist_avx2_dir/GNUmakefile"

echo "wrote $NIST_SUBMISSION_DIR"
