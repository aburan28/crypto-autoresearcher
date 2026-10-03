#!/usr/bin/env bash
# Helpers for the ECC2K-130 Pollard-rho DP walker host.
# Despite the "gpu" name (user request / state prefix), the live walker is
# AArch64/PMULL-only — this host is intentionally Graviton, not GPU.
#
#   ./scripts/rho_gpu_ec2.sh status|ssh|log|stop|terminate
#
# State (gitignored): scripts/.rho_gpu_*
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
REGION="$(cat "$ROOT/.rho_gpu_region" 2>/dev/null || echo us-west-2)"
# Prefer meow34 when present; fall back to finetune-spot (prior host key).
if [[ -n "${RHO_GPU_EC2_KEY:-}" ]]; then
  KEY="$RHO_GPU_EC2_KEY"
elif [[ -f "$HOME/.ssh/meow34.pem" ]]; then
  KEY="$HOME/.ssh/meow34.pem"
else
  KEY="${CADO_EC2_KEY:-$HOME/.ssh/finetune-spot-us-west-2.pem}"
fi
IID_FILE="$ROOT/.rho_gpu_instance_id"
IP_FILE="$ROOT/.rho_gpu_public_ip"

die() { echo "error: $*" >&2; exit 1; }

iid() { [[ -f "$IID_FILE" ]] || die "missing $IID_FILE"; cat "$IID_FILE"; }
ip() {
  if [[ -f "$IP_FILE" ]]; then cat "$IP_FILE"
  else
    aws ec2 describe-instances --region "$REGION" --instance-ids "$(iid)" \
      --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
  fi
}

cmd="${1:-status}"
case "$cmd" in
  status)
    aws ec2 describe-instances --region "$REGION" --instance-ids "$(iid)" \
      --query 'Reservations[].Instances[].[Tags[?Key==`Name`].Value|[0],InstanceId,InstanceType,Architecture,State.Name,PublicIpAddress,PrivateIpAddress,Placement.AvailabilityZone]' \
      --output table
    if [[ -f "$ROOT/.rho_gpu_status.json" ]]; then
      echo "--- local status ---"
      cat "$ROOT/.rho_gpu_status.json"
    fi
    if [[ -f "$ROOT/.rho_gpu_spot_price" ]]; then
      echo "spot_price_usd_hr≈$(cat "$ROOT/.rho_gpu_spot_price")"
    fi
    ;;
  ssh)
    shift || true
    if [[ $# -gt 0 ]]; then
      exec ssh -o StrictHostKeyChecking=accept-new -i "$KEY" "ubuntu@$(ip)" "$@"
    else
      exec ssh -o StrictHostKeyChecking=accept-new -i "$KEY" "ubuntu@$(ip)"
    fi
    ;;
  log)
    ssh -o StrictHostKeyChecking=accept-new -i "$KEY" "ubuntu@$(ip)" \
      'sudo tail -n 100 -f /opt/rho-ecc2k/logs/*.log /var/log/rho-ecc2k-setup.log 2>/dev/null || true'
    ;;
  progress)
    ssh -o StrictHostKeyChecking=accept-new -i "$KEY" "ubuntu@$(ip)" \
      '/opt/rho-ecc2k/progress.sh'
    ;;
  stop|terminate)
    aws ec2 terminate-instances --region "$REGION" --instance-ids "$(iid)"
    echo "terminating $(iid) (RDS and other instances untouched)"
    ;;
  *)
    echo "usage: $0 status|ssh|log|progress|stop|terminate" >&2
    exit 1
    ;;
esac
