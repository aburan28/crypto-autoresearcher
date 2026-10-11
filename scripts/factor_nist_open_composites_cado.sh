#!/usr/bin/env bash
# Factor incomplete NIST prime-field curve parameters with CADO-NFS.
#
# Targets: twist cofactors and Cheon n±1 remainders (and P-521 CM disc)
# that are still composite after NIST docs + small trial division.
# Skips the P-521 twist 461-bit piece (probable prime, not a GNFS target).
#
# Usage:
#   ./scripts/factor_nist_open_composites_cado.sh              # list targets
#   ./scripts/factor_nist_open_composites_cado.sh list
#   ./scripts/factor_nist_open_composites_cado.sh p192-twist
#   ./scripts/factor_nist_open_composites_cado.sh -v p192-nm1    # COMMAND log
#   ./scripts/factor_nist_open_composites_cado.sh -vv all-easy   # DEBUG log
#   ./scripts/factor_nist_open_composites_cado.sh all
#
# Env overrides:
#   CADO_NFS_PY      path to cado-nfs.py
#   CADO_PARAMS      directory with params.c*
#   CADO_WORKDIR     parent work directory
#   CADO_THREADS     thread count (default: hw.logicalcpu)
#   CADO_SCREENLOG   INFO | COMMAND | DEBUG  (default: INFO; -v/-vv override)
#   CADO_FILELOG     same levels for the workdir log file (default: DEBUG)
#   CADO_DEBUG=1     keep workdir artifacts even on success
#   CADO_VERBOSEPARAM=1  dump parameter parsing

set -euo pipefail

CADO_NFS_PY="${CADO_NFS_PY:-/Volumes/SSD990/cado-nfs/build/test/cado-nfs.py}"
CADO_PARAMS="${CADO_PARAMS:-/Volumes/SSD990/cado-nfs/parameters/factor}"
CADO_WORKDIR="${CADO_WORKDIR:-$HOME/cado-nist-open}"
CADO_SCREENLOG="${CADO_SCREENLOG:-INFO}"
CADO_FILELOG="${CADO_FILELOG:-DEBUG}"
if [[ -z "${CADO_THREADS:-}" ]]; then
  if command -v sysctl >/dev/null 2>&1; then
    CADO_THREADS="$(sysctl -n hw.logicalcpu 2>/dev/null || sysctl -n hw.ncpu)"
  else
    CADO_THREADS="$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4)"
  fi
fi

# name|decimal_N|approx_digits|notes
# Ordered easiest → hardest.
TARGETS=(
  'p192-twist|272917466755942641905903887966924948626114027286861201673|57|P-192 twist / 23'
  'p192-nm1|32843772160876312075323301711888127949807423467888459|53|P-192 n-1 rem (trial <1e7)'
  'p192-np1|25516673721084068145673940744618126072224368996678220667|56|P-192 n+1 rem (trial <1e7)'
  'p224-np1|101353182959212931558898552958720398272397773362497713239408730707|65|P-224 n+1 rem (trial <1e7)'
  'p256-np1|6162431570535191525422961519393697367216442534546873887302940876054737203|73|P-256 n+1 rem (trial <1e7)'
  'p384-np1|1557469607425165783497727874272260515075606922531352427779657307711218862633639645235933417854787936152469367|109|P-384 n+1 rem (trial <1e7)'
  'p384-nm1|3436421262549666772394822963556917303774615320989486016740528979559363282671660872963453367185792335038761002437|112|P-384 n-1 rem (trial <1e7)'
  'p521-cmdisc|5405277566604743401278975911602132324296054382763978192866815683124167925520445433545449676793281443032921640112007528563470322271623658275613707476827805679|157|P-521 CM disc abs(D)/5 cofactor'
  'p521-nm1|8686010947518764000493340485319251269434254259172527620677065040319390409295451248399471796941544773224489068299950553585175735406616468529993634152791|151|P-521 n-1 rem (trial <1e7)'
  'p521-np1|15255105911401354922182001775736429371709856222540678687543252131523429296439234209433461658518260438962142214158585158030810596916534178534161797539348901|155|P-521 n+1 rem (trial <1e7)'
)

EASY_NAMES=(p192-twist p192-nm1 p192-np1 p224-np1 p256-np1)

die() { echo "error: $*" >&2; exit 1; }

params_for_digits() {
  local d="$1"
  # Snap up to nearest available cado params.cNNN file.
  local candidates=(60 65 70 75 80 85 90 95 100 105 110 115 120 125 130 135 140 145 150 155 160 165 170 175 180 185 190 195 200)
  local best=""
  local c
  for c in "${candidates[@]}"; do
    if (( c >= d )) && [[ -f "${CADO_PARAMS}/params.c${c}" ]]; then
      best="$c"
      break
    fi
  done
  if [[ -z "$best" ]]; then
    # fall back to largest available ≤ or just c160+
    for c in 200 195 190 185 180 175 170 165 160 155 150; do
      if [[ -f "${CADO_PARAMS}/params.c${c}" ]]; then
        best="$c"
        break
      fi
    done
  fi
  [[ -n "$best" ]] || die "no params file for ${d} digits under ${CADO_PARAMS}"
  echo "${CADO_PARAMS}/params.c${best}"
}

lookup_target() {
  local want="$1"
  local row name
  for row in "${TARGETS[@]}"; do
    name="${row%%|*}"
    if [[ "$name" == "$want" ]]; then
      echo "$row"
      return 0
    fi
  done
  return 1
}

list_targets() {
  printf '%-14s %6s  %s\n' 'NAME' 'DIGITS' 'NOTES'
  printf '%-14s %6s  %s\n' '----' '------' '-----'
  local row name rest digits notes
  for row in "${TARGETS[@]}"; do
    name="${row%%|*}"
    rest="${row#*|}"
    # N|digits|notes
    digits="$(echo "$rest" | cut -d'|' -f2)"
    notes="$(echo "$rest" | cut -d'|' -f3)"
    printf '%-14s %6s  %s\n' "$name" "$digits" "$notes"
  done
  echo
  echo "Skipped on purpose: p521-twist 461-bit cofactor (PRP, not composite)."
  echo "Workdir parent: ${CADO_WORKDIR}"
  echo "cado-nfs.py:    ${CADO_NFS_PY}"
  echo "threads:        ${CADO_THREADS}"
}

check_prereqs() {
  [[ -x "${CADO_NFS_PY}" || -f "${CADO_NFS_PY}" ]] || die "cado-nfs.py not found: ${CADO_NFS_PY}"
  python3 -c 'import flask' 2>/dev/null || die "python3 module flask missing (pip3 install flask)"
  mkdir -p "${CADO_WORKDIR}"
}

run_one() {
  local name="$1"
  local row N digits notes params work
  row="$(lookup_target "$name")" || die "unknown target: ${name} (try: list)"
  N="$(echo "$row" | cut -d'|' -f2)"
  digits="$(echo "$row" | cut -d'|' -f3)"
  notes="$(echo "$row" | cut -d'|' -f4)"
  params="$(params_for_digits "$digits")"
  work="${CADO_WORKDIR}/${name}"

  echo "================================================================"
  echo "target:  ${name}"
  echo "notes:   ${notes}"
  echo "N:       ${N}"
  echo "digits:  ${digits}"
  echo "params:  ${params}"
  echo "workdir: ${work}"
  echo "threads: ${CADO_THREADS}"
  echo "================================================================"

  mkdir -p "${work}"
  # --parameters / --workdir / --server-threads are flags, NOT key=value
  # positionals. Passing parameters=... makes CADO ignore the file and
  # auto-pick params.cDD by digit count (fails below c60).
  local exec_cado=(
    python3 "${CADO_NFS_PY}"
    --parameters "${params}"
    --workdir "${work}"
    --server-threads "${CADO_THREADS}"
    --screenlog "${CADO_SCREENLOG}"
    --filelog "${CADO_FILELOG}"
  )
  if [[ "${CADO_VERBOSEPARAM:-0}" == "1" ]]; then
    exec_cado+=(--verboseparam)
  fi
  if [[ -n "${CADO_DEBUG:-}" ]]; then
    export CADO_DEBUG=1
  fi
  exec_cado+=(
    "${N}"
    "server.whitelist=0.0.0.0/0"
  )
  echo "+ ${exec_cado[*]}"
  echo "screenlog=${CADO_SCREENLOG} filelog=${CADO_FILELOG}"
  "${exec_cado[@]}"
}

already_factored() {
  local work="$1"
  # CADO writes factors to stdout; also leaves *.factors / Factor* in workdir
  # on many versions. Treat prior success if a non-empty factors artifact exists.
  [[ -d "$work" ]] || return 1
  local f
  for f in "${work}"/*.factors "${work}"/factors.* "${work}"/*/factors; do
    [[ -f "$f" && -s "$f" ]] && return 0
  done
  # Resume-friendly: if user saved stdout
  [[ -f "${work}/FACTORS.txt" && -s "${work}/FACTORS.txt" ]] && return 0
  return 1
}

run_many() {
  local names=("$@")
  local n rc=0
  for n in "${names[@]}"; do
    local row work
    row="$(lookup_target "$n")" || { echo "skip unknown $n"; rc=1; continue; }
    work="${CADO_WORKDIR}/${n}"
    if already_factored "$work"; then
      echo "skip ${n}: already has factors under ${work}"
      continue
    fi
    if ! run_one "$n"; then
      echo "FAILED: ${n}" >&2
      rc=1
      # continue batch; do not abort remaining targets
    fi
  done
  return "$rc"
}

main() {
  # Leading -v / -vv / --verbose before the target.
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -v|--verbose)
        CADO_SCREENLOG=COMMAND
        shift
        ;;
      -vv|--debug)
        CADO_SCREENLOG=DEBUG
        CADO_FILELOG=DEBUG
        CADO_VERBOSEPARAM=1
        shift
        ;;
      -vvv)
        CADO_SCREENLOG=DEBUG
        CADO_FILELOG=DEBUG
        CADO_VERBOSEPARAM=1
        CADO_DEBUG=1
        shift
        ;;
      *)
        break
        ;;
    esac
  done

  local cmd="${1:-list}"
  case "$cmd" in
    list|-h|--help|help)
      list_targets
      echo
      echo "Verbosity: -v (COMMAND), -vv (DEBUG+param dump), -vvv (also CADO_DEBUG=1)"
      echo "Or: CADO_SCREENLOG=DEBUG CADO_FILELOG=DEBUG ./scripts/... p192-nm1"
      ;;
    all-easy)
      check_prereqs
      run_many "${EASY_NAMES[@]}"
      ;;
    all)
      check_prereqs
      local names=()
      local row
      for row in "${TARGETS[@]}"; do
        names+=("${row%%|*}")
      done
      run_many "${names[@]}"
      ;;
    *)
      check_prereqs
      run_one "$cmd"
      ;;
  esac
}

main "$@"
