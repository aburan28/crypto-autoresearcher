#!/usr/bin/env bash
# Backup CADO NIST factorization workdirs from the EC2 server to S3.
#
# The spot server has no instance profile. This script can:
#   - one-shot sync using short-lived creds over SSH
#   - install automatic backups on the instance (systemd timer) + refresh
#     temporary credentials from your laptop (launchd)
#
# Usage:
#   ./scripts/cado_ec2_s3_backup.sh sync
#   ./scripts/cado_ec2_s3_backup.sh snapshot
#   ./scripts/cado_ec2_s3_backup.sh status
#   ./scripts/cado_ec2_s3_backup.sh pull-logs
#   ./scripts/cado_ec2_s3_backup.sh install-auto   # enable automatic backups
#   ./scripts/cado_ec2_s3_backup.sh refresh-creds  # push fresh temp creds to EC2
#   ./scripts/cado_ec2_s3_backup.sh uninstall-auto
#
# Env:
#   CADO_S3_BUCKET   default: crypto-autoresearcher
#   CADO_S3_PREFIX   default: cado-nist-open
#   CADO_EC2_KEY     default: ~/.ssh/finetune-spot-us-west-2.pem
#   CADO_REMOTE_DIR  default: /opt/cado-nist-open
#   AWS_REGION       default: us-west-2
#   CADO_BACKUP_EVERY_MIN  default: 30
#   CADO_EC2_HOST    optional override

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
REGION="${AWS_REGION:-us-west-2}"
BUCKET="${CADO_S3_BUCKET:-crypto-autoresearcher}"
PREFIX="${CADO_S3_PREFIX:-cado-nist-open}"
REMOTE_DIR="${CADO_REMOTE_DIR:-/opt/cado-nist-open}"
KEY="${CADO_EC2_KEY:-$HOME/.ssh/finetune-spot-us-west-2.pem}"
BACKUP_EVERY_MIN="${CADO_BACKUP_EVERY_MIN:-30}"
IID_FILE="$ROOT/.cado_ec2_instance_id"
IP_FILE="$ROOT/.cado_ec2_public_ip"
LAUNCH_AGENT="$HOME/Library/LaunchAgents/com.adamburan.cado-s3-backup.plist"
LABEL="com.adamburan.cado-s3-backup"

die() { echo "error: $*" >&2; exit 1; }

remote_host() {
  if [[ -n "${CADO_EC2_HOST:-}" ]]; then echo "$CADO_EC2_HOST"; return; fi
  if [[ -f "$IP_FILE" ]]; then cat "$IP_FILE"; return; fi
  [[ -f "$IID_FILE" ]] || die "no host: set CADO_EC2_HOST or scripts/.cado_ec2_public_ip"
  aws ec2 describe-instances --region "$REGION" --instance-ids "$(cat "$IID_FILE")" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
}

ssh_base() {
  local host
  host="$(remote_host)"
  [[ -n "$host" && "$host" != "None" ]] || die "could not resolve EC2 host"
  echo ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=20 -i "$KEY" "ubuntu@${host}"
}

# Temporary session credentials only (never write long-lived AKIA keys to the server).
session_token_json() {
  aws sts get-session-token \
    --duration-seconds "${CADO_SESSION_SECONDS:-129600}" \
    --region "$REGION" \
    --output json
}

session_env_exports() {
  python3 - <<'PY'
import json, os, subprocess
region = os.environ.get("AWS_REGION", "us-west-2")
secs = os.environ.get("CADO_SESSION_SECONDS", "129600")
raw = subprocess.check_output(
    ["aws", "sts", "get-session-token", "--duration-seconds", secs,
     "--region", region, "--output", "json"],
    text=True,
)
c = json.loads(raw)["Credentials"]
print(f"export AWS_ACCESS_KEY_ID={c['AccessKeyId']}")
print(f"export AWS_SECRET_ACCESS_KEY={c['SecretAccessKey']}")
print(f"export AWS_SESSION_TOKEN={c['SessionToken']}")
print(f"export AWS_DEFAULT_REGION={region}")
print(f"export AWS_REGION={region}")
print(f"# expires {c['Expiration']}")
PY
}

ensure_aws_cli_remote() {
  local sshc
  sshc="$(ssh_base)"
  # shellcheck disable=SC2086
  $sshc 'command -v aws >/dev/null || {
    curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m).zip" -o /tmp/awscliv2.zip
    sudo apt-get update -y >/dev/null
    sudo apt-get install -y unzip >/dev/null
    unzip -qo /tmp/awscliv2.zip -d /tmp
    sudo /tmp/aws/install -u
  }
  aws --version' >/dev/null
}

remote_sync() {
  local dest="$1"
  local include_args="${2:-}"
  local sshc exports
  sshc="$(ssh_base)"
  ensure_aws_cli_remote
  exports="$(session_env_exports)"
  echo "→ sync ${REMOTE_DIR}/ → s3://${BUCKET}/${dest}/"
  # shellcheck disable=SC2086
  $sshc "sudo bash -s" <<EOF
set -euo pipefail
${exports}
command -v aws >/dev/null
aws s3 sync "${REMOTE_DIR}/" "s3://${BUCKET}/${dest}/" \\
  --region "${REGION}" \\
  --only-show-errors \\
  ${include_args} \\
  --exclude "*/client/**" \\
  --exclude "*/download/**" \\
  --exclude "*.sock"
echo "OK s3://${BUCKET}/${dest}/"
EOF
}

cmd_status() {
  local sshc
  sshc="$(ssh_base)"
  echo "host: $(remote_host)"
  # shellcheck disable=SC2086
  $sshc "sudo du -sh ${REMOTE_DIR} ${REMOTE_DIR}/* 2>/dev/null; echo '---'; sudo ls -la ${REMOTE_DIR}; echo '--- timer ---'; systemctl is-active cado-s3-backup.timer 2>/dev/null || echo 'timer: not installed'; systemctl list-timers cado-s3-backup.timer --no-pager 2>/dev/null || true"
  echo "--- S3 ---"
  aws s3 ls "s3://${BUCKET}/${PREFIX}/" --region "$REGION" 2>/dev/null || echo "(empty)"
  if [[ -f "$LAUNCH_AGENT" ]]; then
    echo "--- launchd ---"
    launchctl print "gui/$(id -u)/$LABEL" 2>/dev/null | head -20 || echo "plist present but not loaded"
  fi
}

cmd_sync() { remote_sync "${PREFIX}/live"; }

cmd_snapshot() {
  local ts
  ts="$(date -u +%Y%m%dT%H%M%SZ)"
  remote_sync "${PREFIX}/snapshots/${ts}"
  remote_sync "${PREFIX}/live"
  echo "snapshot: s3://${BUCKET}/${PREFIX}/snapshots/${ts}/"
}

cmd_pull_logs() {
  remote_sync "${PREFIX}/logs-live" \
    '--exclude "*" --include "progress.log" --include "*/run.log" --include "ALL_DONE" --include "*/FACTORS.txt"'
}

cmd_refresh_creds() {
  local sshc script
  sshc="$(ssh_base)"
  ensure_aws_cli_remote
  script="$(
    AWS_REGION="$REGION" CADO_SESSION_SECONDS="${CADO_SESSION_SECONDS:-129600}" python3 - <<'PY'
import json, os, subprocess
region = os.environ.get("AWS_REGION", "us-west-2")
secs = os.environ.get("CADO_SESSION_SECONDS", "129600")
raw = subprocess.check_output(
    ["aws", "sts", "get-session-token", "--duration-seconds", secs,
     "--region", region, "--output", "json"],
    text=True,
)
c = json.loads(raw)["Credentials"]
print(f"""set -euo pipefail
umask 077
mkdir -p /root/.aws
cat > /root/.aws/credentials <<'EOF'
[default]
aws_access_key_id = {c['AccessKeyId']}
aws_secret_access_key = {c['SecretAccessKey']}
aws_session_token = {c['SessionToken']}
EOF
cat > /root/.aws/config <<'EOF'
[default]
region = {region}
output = json
EOF
chmod 600 /root/.aws/credentials /root/.aws/config
echo "creds refreshed; expire {c['Expiration']}"
aws sts get-caller-identity --region {region}
""")
PY
  )"
  # shellcheck disable=SC2086
  printf '%s\n' "$script" | $sshc "sudo bash -s"
}

install_remote_units() {
  local sshc
  sshc="$(ssh_base)"
  # shellcheck disable=SC2086
  $sshc "sudo bash -s" <<EOF
set -euo pipefail
cat > /usr/local/bin/cado-s3-backup <<'SCRIPT'
#!/bin/bash
set -euo pipefail
BUCKET="${BUCKET}"
PREFIX="${PREFIX}"
REMOTE_DIR="${REMOTE_DIR}"
REGION="${REGION}"
LOG=/var/log/cado-s3-backup.log
exec >>"\$LOG" 2>&1
echo "==== \$(date -u +%Y-%m-%dT%H:%M:%SZ) start ===="
if ! aws sts get-caller-identity --region "\$REGION" >/dev/null 2>&1; then
  echo "ERROR: no usable AWS credentials in /root/.aws (run refresh-creds from laptop)"
  exit 1
fi
# live mirror
aws s3 sync "\$REMOTE_DIR/" "s3://\$BUCKET/\$PREFIX/live/" \\
  --region "\$REGION" \\
  --only-show-errors \\
  --exclude "*/client/**" \\
  --exclude "*/download/**" \\
  --exclude "*.sock"
# small logs mirror
aws s3 sync "\$REMOTE_DIR/" "s3://\$BUCKET/\$PREFIX/logs-live/" \\
  --region "\$REGION" \\
  --only-show-errors \\
  --exclude "*" \\
  --include "progress.log" \\
  --include "*/run.log" \\
  --include "ALL_DONE" \\
  --include "*/FACTORS.txt"
# on ALL_DONE, also take a dated snapshot once
if [[ -f "\$REMOTE_DIR/ALL_DONE" ]]; then
  STAMP_FILE=/var/lib/cado-s3-backup.final-snapshot
  if [[ ! -f "\$STAMP_FILE" ]]; then
    TS=\$(date -u +%Y%m%dT%H%M%SZ)
    aws s3 sync "\$REMOTE_DIR/" "s3://\$BUCKET/\$PREFIX/snapshots/\$TS/" \\
      --region "\$REGION" \\
      --only-show-errors \\
      --exclude "*/client/**" \\
      --exclude "*/download/**" \\
      --exclude "*.sock"
    echo "\$TS" > "\$STAMP_FILE"
    echo "final snapshot s3://\$BUCKET/\$PREFIX/snapshots/\$TS/"
  fi
fi
echo "==== \$(date -u +%Y-%m-%dT%H:%M:%SZ) ok ===="
SCRIPT
chmod 755 /usr/local/bin/cado-s3-backup

cat > /etc/systemd/system/cado-s3-backup.service <<'UNIT'
[Unit]
Description=Backup CADO NIST workdir to S3
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
Nice=10
IOSchedulingClass=best-effort
IOSchedulingPriority=7
ExecStart=/usr/local/bin/cado-s3-backup
UNIT

cat > /etc/systemd/system/cado-s3-backup.timer <<UNIT
[Unit]
Description=Periodic CADO → S3 backup

[Timer]
OnBootSec=3min
OnUnitActiveSec=${BACKUP_EVERY_MIN}min
AccuracySec=1min
Persistent=true
Unit=cado-s3-backup.service

[Install]
WantedBy=timers.target
UNIT

# Also backup soon after each job DONE line appears in progress.log
cat > /usr/local/bin/cado-s3-backup-watch <<'SCRIPT'
#!/bin/bash
set -euo pipefail
LOG=/opt/cado-nist-open/progress.log
STATE=/var/lib/cado-s3-backup.watch-offset
mkdir -p /var/lib
[[ -f "\$STATE" ]] || echo 0 > "\$STATE"
while true; do
  if [[ -f "\$LOG" ]]; then
    sz=\$(stat -c%s "\$LOG")
    off=\$(cat "\$STATE")
    if (( sz > off )); then
      if tail -c +"\$((off+1))" "\$LOG" | grep -q "===== DONE "; then
        /usr/local/bin/cado-s3-backup || true
      fi
      echo "\$sz" > "\$STATE"
    fi
  fi
  sleep 60
done
SCRIPT
chmod 755 /usr/local/bin/cado-s3-backup-watch

cat > /etc/systemd/system/cado-s3-backup-watch.service <<'UNIT'
[Unit]
Description=Trigger S3 backup when CADO jobs complete
After=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=10
ExecStart=/usr/local/bin/cado-s3-backup-watch

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable --now cado-s3-backup.timer
systemctl enable --now cado-s3-backup-watch.service
systemctl start cado-s3-backup.service || true
systemctl list-timers cado-s3-backup.timer --no-pager
EOF
}

install_launchd() {
  mkdir -p "$(dirname "$LAUNCH_AGENT")"
  local script
  script="$(cd "$ROOT" && pwd)/cado_ec2_s3_backup.sh"
  cat > "$LAUNCH_AGENT" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${script}</string>
    <string>refresh-creds</string>
  </array>
  <key>StartInterval</key><integer>21600</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>${HOME}/Library/Logs/cado-s3-backup.log</string>
  <key>StandardErrorPath</key><string>${HOME}/Library/Logs/cado-s3-backup.log</string>
</dict>
</plist>
PLIST
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$LAUNCH_AGENT"
  launchctl enable "gui/$(id -u)/$LABEL" 2>/dev/null || true
  launchctl kickstart -k "gui/$(id -u)/$LABEL" 2>/dev/null || true
  echo "installed launchd agent $LABEL (refresh-creds every 6h)"
  echo "log: ~/Library/Logs/cado-s3-backup.log"
}

cmd_install_auto() {
  echo "Installing automatic S3 backups..."
  cmd_refresh_creds
  install_remote_units
  install_launchd
  echo
  echo "Automatic backup enabled:"
  echo "  • EC2 timer: every ${BACKUP_EVERY_MIN} min → s3://${BUCKET}/${PREFIX}/live/"
  echo "  • EC2 watch: syncs soon after each '===== DONE' in progress.log"
  echo "  • Mac launchd: refreshes temp AWS creds on EC2 every 6h"
  echo "  • Final snapshot when ALL_DONE appears"
  echo
  echo "Re-run: ./scripts/cado_ec2_s3_backup.sh refresh-creds   # if timer starts failing"
}

cmd_uninstall_auto() {
  local sshc
  sshc="$(ssh_base)"
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  rm -f "$LAUNCH_AGENT"
  # shellcheck disable=SC2086
  $sshc 'sudo bash -s' <<'EOF'
systemctl disable --now cado-s3-backup.timer 2>/dev/null || true
systemctl disable --now cado-s3-backup-watch.service 2>/dev/null || true
systemctl stop cado-s3-backup.service 2>/dev/null || true
rm -f /etc/systemd/system/cado-s3-backup.service \
      /etc/systemd/system/cado-s3-backup.timer \
      /etc/systemd/system/cado-s3-backup-watch.service \
      /usr/local/bin/cado-s3-backup \
      /usr/local/bin/cado-s3-backup-watch
systemctl daemon-reload
echo "remote auto-backup removed"
EOF
  echo "uninstalled"
}

cmd="${1:-sync}"
case "$cmd" in
  sync) cmd_sync ;;
  snapshot) cmd_snapshot ;;
  status) cmd_status ;;
  pull-logs|logs) cmd_pull_logs ;;
  refresh-creds) cmd_refresh_creds ;;
  install-auto) cmd_install_auto ;;
  uninstall-auto) cmd_uninstall_auto ;;
  -h|--help|help) sed -n '2,30p' "$0" ;;
  *) die "unknown command: $cmd" ;;
esac
