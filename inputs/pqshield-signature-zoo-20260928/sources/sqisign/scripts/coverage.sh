#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
#
# Measure test coverage of the project with gcov and gcovr.
#
#   scripts/coverage.sh                        measure every configuration valid on this host
#   scripts/coverage.sh --config=ref,arm64     measure the named configurations instead
#   scripts/coverage.sh --open                 open the HTML report when it is done
#   scripts/coverage.sh --summary=FILE         append a markdown summary to FILE
#   scripts/coverage.sh --fail-under=N         exit non-zero below N percent line coverage
#
# Set GCOVR=/path/to/gcovr to pick a specific binary.
#
# Configures CMAKE_BUILD_TYPE=COVERAGE (-O0, no LTO) in build-coverage-<config>/, builds it, runs ctest, and turns the
# resulting .gcda files into a report. Without --fail-under the exit status reflects only setup errors and failing
# tests, never a low number.

set -eu

# 7.0 is the minimum, while 8.5 collapses the report into a single self-contained .html file, see html_args below.
MIN_VERSION=7.0

# Both the gcovr filters and ctest's KAT tests need the repository root as the working directory.
TOPLEVEL=$(git rev-parse --show-toplevel) || exit 1
cd "$TOPLEVEL"

# shellcheck source=scripts/quality_checks_exclusions.sh
. "$TOPLEVEL/scripts/quality_checks_exclusions.sh"

# broadwell and arm64 each need their own assembly, so only the one matching the host is offered.
case "$(uname -m)" in
    x86_64 | amd64) HOST_CONFIGS="ref broadwell" ;;
    arm64 | aarch64) HOST_CONFIGS="ref arm64" ;;
    *) HOST_CONFIGS="ref" ;;
esac

open_report=0
summary_file=""
fail_under=""
configs=""
for arg in "$@"; do
    case "$arg" in
        --config=*) configs="$configs ${arg#--config=}" ;;
        --open) open_report=1 ;;
        --summary=*) summary_file=${arg#--summary=} ;;
        --fail-under=*)
            fail_under=${arg#--fail-under=}
            case "$fail_under" in
                '' | *[!0-9.]*)
                    echo "error: --fail-under wants a percentage, got '$fail_under'" >&2
                    exit 1
                    ;;
            esac
            ;;
        *)
            echo "error: unknown argument '$arg'; see the comments at the top of $0" >&2
            exit 1
            ;;
    esac
done
IFS=', ' read -ra CONFIGS <<<"${configs:-$HOST_CONFIGS}"

GCOVR=${GCOVR:-gcovr}
version=$("$GCOVR" --version 2>/dev/null | sed -n 's/^gcovr \([0-9][0-9.]*\).*/\1/p') || true
if [ -z "$version" ]; then
    echo "error: gcovr not found or unrecognized (looked for '$GCOVR')." >&2
    echo "       apt-get install gcovr / brew install gcovr, or set GCOVR=/path/to/it" >&2
    exit 1
fi
if [ "$(printf '%s\n%s\n' "$version" "$MIN_VERSION" | sort -V | head -1)" != "$MIN_VERSION" ]; then
    echo "error: gcovr $version is too old; this project needs >= $MIN_VERSION." >&2
    echo "       Debian bookworm (6.0) and Ubuntu 22.04 (5.0) are too old: use a newer release" >&2
    echo "       (Debian trixie 7.2, Ubuntu 24.04 7.0), backports, or pip install gcovr." >&2
    exit 1
fi

# The sanity guard, --fail-under and --summary all read gcovr's JSON summary rather than re-running gcovr.
if ! command -v python3 >/dev/null 2>&1; then
    echo "error: python3 is required to read gcovr's JSON summary." >&2
    exit 1
fi

# gcovr wants regexes, not paths. The harness list is excluded here but nowhere else.
qc_exclude_check "${QC_EXCLUDE[@]}" "${QC_EXCLUDE_HARNESS[@]}" || exit 1
EXCLUDE=()
while IFS= read -r re; do
    EXCLUDE+=("$re")
done < <(qc_exclude_regexes "${QC_EXCLUDE[@]}" "${QC_EXCLUDE_HARNESS[@]}")

# The per-module unit tests, as one regex rather than 23 entries in the shared list.
TESTS_RE='.*/test/'
git ls-files | grep -qE "^$TESTS_RE" || {
    echo "error: '$TESTS_RE' in $0 matches nothing in the tree" >&2
    exit 1
}
EXCLUDE+=("$TESTS_RE")

jobs=$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4)

# --root plus repository-relative filters, so the report reads the same wherever it was produced. Headers are included:
# much of gf and ec is static inline.
GCOVR_ARGS=(
    --root "$TOPLEVEL"
    --filter 'src/'
    --filter 'apps/'
    --exclude-unreachable-branches
    --merge-mode-functions merge-use-line-min
    --gcov-ignore-parse-errors all
    -j "$jobs"
)
for path in "${EXCLUDE[@]}"; do
    GCOVR_ARGS+=(--exclude "$path")
done

# 8.5 dropped the argument --html-single-page took in 7.x, so only spell it where the bare form is right. Below that the
# report is a directory of pages; --html-self-contained keeps it usable offline, which is how it is always read.
if [ "$(printf '%s\n8.5\n' "$version" | sort -V | head -1)" = "8.5" ]; then
    single_page=1
else
    single_page=0
fi

# Overall line/branch/function figures plus one row per module, from gcovr's own JSON. The HTML report is entirely
# gcovr's.
markdown_summary() {
    python3 - "$1" "$2" <<'PY'
import json, sys

cfg, path = sys.argv[1:3]
data = json.load(open(path))


def cell(entry, kind):
    total = entry.get("%s_total" % kind, 0)
    if not total:
        return "-"
    return "%.1f%% (%d/%d)" % (entry.get("%s_percent" % kind, 0.0), entry.get("%s_covered" % kind, 0), total)


def module(filename):
    parts = filename.split("/")
    return "/".join(parts[:2]) if parts[0] == "src" and len(parts) > 2 else parts[0]


modules = {}
for entry in data.get("files", []):
    acc = modules.setdefault(module(entry["filename"]), {})
    for kind in ("line", "branch", "function"):
        for suffix in ("total", "covered"):
            key = "%s_%s" % (kind, suffix)
            acc[key] = acc.get(key, 0) + entry.get(key, 0)
for acc in modules.values():
    for kind in ("line", "branch", "function"):
        total = acc["%s_total" % kind]
        acc["%s_percent" % kind] = 100.0 * acc["%s_covered" % kind] / total if total else 0.0

out = ["### Coverage: %s" % cfg, ""]
out += ["| Module | Lines | Branches | Functions |", "|---|---|---|---|"]
out += ["| **Total** | %s | %s | %s |" % tuple(cell(data, k) for k in ("line", "branch", "function"))]
out += [
    "| `%s` | %s | %s | %s |" % ((name,) + tuple(cell(acc, k) for k in ("line", "branch", "function")))
    for name, acc in sorted(modules.items())
]
print("\n".join(out) + "\n")
PY
}

echo "gcovr $version, configurations: ${CONFIGS[*]}"
status=0

for cfg in "${CONFIGS[@]}"; do
    builddir="build-coverage-$cfg"

    mkdir -p "$builddir"
    generator=()
    command -v ninja >/dev/null 2>&1 && generator=(-G Ninja)
    if ! cmake -S . -B "$builddir" -DCMAKE_BUILD_TYPE=COVERAGE -DSQISIGN_BUILD_TYPE="$cfg" \
        -DSQISIGN_TEST_REPS=1 ${generator[@]+"${generator[@]}"} \
        >"$builddir/configure.log" 2>&1; then
        echo "error: cmake configure failed for SQISIGN_BUILD_TYPE=$cfg, see $builddir/configure.log" >&2
        exit 1
    fi

    echo "$cfg: building"
    if ! cmake --build "$builddir" -j "$jobs" >"$builddir/build.log" 2>&1; then
        echo "error: build failed for SQISIGN_BUILD_TYPE=$cfg, see $builddir/build.log" >&2
        exit 1
    fi

    # Counters accumulate across runs, so a second invocation would otherwise report the sum of both.
    find "$builddir" -name '*.gcda' -delete

    echo "$cfg: testing"
    if ! ctest --test-dir "$builddir" -j "$jobs" -E threadsafety --output-on-failure \
        >"$builddir/ctest.log" 2>&1; then
        echo "warning: $cfg: some tests failed, so the report is of a partly failing suite; see $builddir/ctest.log" >&2
        status=1
    fi

    # gcov must come from the same toolchain as the compiler; llvm-cov emulates it for clang builds.
    cc=$(sed -n 's/^CMAKE_C_COMPILER:[A-Z]*=//p' "$builddir/CMakeCache.txt")
    gcov_args=()
    case "$cc" in
        *clang*)
            if llvm_cov=$(command -v llvm-cov 2>/dev/null) || llvm_cov=$(xcrun --find llvm-cov 2>/dev/null); then
                gcov_args=(--gcov-executable "$llvm_cov gcov")
            else
                echo "error: $cc is clang, but no llvm-cov was found to read its coverage data." >&2
                exit 1
            fi
            ;;
    esac

    html_args=(--html-title "SQIsign coverage ($cfg)" --html-self-contained)
    if [ "$single_page" -eq 1 ]; then
        report="$builddir/coverage.html"
        html_args+=(--html-single-page --html-nested "$report")
    else
        report="$builddir/coverage-html/index.html"
        mkdir -p "$builddir/coverage-html"
        html_args+=(--html-nested "$report")
    fi

    "$GCOVR" "${GCOVR_ARGS[@]}" ${gcov_args[@]+"${gcov_args[@]}"} "${html_args[@]}" \
        --json-summary-pretty --json-summary "$builddir/summary.json" \
        --txt-summary "$builddir" 2>"$builddir/gcovr.log" || {
        echo "error: gcovr failed for SQISIGN_BUILD_TYPE=$cfg, see $builddir/gcovr.log" >&2
        exit 1
    }

    # Skipped lines make the report understate coverage.
    if grep -q '(WARNING)' "$builddir/gcovr.log"; then
        echo "warning: $cfg: gcovr could not parse some gcov output and skipped it; see $builddir/gcovr.log" >&2
    fi

    # A run that measured nothing reports 0% just as loudly as a genuinely untested tree.
    read -r total_lines line_percent <<<"$(python3 -c \
        'import json,sys; d=json.load(open(sys.argv[1])); print(d["line_total"], d["line_percent"])' \
        "$builddir/summary.json" || echo '0 0')"
    if [ "$total_lines" -eq 0 ]; then
        echo "error: $cfg: gcovr found no instrumented lines. This is a bug in $0, not an untested tree." >&2
        exit 1
    fi

    echo "$cfg: report at $report"
    if [ -n "$summary_file" ]; then
        markdown_summary "$cfg" "$builddir/summary.json" >>"$summary_file"
    fi
    # gcovr's own --fail-under-line would parse every gcov file a second time for a number we already have.
    if [ -n "$fail_under" ] && awk "BEGIN { exit !($line_percent < $fail_under) }"; then
        echo "error: $cfg: line coverage $line_percent% is below the --fail-under=$fail_under threshold" >&2
        status=1
    fi
    if [ "$open_report" -eq 1 ]; then
        if command -v xdg-open >/dev/null 2>&1; then
            xdg-open "$report" >/dev/null 2>&1 &
        elif command -v open >/dev/null 2>&1; then
            open "$report"
        fi
    fi
done

exit "$status"
