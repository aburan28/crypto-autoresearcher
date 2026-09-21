#!/bin/sh
# emit_host_binding_v2.sh
#
# Sixth-generation repair of emit_host_binding.sh (v1 predecessor:
# coordination/goals/GOAL-ENDO-001/batches/BATCH-820ee8/tasks/TASK-20260830-78b00f/emit_host_binding.sh).
# This file is an ADDITIVE successor: the v1 predecessor is not edited,
# replaced, or reinterpreted. Repairs RT-J2-O1 only (PATH manipulation);
# RT-J2-O3 and RT-J3-O1 are repaired in emit_procedure_v2.md and
# repair-package-v6.yaml respectively, not here. RT-J2-O2 (self-attestation)
# is a DISCLOSED, unrepaired limitation carried forward unchanged -- see
# emit_procedure_v2.md "narrowed provenance declaration".
#
# Emit a host_binding JSON block from the host's own identity surfaces.
#
# POSIX sh. No network access. No repository writes. Reads ONLY the host's
# own identity surfaces (hostname; the filesystem device and mount point of
# the working directory the script is run from).
#
# --------------------------------------------------------------------------
# RT-J2-O1 REPAIR: every external command below is invoked by an ABSOLUTE
# PATH pinned literally in this script, never by bare name. A caller who
# prepends a directory containing fake `hostname`/`df`/etc. binaries to PATH
# cannot influence which binary executes, because PATH is never consulted:
# the shell invokes the literal pathname directly. This closes RT-J2-O1
# against exactly the attack that found it (PATH-prepending a hostile
# `hostname`/`df`).
#
# Absolute paths below were verified to exist on THIS authoring host with
# `command -v <cmd>` at authoring time (recorded in runtime-session-receipt.json
# and repair-package-v6.yaml). This host is Darwin (macOS). A comment next to
# each constant documents the common Linux-equivalent absolute path, which
# commonly differs; this script does NOT attempt runtime OS detection or
# fallback -- it is pinned to the paths verified on the authoring host. A
# port to a host where these absolute paths do not exist must re-verify with
# `command -v` and update the constants; that is an explicit, reviewable
# script change, never a silent PATH lookup.
#
# Verified on this host with `command -v <cmd>` (see runtime-session-receipt.json):
#   HOSTNAME_BIN=/bin/hostname   (Linux common equivalent: /bin/hostname or
#                                 /usr/bin/hostname; some minimal/busybox
#                                 images only provide /bin/hostname)
#   DF_BIN=/bin/df                (Linux common equivalent: /bin/df or
#                                 /usr/bin/df)
#   DATE_BIN=/bin/date            (Linux common equivalent: /bin/date)
#   SED_BIN=/usr/bin/sed          (Linux common equivalent: /bin/sed or
#                                 /usr/bin/sed)
#   AWK_BIN=/usr/bin/awk          (Linux common equivalent: /usr/bin/awk or
#                                 /bin/awk; some minimal images symlink this
#                                 to busybox awk)
#   TR_BIN=/usr/bin/tr            (Linux common equivalent: /usr/bin/tr or
#                                 /bin/tr)
#   TAIL_BIN=/usr/bin/tail        (Linux common equivalent: /usr/bin/tail or
#                                 /bin/tail)
#
# `printf`, `[`, and other constructs used below are POSIX sh BUILTINS, not
# externally resolved commands (verified with `type printf` at authoring
# time: "printf is a shell builtin" on this host's /bin/sh). Builtins are not
# subject to PATH-based command substitution in the same way external
# binaries are, since the shell itself implements them; they are unaffected
# by prepending a hostile directory to PATH. No PATH lookup for any external
# command remains in this script.
# --------------------------------------------------------------------------

HOSTNAME_BIN=/bin/hostname
DF_BIN=/bin/df
DATE_BIN=/bin/date
SED_BIN=/usr/bin/sed
AWK_BIN=/usr/bin/awk
TR_BIN=/usr/bin/tr
TAIL_BIN=/usr/bin/tail

# Fail closed if any pinned absolute path does not exist or is not
# executable on this host -- this is a repair-time / run-time integrity
# check, not a PATH lookup: it verifies the literal pinned path, it never
# searches PATH for an alternative.
for _bin in "$HOSTNAME_BIN" "$DF_BIN" "$DATE_BIN" "$SED_BIN" "$AWK_BIN" \
            "$TR_BIN" "$TAIL_BIN"; do
  if [ ! -x "$_bin" ]; then
    printf 'emit_host_binding_v2: ERROR: pinned absolute path not executable on this host: %s\n' \
      "$_bin" >&2
    printf 'emit_host_binding_v2: this script is pinned to paths verified on the authoring host; re-verify with `command -v` and update the constants before running elsewhere.\n' >&2
    exit 1
  fi
done
unset _bin

# Output: a single JSON object on stdout with exactly:
#   schema            -- crypto.autoresearch.runtime_session_receipt.v2
#   host_binding.host_id
#   host_binding.filesystem_id
#   host_binding.filesystem_mount
#   emitted_at        -- UTC ISO-8601 timestamp
#
# Failure behavior: if ANY identity surface is unreadable or empty after
# normalization, the script writes a diagnostic to stderr, emits NO partial
# JSON block on stdout, and exits nonzero. Placeholder values are never
# emitted. (Preserved unchanged from v1.)
#
# Host identity surfaces:
#
#   host_id:            "$HOSTNAME_BIN" (absolute path pinned above).
#     Normalization (per v5 rule): trimmed, case-preserved.
#
#   filesystem_id:       "$DF_BIN" -P . first column (the device path).
#     Normalization (per v5 rule): lowercase, trimmed, no trailing slash.
#
#   filesystem_mount:    "$DF_BIN" -P . trailing column(s) (the mount point).
#     Normalization (per v5 rule): absolute POSIX path, trailing slash
#     stripped except root "/".
#
# The -P (POSIX) flag on df guarantees one line per filesystem with the
# mount point in the trailing field(s), preventing line-wrap on long
# device names. Mount points may contain spaces; the extraction below
# takes everything after the first five df fields to preserve that.
#
# RT-J2-O3 NOTE (documented fully in emit_procedure_v2.md): this script
# captures the CWD's filesystem identity at the moment it runs. It cannot
# by itself detect a "paste-from-different-mount" attack (running the
# script on one mount and presenting the output as if captured on another);
# that is a procedural/reviewer-verification control, not something this
# script can enforce internally. See emit_procedure_v2.md Step "Independent
# mount verification".

set -u

# -----------------------------------------------------------------------
# Capture all three surfaces BEFORE emitting anything. If any surface is
# unreadable, we exit with no stdout output.
# -----------------------------------------------------------------------

# --- host_id: hostname surface (absolute path, no PATH lookup) ---
host_id_raw=$("$HOSTNAME_BIN" 2>/dev/null) || host_id_raw=""
host_id=$(printf '%s' "$host_id_raw" | "$SED_BIN" 's/^[[:space:]]*//; s/[[:space:]]*$//')

# --- df line for the working directory (absolute path, no PATH lookup) ---
# Capture df separately from tail so a nonzero df status is not masked by
# tail's success, and drop the header row so a header-only failure cannot be
# parsed as a data line.
if df_out=$("$DF_BIN" -P . 2>/dev/null); then
  df_line=$(printf '%s\n' "$df_out" | "$AWK_BIN" 'NR > 1' | "$TAIL_BIN" -1)
else
  df_line=""
fi

# --- filesystem_id: device path (first field of df output) ---
fs_dev_raw=$(printf '%s' "$df_line" | "$AWK_BIN" '{print $1}')
# Normalize: trim, strip trailing slash, lowercase
fs_dev=$(printf '%s' "$fs_dev_raw" \
  | "$SED_BIN" 's/^[[:space:]]*//; s/[[:space:]]*$//; s#/$##' \
  | "$TR_BIN" 'A-Z' 'a-z')

# --- filesystem_mount: mount point (everything after the first 5 fields) ---
# df -P POSIX format: Filesystem 512-blocks Used Available Capacity Mounted-on
# The mount point is fields 6..NF and may contain spaces.
fs_mount_raw=$(printf '%s' "$df_line" \
  | "$SED_BIN" -E 's/^([^[:space:]]+[[:space:]]+){5}//' \
  | "$SED_BIN" 's/^[[:space:]]*//; s/[[:space:]]*$//')
# Strip trailing slash except for root "/"
fs_mount=$(printf '%s' "$fs_mount_raw" | "$SED_BIN" 's#/*$##')
[ "$fs_mount" = "" ] && [ -n "$fs_mount_raw" ] && fs_mount="/"

# -----------------------------------------------------------------------
# Validate: every surface must be non-empty. No partial output on failure.
# (Preserved unchanged from v1; RT-J3-O1's stricter empty/null handling is
# a receipt-schema/validation-rule extension -- missing_receipt_field_v2 in
# repair-package-v6.yaml -- not a change to this script's own emit-time
# non-empty check, which already fails closed on emptiness.)
# -----------------------------------------------------------------------
missing=""
[ -n "$host_id" ]    || missing="$missing host_id"
[ -n "$fs_dev" ]     || missing="$missing filesystem_id"
[ -n "$fs_mount" ]   || missing="$missing filesystem_mount"

if [ -n "$missing" ]; then
  printf 'emit_host_binding_v2: ERROR: unreadable or empty host identity surface(s):%s\n' \
    "$missing" >&2
  exit 1
fi

# --- emitted_at: UTC timestamp (absolute path, no PATH lookup) ---
emitted_at=$("$DATE_BIN" -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null) || {
  printf 'emit_host_binding_v2: ERROR: date surface unreadable\n' >&2
  exit 1
}

# -----------------------------------------------------------------------
# Emit the JSON block. Minimal defensive escaping of backslash and
# double-quote; the host identity surfaces are simple strings but we do
# not assume that.
# -----------------------------------------------------------------------
esc() {
  printf '%s' "$1" | "$SED_BIN" 's/\\/\\\\/g; s/"/\\"/g'
}

printf '{"schema":"crypto.autoresearch.runtime_session_receipt.v2","host_binding":{"host_id":"%s","filesystem_id":"%s","filesystem_mount":"%s"},"emitted_at":"%s"}\n' \
  "$(esc "$host_id")" \
  "$(esc "$fs_dev")" \
  "$(esc "$fs_mount")" \
  "$emitted_at"
