#!/usr/bin/env bash
# Helpers for the CADO EC2 spot workers.
#   ./scripts/cado_ec2.sh status|log|log-client|ssh|ssh-client|pull|terminate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
REGION=us-west-2
KEY="${CADO_EC2_KEY:-$HOME/.ssh/finetune-spot-us-west-2.pem}"
IID_FILE="$ROOT/.cado_ec2_instance_id"
IP_FILE="$ROOT/.cado_ec2_public_ip"
CLIENT_IID_FILE="$ROOT/.cado_ec2_client_c8i_id"
CLIENT_IP_FILE="$ROOT/.cado_ec2_client_c8i_ip"

iid() { cat "$IID_FILE"; }
ip() {
  if [[ -f "$IP_FILE" ]]; then cat "$IP_FILE"
  else
    aws ec2 describe-instances --region "$REGION" --instance-ids "$(iid)" \
      --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
  fi
}
client_iid() { cat "$CLIENT_IID_FILE"; }
client_ip() {
  if [[ -f "$CLIENT_IP_FILE" ]]; then cat "$CLIENT_IP_FILE"
  else
    aws ec2 describe-instances --region "$REGION" --instance-ids "$(client_iid)" \
      --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
  fi
}

cmd="${1:-status}"
case "$cmd" in
  status)
    ids=("$(iid)")
    if [[ -f "$ROOT/.cado_ec2_all_client_ids" ]]; then
      while read -r cid; do [[ -n "$cid" ]] && ids+=("$cid"); done < "$ROOT/.cado_ec2_all_client_ids"
    elif [[ -f "$CLIENT_IID_FILE" ]]; then
      ids+=("$(client_iid)")
    fi
    mapfile -t ids < <(printf '%s\n' "${ids[@]}" | awk 'NF && !seen[$0]++')
    aws ec2 describe-instances --region "$REGION" --instance-ids "${ids[@]}" \
      --query 'Reservations[].Instances[].[Tags[?Key==`Name`].Value|[0],InstanceId,InstanceType,State.Name,PublicIpAddress]' \
      --output table
    ;;
  log)
    ssh -o StrictHostKeyChecking=accept-new -i "$KEY" "ubuntu@$(ip)" \
      'sudo tail -n 80 -f /opt/cado-nist-open/progress.log'
    ;;
  log-client)
    ssh -o StrictHostKeyChecking=accept-new -i "$KEY" "ubuntu@$(client_ip)" \
      'sudo tail -n 80 -f /var/log/cado-client-setup.log'
    ;;
  ssh)
    exec ssh -o StrictHostKeyChecking=accept-new -i "$KEY" "ubuntu@$(ip)"
    ;;
  ssh-client)
    exec ssh -o StrictHostKeyChecking=accept-new -i "$KEY" "ubuntu@$(client_ip)"
    ;;
  pull)
    mkdir -p "$HOME/cado-nist-open-ec2"
    rsync -avz -e "ssh -i $KEY -o StrictHostKeyChecking=accept-new" \
      "ubuntu@$(ip):/opt/cado-nist-open/" "$HOME/cado-nist-open-ec2/"
    ;;
  backup|s3-backup)
    shift
    exec "$ROOT/cado_ec2_s3_backup.sh" "${@:-sync}"
    ;;
  terminate)
    ids=("$(iid)")
    if [[ -f "$ROOT/.cado_ec2_all_client_ids" ]]; then
      while read -r cid; do [[ -n "$cid" ]] && ids+=("$cid"); done < "$ROOT/.cado_ec2_all_client_ids"
    elif [[ -f "$CLIENT_IID_FILE" ]]; then
      ids+=("$(client_iid)")
    fi
    # unique
    mapfile -t ids < <(printf '%s\n' "${ids[@]}" | awk 'NF && !seen[$0]++')
    aws ec2 terminate-instances --region "$REGION" --instance-ids "${ids[@]}"
    echo "terminating ${ids[*]}"
    ;;
  *)
    echo "usage: $0 status|log|log-client|ssh|ssh-client|pull|backup|terminate" >&2
    exit 1
    ;;
esac
