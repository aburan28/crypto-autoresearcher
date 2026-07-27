#!/usr/bin/env bash
# Cluster prerequisites for multi-node Kimi-K3 serving on EKS.
#   ./install-prereqs.sh
set -euo pipefail

echo "==> NVIDIA device plugin"
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.17.0/deployments/static/nvidia-device-plugin.yml

echo "==> EFA device plugin (skip if installed as an EKS addon in cluster.yaml)"
kubectl apply -f https://raw.githubusercontent.com/aws-samples/aws-efa-eks/main/manifest/efa-k8s-device-plugin.yml \
    || echo "    already present via addon"

echo "==> LeaderWorkerSet controller"
kubectl apply --server-side -f \
    https://github.com/kubernetes-sigs/lws/releases/latest/download/manifests.yaml
kubectl -n lws-system wait deploy/lws-controller-manager \
    --for=condition=Available --timeout=300s

echo "==> FSx for Lustre CSI driver"
kubectl apply -k \
    "github.com/kubernetes-sigs/aws-fsx-csi-driver/deploy/kubernetes/overlays/stable/?ref=release-1.9"

echo "==> Scripts ConfigMap (nccl-efa-env.sh is sourced by every vLLM container;"
echo "    verify-efa.sh is invoked by the nccl-test Job)"
kubectl create configmap kimi-k3-scripts \
    --from-file="$(dirname "$0")/nccl-efa-env.sh" \
    --from-file="$(dirname "$0")/verify-efa.sh" \
    --dry-run=client -o yaml | kubectl apply -f -

cat <<'EOF'

==> Remaining manual steps:

  1. Create the FSx for Lustre filesystem with an S3 data repository association
     pointing at the prefix used by stage-weights.sh, then create a PV/PVC named
     'fsx-models'. The LWS manifests mount that claim name.

  2. Build and push the EFA-enabled vLLM image to ECR. It needs:
       - a vLLM build with FlashKDA + SiTU MXFP4 MoE support for Kimi-K3
       - aws-ofi-nccl at /opt/amazon/ofi-nccl/lib
       - nccl-tests at /opt/nccl-tests/build (for verify-efa.sh)
     Then replace <ACCOUNT_ID> and <REGION> in eks/*.yaml.

  3. Run verify-efa.sh before deploying the model. Do not skip this.
EOF
