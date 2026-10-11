#!/usr/bin/env bash
# Control helper for the (terminated) g7e.2xlarge attempt.
#
#   ./scripts/rho_g7e_ec2.sh status|ssh|log|stop|terminate
#
# State (gitignored): scripts/.rho_g7e_*
#
# NOTE: g7e.2xlarge is x86_64 and was launched in us-east-1 — it cannot run the
# Type-II walker natively and cannot reach private RDS in us-west-2. It was
# terminated; use ./scripts/rho_gpu_ec2.sh for the live Graviton walker.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
REGION="$(cat "$ROOT/.rho_g7e_region" 2>/dev/null || echo us-east-1)"
KEY="${RHO_G7E_EC2_KEY:-$HOME/.ssh/meow34.pem}"
IID_FILE="$ROOT/.rho_g7e_instance_id"
IP_FILE="$ROOT/.rho_g7e_public_ip"

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
      --output table || true
    if [[ -f "$ROOT/.rho_g7e_status.json" ]]; then
      echo "--- local status ---"
      cat "$ROOT/.rho_g7e_status.json"
    fi
    echo "NOTE: prefer ./scripts/rho_gpu_ec2.sh (Graviton walker in us-west-2)"
    ;;
  ssh)
    die "g7e host terminated; use ./scripts/rho_gpu_ec2.sh ssh"
    ;;
  log)
    die "g7e host terminated; use ./scripts/rho_gpu_ec2.sh log"
    ;;
  stop|terminate)
    aws ec2 terminate-instances --region "$REGION" --instance-ids "$(iid)" || true
    echo "terminate requested for $(iid) (RDS untouched)"
    ;;
  *)
    echo "usage: $0 status|ssh|log|stop|terminate" >&2
    exit 1
    ;;
esac
