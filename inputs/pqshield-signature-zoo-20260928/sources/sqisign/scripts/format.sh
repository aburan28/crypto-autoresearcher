#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
#
# Format (or check) the project's C sources with clang-format.
#
#   scripts/format.sh                 format every file in scope, in place
#   scripts/format.sh --check         report badly formatted files, change nothing
#   scripts/format.sh [--check] PATH... restrict the run to PATH...
#
# The clang-format version and the set of files to skip are NOT configured here:
# both are read from .pre-commit-config.yaml so that this script, the
# pre-commit hook and CI can never disagree. See FORMATTING.md.
#
# The binary itself is the one pre-commit downloaded for that pinned version,
# taken from its cache; nothing on PATH is used. Set CLANG_FORMAT to override
# that with a specific binary (this is what CI does):
#   CLANG_FORMAT=$(which clang-format-18) scripts/format.sh --check

set -eu

CONFIG=".pre-commit-config.yaml"

# Work from the top of the checkout, so the script can be run from anywhere.
if ! TOPLEVEL=$(git rev-parse --show-toplevel 2>/dev/null); then
    echo "error: not inside a git checkout" >&2
    exit 1
fi
cd "$TOPLEVEL"

if [ ! -f "$CONFIG" ]; then
    echo "error: $CONFIG not found in $TOPLEVEL" >&2
    exit 1
fi

check_only=0
if [ "${1-}" = "--check" ]; then
    check_only=1
    shift
fi

# ---------------------------------------------------------------------------
# Read the pinned version and the exclusion list out of $CONFIG.
#
# Both extractions are fatal on failure: silently falling back to "no exclusions" would reformat vendored and generated
# code, which is exactly the mistake this script exists to prevent.
# ---------------------------------------------------------------------------
PINNED=$(sed -n 's/^[[:space:]]*rev:[[:space:]]*v\{0,1\}\([0-9][0-9.]*\)[[:space:]]*$/\1/p' "$CONFIG")
EXCLUDE=$(sed -n "s/^[[:space:]]*exclude:[[:space:]]*'\(.*\)'[[:space:]]*\$/\1/p" "$CONFIG")

if [ -z "$PINNED" ]; then
    echo "error: could not read 'rev:' from $CONFIG" >&2
    exit 1
fi
if [ -z "$EXCLUDE" ]; then
    echo "error: could not read 'exclude:' from $CONFIG" >&2
    echo "       it must be a single line wrapped in single quotes" >&2
    exit 1
fi
PINNED_MAJOR=${PINNED%%.*}

# ---------------------------------------------------------------------------
# Locate a clang-format whose major version matches the pin.
#
# Nothing on PATH is considered; the binary comes from pre-commit's cache. The cache root is pre-commit's documented
# interface ($PRE_COMMIT_HOME, else $XDG_CACHE_HOME); the layout inside it is not, so the known layout is tried first
# and a search of the root is the fallback if pre-commit ever rearranges it.
# ---------------------------------------------------------------------------
clang_format_version() {
    "$1" --version 2>/dev/null | sed -n 's/.*version \([0-9][0-9.]*\).*/\1/p'
}

CF=""
CF_VERSION=""
# ${HOME-} rather than $HOME: with `set -u` an unset HOME would be fatal here, even for a CLANG_FORMAT run that never
# looks at the cache. The resulting nonsense path simply matches nothing.
PRE_COMMIT_CACHE=${PRE_COMMIT_HOME:-${XDG_CACHE_HOME:-${HOME-}/.cache}/pre-commit}

# Sets CF/CF_VERSION from the candidate paths read on stdin. An exact $PINNED match wins outright; otherwise the first
# $PINNED_MAJOR.x seen is kept as a fallback, so an environment left over from an older pin is skipped rather than used.
select_clang_format() {
    local candidate version fallback="" fallback_version=""
    while IFS= read -r candidate; do
        [ -x "$candidate" ] || continue # also skips a glob that matched nothing and expanded to itself
        version=$(clang_format_version "$candidate")
        [ "${version%%.*}" = "$PINNED_MAJOR" ] || continue
        if [ "$version" = "$PINNED" ]; then
            CF="$candidate"
            CF_VERSION="$version"
            return 0
        fi
        [ -n "$fallback" ] || {
            fallback="$candidate"
            fallback_version="$version"
        }
    done
    [ -n "$fallback" ] || return 1
    CF="$fallback"
    CF_VERSION="$fallback_version"
}

# Process substitution, not a pipe: a piped select_clang_format would run in a subshell and its assignment to CF would
# be discarded when that subshell exits.
find_in_pre_commit_cache() {
    # The layout pre-commit 4.x actually uses. Usually one stat and one --version, no directory walk.
    select_clang_format < <(printf '%s\n' "$PRE_COMMIT_CACHE"/repo*/py_env-*/bin/clang-format) && return 0
    # Only reached if that ever moves: search the cache root rather than failing outright. Bounded to the depth the
    # binary could plausibly live at, which also skips the duplicate copy deeper inside site-packages.
    select_clang_format < <(find "$PRE_COMMIT_CACHE" -maxdepth 4 -type f -perm -u+x -name clang-format 2>/dev/null)
}

if [ -n "${CLANG_FORMAT-}" ]; then
    # An explicit CLANG_FORMAT of the wrong version is a user error, not something to silently skip past.
    version=$(clang_format_version "$CLANG_FORMAT")
    if [ "${version%%.*}" != "$PINNED_MAJOR" ]; then
        echo "error: CLANG_FORMAT=$CLANG_FORMAT is version ${version:-unknown}," \
             "but this project requires clang-format $PINNED_MAJOR.x" >&2
        exit 1
    fi
    CF="$CLANG_FORMAT"
    CF_VERSION="$version"
else
    # A miss here is not fatal, so it must not trip `set -e`.
    find_in_pre_commit_cache || true
fi

if [ -z "$CF" ]; then
    if ! command -v pre-commit >/dev/null 2>&1; then
        cat >&2 <<EOF
error: clang-format $PINNED not found.

This project gets it from pre-commit:

    pipx install pre-commit     # or brew / apt / uv -- see FORMATTING.md
    pre-commit install --install-hooks

Then re-run this command.
EOF
    else
        # `pre-commit install` on its own only writes .git/hooks/pre-commit; the hook environments, and so the binary
        # this script needs, are not built until --install-hooks or the first commit.
        cat >&2 <<EOF
error: clang-format $PINNED not found in $PRE_COMMIT_CACHE.

    pre-commit install --install-hooks    # fetch it (needs network once)

Or point at a binary yourself: CLANG_FORMAT=/path/to/clang-format $0
EOF
    fi
    exit 1
fi

if [ "$CF_VERSION" != "$PINNED" ]; then
    echo "note: using clang-format $CF_VERSION; CI pins $PINNED." \
         "Any $PINNED_MAJOR.x release formats this tree identically." >&2
fi

# ---------------------------------------------------------------------------
# Build the file list.
# ---------------------------------------------------------------------------
if [ "$#" -gt 0 ]; then
    files=$(git ls-files -- "$@" | grep -E '\.[ch]$' || true)
else
    files=$(git ls-files '*.c' '*.h')
fi
files=$(printf '%s\n' "$files" | grep -vE "$EXCLUDE" || true)

if [ -z "$files" ]; then
    echo "no files to format"
    exit 0
fi
count=$(printf '%s\n' "$files" | wc -l | tr -d ' ')

# ---------------------------------------------------------------------------
# Run.
# ---------------------------------------------------------------------------
status=0
if [ "$check_only" -eq 1 ]; then
    printf '%s\n' "$files" | tr '\n' '\0' \
        | xargs -0 "$CF" --style=file --dry-run --Werror || status=$?
    if [ "$status" -ne 0 ]; then
        cat >&2 <<EOF

error: $count files checked, some are not correctly formatted (see above).
       Run 'scripts/format.sh' (or 'make format') to fix them.
EOF
        exit 1
    fi
    echo "$count files checked, all correctly formatted"
else
    printf '%s\n' "$files" | tr '\n' '\0' | xargs -0 "$CF" --style=file -i
    echo "$count files formatted with clang-format $CF_VERSION"
fi
