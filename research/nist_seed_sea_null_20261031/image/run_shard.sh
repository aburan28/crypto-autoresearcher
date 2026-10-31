#!/usr/bin/env bash
# Run WORKERS parallel GP shards for one field, then upload rows and a receipt
# to $ISOLAB_RESULTS_URI (set by the lab for each Job).
#   run_shard.sh FIELD P_HEX SEED_BASE PER_WORKER WORKERS
set -euo pipefail
field=$1 p_hex=$2 seed_base=$3 per_worker=$4 workers=$5
work=${TMPDIR:-/tmp}/sea-null-$field-$seed_base
mkdir -p "$work"
start=$(date -u +%s)
pids=()
for w in $(seq 0 $((workers - 1))); do
  FIELD=$field P_HEX=$p_hex SEED=$((seed_base + w)) TARGET=$per_worker \
    OUT=$work/rows-$((seed_base + w)).jsonl \
    gp -q -f -D datadir=/usr/share/pari /opt/sea-null/sea_null_shard.gp \
    > "$work/gp-$((seed_base + w)).log" 2>&1 &
  pids+=($!)
done
status=0
for pid in "${pids[@]}"; do wait "$pid" || status=1; done
end=$(date -u +%s)
{
  printf '{"field":"%s","seed_base":%s,"per_worker":%s,"workers":%s,' "$field" "$seed_base" "$per_worker" "$workers"
  printf '"exit":%s,"wall_seconds":%s,' "$status" "$((end - start))"
  printf '"gp_version":"%s",' "$(echo 'print(version())' | gp -q -f)"
  printf '"worker_sha256":"%s",' "$(sha256sum /opt/sea-null/sea_null_shard.gp | cut -d' ' -f1)"
  printf '"pod":"%s"}\n' "${HOSTNAME:-unknown}"
} > "$work/receipt.json"
sha256sum "$work"/*.jsonl "$work"/*.log "$work/receipt.json" > "$work/manifest.sha256"
aws s3 cp --recursive "$work" "${ISOLAB_RESULTS_URI%/}/sea-null/$field/$seed_base/"
exit "$status"
