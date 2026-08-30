#!/bin/sh
# emit_host_binding.sh
#
# Emit a host_binding JSON block from the host's own identity surfaces.
#
# POSIX sh. No network access. No repository writes. Reads ONLY the host's
# own identity surfaces (hostname; the filesystem device and mount point of
# the working directory the script is run from).
#
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
# emitted.
#
# Host identity surfaces and their platform commands:
#
#   host_id:
#     macOS : `hostname` (returns the system hostname, e.g.
#             "Adams-MacBook-Pro.local"; equivalent to the HostName /
#             LocalHostName / ComputerName surface exposed by scutil).
#     Linux : `hostname` (from hostname(1), or read from
#             /proc/sys/kernel/hostname).
#     Normalization (per v5 rule): trimmed, case-preserved.
#
#   filesystem_id:
#     macOS : `df -P .` first column (the device path, e.g. "/dev/disk5s1").
#     Linux : `df -P .` first column, or `findmnt -no SOURCE .`.
#     Normalization (per v5 rule): lowercase, trimmed, no trailing slash.
#
#   filesystem_mount:
#     macOS : `df -P .` last column(s) (the mount point, e.g.
#             "/Volumes/SSD990").
#     Linux : `df -P .` last column(s), or `findmnt -no TARGET .`.
#     Normalization (per v5 rule): absolute POSIX path, trailing slash
#     stripped except root "/".
#
# The -P (POSIX) flag on df guarantees one line per filesystem with the
# mount point in the trailing field(s), preventing line-wrap on long
# device names. Mount points may contain spaces; the extraction below
# takes everything after the first five df fields to preserve that.

set -u

# -----------------------------------------------------------------------
# Capture all three surfaces BEFORE emitting anything. If any surface is
# unreadable, we exit with no stdout output.
# -----------------------------------------------------------------------

# --- host_id: hostname surface ---
host_id_raw=$(hostname 2>/dev/null) || host_id_raw=""
host_id=$(printf '%s' "$host_id_raw" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')

# --- df line for the working directory ---
df_line=$(df -P . 2>/dev/null | tail -1) || df_line=""

# --- filesystem_id: device path (first field of df output) ---
fs_dev_raw=$(printf '%s' "$df_line" | awk '{print $1}')
# Normalize: trim, strip trailing slash, lowercase
fs_dev=$(printf '%s' "$fs_dev_raw" \
  | sed 's/^[[:space:]]*//; s/[[:space:]]*$//; s#/$##' \
  | tr 'A-Z' 'a-z')

# --- filesystem_mount: mount point (everything after the first 5 fields) ---
# df -P POSIX format: Filesystem 512-blocks Used Available Capacity Mounted-on
# The mount point is fields 6..NF and may contain spaces.
fs_mount_raw=$(printf '%s' "$df_line" \
  | sed -E 's/^([^[:space:]]+[[:space:]]+){5}//' \
  | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
# Strip trailing slash except for root "/"
fs_mount=$(printf '%s' "$fs_mount_raw" | sed 's#/*$##')
[ "$fs_mount" = "" ] && fs_mount="/"

# -----------------------------------------------------------------------
# Validate: every surface must be non-empty. No partial output on failure.
# -----------------------------------------------------------------------
missing=""
[ -n "$host_id" ]    || missing="$missing host_id"
[ -n "$fs_dev" ]     || missing="$missing filesystem_id"
[ -n "$fs_mount" ]   || missing="$missing filesystem_mount"

if [ -n "$missing" ]; then
  printf 'emit_host_binding: ERROR: unreadable or empty host identity surface(s):%s\n' \
    "$missing" >&2
  exit 1
fi

# --- emitted_at: UTC timestamp ---
emitted_at=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null) || {
  printf 'emit_host_binding: ERROR: date surface unreadable\n' >&2
  exit 1
}

# -----------------------------------------------------------------------
# Emit the JSON block. Minimal defensive escaping of backslash and
# double-quote; the host identity surfaces are simple strings but we do
# not assume that.
# -----------------------------------------------------------------------
esc() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

printf '{"schema":"crypto.autoresearch.runtime_session_receipt.v2","host_binding":{"host_id":"%s","filesystem_id":"%s","filesystem_mount":"%s"},"emitted_at":"%s"}\n' \
  "$(esc "$host_id")" \
  "$(esc "$fs_dev")" \
  "$(esc "$fs_mount")" \
  "$emitted_at"
