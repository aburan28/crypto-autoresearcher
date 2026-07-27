#!/usr/bin/env bash
# Prove the fabric works BEFORE spending an hour loading 1.5 TB of weights.
#
#   ./verify-efa.sh [num_nodes] [gpus_per_node]
#
# Run this inside the same container image and pod spec the model will use. If
# all_to_all bandwidth is bad here, every latency and throughput number you measure
# afterwards is meaningless -- and the usual cause is a silent NCCL fallback to TCP,
# which produces no error at all.
set -euo pipefail

NODES="${1:-8}"
GPUS_PER_NODE="${2:-8}"
NP=$(( NODES * GPUS_PER_NODE ))

source "$(dirname "$0")/nccl-efa-env.sh"

echo "==> EFA devices visible to this container"
fi_info -p efa 2>/dev/null | grep -E 'provider|domain' | head -20 || {
    echo "fi_info found no EFA provider. The EFA device plugin is not wired up." >&2
    exit 1
}

echo
echo "==> Confirming NCCL selects the EFA plugin (expect 'Using network AWS Libfabric')"
NCCL_DEBUG=INFO mpirun -np 2 -N 1 \
    --allow-run-as-root --bind-to none \
    /opt/nccl-tests/build/all_reduce_perf -b 8 -e 8 -f 2 -g 1 2>&1 |
    grep -E 'NET/OFI|Using network|NCCL INFO Bootstrap' | head -5 || true

# all_to_all is the collective that matters for a 896-expert MoE. A good all_reduce
# number with a bad all_to_all number still means a bad K3 deployment.
echo
echo "==> all_to_all across ${NP} ranks (${NODES} nodes x ${GPUS_PER_NODE} GPUs)"
mpirun -np "${NP}" -N "${GPUS_PER_NODE}" \
    --allow-run-as-root --bind-to none \
    -x FI_PROVIDER -x FI_EFA_USE_DEVICE_RDMA -x LD_LIBRARY_PATH \
    -x NCCL_SOCKET_IFNAME -x NCCL_NET_GDR_LEVEL \
    /opt/nccl-tests/build/alltoall_perf -b 8M -e 2G -f 2 -g 1 | tee /tmp/alltoall.log

echo
echo "==> Peak busbw"
awk '/^ *[0-9]/ {if ($NF+0 > max) max=$NF+0} END {printf "    %.1f GB/s\n", max}' /tmp/alltoall.log

cat <<'EOF'

Interpreting the result:
  - Within one NVLink domain (GB200 NVL72), expect NVLink-class bandwidth --
    hundreds of GB/s. This is why the UltraServer is the preferred shape for K3.
  - Across nodes over 3.2 Tbps EFA, expect roughly an order of magnitude less.
  - Single-digit GB/s means NCCL fell back to TCP. Fix that before going further:
    check that libnccl-net.so from aws-ofi-nccl is on LD_LIBRARY_PATH, that the pod
    requests vpc.amazonaws.com/efa, and that all nodes are in one AZ and one
    cluster placement group.
EOF
