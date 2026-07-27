#!/usr/bin/env bash
# NCCL + EFA environment for multi-node Kimi-K3 serving.
# Source this before launching vLLM: `source /opt/scripts/nccl-efa-env.sh`
#
# The failure mode this guards against: without the aws-ofi-nccl plugin on the
# library path, NCCL silently falls back to TCP sockets. Nothing errors -- the
# deployment just runs roughly an order of magnitude slower, and for a 896-expert
# MoE whose critical path is all-to-all, that is the difference between usable and
# useless. Always run verify-efa.sh before concluding anything about performance.

# libfabric: use the EFA provider and let NCCL do GPU-direct RDMA.
export FI_PROVIDER=efa
export FI_EFA_USE_DEVICE_RDMA=1
export FI_EFA_FORK_SAFE=1

# aws-ofi-nccl plugin must be visible to NCCL.
export LD_LIBRARY_PATH="/opt/amazon/ofi-nccl/lib:/opt/amazon/efa/lib:${LD_LIBRARY_PATH:-}"

# Bind NCCL to the EFA interfaces, not the pod's default eth0.
export NCCL_SOCKET_IFNAME="${NCCL_SOCKET_IFNAME:-eth}"
export NCCL_PROTO=simple

# Blackwell/Hopper multi-node: keep NCCL from disabling GDR on the P2P path.
export NCCL_NET_GDR_LEVEL=PIX

# Raise this to INFO once to confirm the EFA provider is selected, then lower it --
# NCCL debug output at scale is voluminous.
export NCCL_DEBUG="${NCCL_DEBUG:-WARN}"
export NCCL_DEBUG_SUBSYS="${NCCL_DEBUG_SUBSYS:-INIT,NET}"

# vLLM: NCCL is the collective backend for EP all-to-all.
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export VLLM_USE_V1=1

# Load 1.5 TB from FSx without re-verifying checksums on every start.
export SAFETENSORS_FAST_GPU=1
export HF_HUB_DISABLE_TELEMETRY=1

echo "[nccl-efa-env] FI_PROVIDER=${FI_PROVIDER} NCCL_SOCKET_IFNAME=${NCCL_SOCKET_IFNAME}"
if ! ls /opt/amazon/ofi-nccl/lib/libnccl-net*.so >/dev/null 2>&1; then
    echo "[nccl-efa-env] WARNING: aws-ofi-nccl plugin not found." >&2
    echo "[nccl-efa-env] NCCL will fall back to TCP and performance will collapse." >&2
fi
