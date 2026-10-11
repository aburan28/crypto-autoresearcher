#!/usr/bin/env bash
# Provision / manage an RDS PostgreSQL store for Pollard-rho distinguished points.
#
# Usage:
#   ./scripts/rho_rds.sh create|status|migrate|connstr|allow-sg|allow-cidr|destroy
#
# State (gitignored): scripts/.rho_rds_*
# Schema:            scripts/rho_dp/schema.sql
# IAM (if create fails): scripts/rho_dp/iam-policy-rho-rds.json
#
# Defaults target the same us-west-2 default VPC as the CADO EC2 workers.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
REGION="${AWS_REGION:-us-west-2}"
VPC_ID="${RHO_RDS_VPC:-vpc-0394e002d95674fe6}"
DB_ID="${RHO_RDS_DB_ID:-rho-dp}"
DB_CLASS="${RHO_RDS_INSTANCE_CLASS:-db.t4g.micro}"
DB_STORAGE="${RHO_RDS_STORAGE_GB:-20}"
DB_ENGINE="${RHO_RDS_ENGINE:-postgres}"
DB_ENGINE_VERSION="${RHO_RDS_ENGINE_VERSION:-16}"
DB_NAME="${RHO_RDS_DB_NAME:-rho_dp}"
DB_USER="${RHO_RDS_MASTER_USER:-rho}"
SECRET_NAME="${RHO_RDS_SECRET_NAME:-rho/dp-rds}"
SUBNET_GROUP="${RHO_RDS_SUBNET_GROUP:-rho-dp-subnets}"
# PubliclyAccessible=false → private IP only (reachable from same VPC / peered nets).
# Default VPC subnets are "public" (IGW route); RDS still has no public DNS when false.
PUBLIC_ACCESS="${RHO_RDS_PUBLICLY_ACCESSIBLE:-false}"

STATE_SG="$ROOT/.rho_rds_sg"
STATE_DB="$ROOT/.rho_rds_db_id"
STATE_ENDPOINT="$ROOT/.rho_rds_endpoint"
STATE_SECRET="$ROOT/.rho_rds_secret_arn"
STATE_PASSWORD="$ROOT/.rho_rds_password"   # local fallback if Secrets Manager denied
STATE_SUBNET_GROUP="$ROOT/.rho_rds_subnet_group"
SCHEMA_SQL="$ROOT/rho_dp/schema.sql"

die() { echo "error: $*" >&2; exit 1; }
need() { command -v "$1" >/dev/null || die "missing command: $1"; }

write_state() { printf '%s' "$2" >"$1"; }
read_state() { [[ -f "$1" ]] && cat "$1" || true; }

ensure_sg() {
  local sg existing
  existing="$(read_state "$STATE_SG")"
  if [[ -n "$existing" ]]; then
    if aws ec2 describe-security-groups --region "$REGION" --group-ids "$existing" \
         --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null | grep -q '^sg-'; then
      echo "$existing"
      return
    fi
  fi
  existing="$(aws ec2 describe-security-groups --region "$REGION" \
    --filters "Name=group-name,Values=rho-dp-rds" "Name=vpc-id,Values=$VPC_ID" \
    --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || true)"
  if [[ -n "$existing" && "$existing" != "None" && "$existing" != "null" ]]; then
    write_state "$STATE_SG" "$existing"
    echo "$existing"
    return
  fi
  sg="$(aws ec2 create-security-group --region "$REGION" \
    --group-name rho-dp-rds \
    --description "PostgreSQL for Pollard-rho distinguished points" \
    --vpc-id "$VPC_ID" \
    --query GroupId --output text)"
  aws ec2 create-tags --region "$REGION" --resources "$sg" \
    --tags Key=Name,Value=rho-dp-rds Key=Project,Value=pollard-rho Key=Purpose,Value=dp-store
  write_state "$STATE_SG" "$sg"
  # Wire known CADO worker SGs if present locally.
  local cado
  for cado in "$ROOT/.cado_ec2_sg" "$ROOT/.cado_ec2_client_c8i_sg"; do
    if [[ -f "$cado" ]]; then
      aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$sg" \
        --protocol tcp --port 5432 --source-group "$(cat "$cado")" >/dev/null 2>&1 || true
    fi
  done
  echo "$sg"
}

ensure_subnet_group() {
  local ids
  ids="$(aws ec2 describe-subnets --region "$REGION" \
    --filters "Name=vpc-id,Values=$VPC_ID" \
    --query 'Subnets[].SubnetId' --output text)"
  [[ -n "$ids" ]] || die "no subnets in VPC $VPC_ID"
  # Need ≥2 AZs for RDS subnet groups.
  if aws rds describe-db-subnet-groups --region "$REGION" \
       --db-subnet-group-name "$SUBNET_GROUP" >/dev/null 2>&1; then
    write_state "$STATE_SUBNET_GROUP" "$SUBNET_GROUP"
    echo "$SUBNET_GROUP"
    return 0
  fi
  # shellcheck disable=SC2086
  if ! aws rds create-db-subnet-group --region "$REGION" \
      --db-subnet-group-name "$SUBNET_GROUP" \
      --db-subnet-group-description "rho DP store subnets" \
      --subnet-ids $ids \
      --tags Key=Project,Value=pollard-rho >/dev/null; then
    echo "error: CreateDBSubnetGroup failed (need rds:CreateDBSubnetGroup)" >&2
    return 1
  fi
  write_state "$STATE_SUBNET_GROUP" "$SUBNET_GROUP"
  echo "$SUBNET_GROUP"
}

gen_password() {
  # URL-safe-ish; avoid @:/?&# in connection strings.
  openssl rand -base64 32 | tr -d '/+=' | head -c 32
}

store_password() {
  local pw="$1" arn payload
  payload="$(jq -nc --arg u "$DB_USER" --arg p "$pw" --arg db "$DB_NAME" \
    '{username:$u,password:$p,dbname:$db,engine:"postgres"}')"
  # Omit tags: TagResource is often missing from narrow IAM grants and blocks CreateSecret.
  if arn="$(aws secretsmanager create-secret --region "$REGION" \
      --name "$SECRET_NAME" \
      --description "Master password for rho-dp RDS ($DB_ID)" \
      --secret-string "$payload" \
      --query ARN --output text 2>/dev/null)"; then
    write_state "$STATE_SECRET" "$arn"
    umask 077
    write_state "$STATE_PASSWORD" "$pw"
    echo "secret_arn=$arn" >&2
    return
  fi
  # Update if secret already exists
  if aws secretsmanager put-secret-value --region "$REGION" \
      --secret-id "$SECRET_NAME" \
      --secret-string "$payload" >/dev/null 2>&1; then
    arn="$(aws secretsmanager describe-secret --region "$REGION" --secret-id "$SECRET_NAME" \
      --query ARN --output text 2>/dev/null || true)"
    [[ -n "$arn" && "$arn" != "None" ]] && write_state "$STATE_SECRET" "$arn"
    umask 077
    write_state "$STATE_PASSWORD" "$pw"
    echo "secret_arn=${arn:-$SECRET_NAME} (updated)" >&2
    return
  fi
  # Local fallback (gitignored). Prefer fixing IAM and re-running store-secret.
  umask 077
  write_state "$STATE_PASSWORD" "$pw"
  echo "warning: Secrets Manager unavailable; password written to $STATE_PASSWORD (gitignored)" >&2
}

fetch_password() {
  local arn pw
  arn="$(read_state "$STATE_SECRET")"
  if [[ -n "$arn" ]]; then
    if pw="$(aws secretsmanager get-secret-value --region "$REGION" --secret-id "$arn" \
         --query SecretString --output text 2>/dev/null | jq -r .password)"; then
      [[ -n "$pw" && "$pw" != "null" ]] && { echo "$pw"; return; }
    fi
  fi
  if [[ -f "$STATE_PASSWORD" ]]; then
    cat "$STATE_PASSWORD"
    return
  fi
  if pw="$(aws secretsmanager get-secret-value --region "$REGION" --secret-id "$SECRET_NAME" \
       --query SecretString --output text 2>/dev/null | jq -r .password)"; then
    [[ -n "$pw" && "$pw" != "null" ]] && { echo "$pw"; return; }
  fi
  die "no password available (Secrets Manager + $STATE_PASSWORD empty)"
}

cmd_create() {
  need aws
  need openssl
  need jq
  local sg subnet_group pw pub_flag
  sg="$(ensure_sg)"
  echo "security_group=$sg"
  write_state "$STATE_DB" "$DB_ID"

  if aws rds describe-db-instances --region "$REGION" \
       --db-instance-identifier "$DB_ID" >/dev/null 2>&1; then
    echo "DB $DB_ID already exists; refreshing endpoint state"
    cmd_status
    return
  fi

  if ! subnet_group="$(ensure_subnet_group)"; then
    cat >&2 <<EOF

Blocked before RDS create: missing rds:* IAM on user adam.
Attach scripts/rho_dp/iam-policy-rho-rds.json (account admin):

  aws iam put-user-policy --user-name adam --policy-name RhoDpRds \\
    --policy-document file://scripts/rho_dp/iam-policy-rho-rds.json

Then re-run: ./scripts/rho_rds.sh create && ./scripts/rho_rds.sh migrate

Security group $(read_state "$STATE_SG") is already ready.
EOF
    exit 1
  fi
  echo "subnet_group=$subnet_group"
  # Reuse existing local password across retries so Secrets/local and RDS stay aligned.
  if [[ -f "$STATE_PASSWORD" && -s "$STATE_PASSWORD" ]]; then
    pw="$(cat "$STATE_PASSWORD")"
  else
    pw="$(gen_password)"
  fi
  store_password "$pw"

  if [[ "$PUBLIC_ACCESS" == "true" ]]; then
    pub_flag=(--publicly-accessible)
    echo "warning: PUBLIC access enabled — keep SG tight (prefer allow-cidr YOUR_IP/32 only)" >&2
  else
    pub_flag=(--no-publicly-accessible)
  fi

  echo "creating RDS $DB_ID ($DB_ENGINE $DB_ENGINE_VERSION, $DB_CLASS, ${DB_STORAGE}GB) ..."
  if ! aws rds create-db-instance --region "$REGION" \
      --db-instance-identifier "$DB_ID" \
      --db-instance-class "$DB_CLASS" \
      --engine "$DB_ENGINE" \
      --engine-version "$DB_ENGINE_VERSION" \
      --master-username "$DB_USER" \
      --master-user-password "$pw" \
      --allocated-storage "$DB_STORAGE" \
      --storage-type gp3 \
      --db-name "$DB_NAME" \
      --vpc-security-group-ids "$sg" \
      --db-subnet-group-name "$subnet_group" \
      --backup-retention-period 1 \
      --no-multi-az \
      --no-deletion-protection \
      --storage-encrypted \
      "${pub_flag[@]}" \
      --tags Key=Name,Value=rho-dp Key=Project,Value=pollard-rho Key=Purpose,Value=dp-store; then
    cat >&2 <<EOF

RDS create failed (likely IAM). Attach scripts/rho_dp/iam-policy-rho-rds.json to user adam, then re-run:
  ./scripts/rho_rds.sh create

Narrowest admin fix (account root / IAM admin):
  aws iam put-user-policy --user-name adam --policy-name RhoDpRds \\
    --policy-document file://scripts/rho_dp/iam-policy-rho-rds.json

Security group $sg is already ready (ingress 5432 from CADO worker SGs).
EOF
    exit 1
  fi

  echo "waiting for available (often 5–10 min) ..."
  aws rds wait db-instance-available --region "$REGION" --db-instance-identifier "$DB_ID"
  cmd_status
  echo
  echo "Next: ./scripts/rho_rds.sh migrate"
}

cmd_status() {
  need aws
  write_state "$STATE_DB" "$DB_ID"
  local json endpoint status
  if ! json="$(aws rds describe-db-instances --region "$REGION" \
      --db-instance-identifier "$DB_ID" --output json 2>&1)"; then
    echo "$json" >&2
    echo "security_group=$(read_state "$STATE_SG")"
    echo "db_id=$DB_ID (not found or AccessDenied)"
    return 1
  fi
  endpoint="$(echo "$json" | jq -r '.DBInstances[0].Endpoint.Address // empty')"
  status="$(echo "$json" | jq -r '.DBInstances[0].DBInstanceStatus')"
  [[ -n "$endpoint" ]] && write_state "$STATE_ENDPOINT" "$endpoint"
  echo "$json" | jq -r '
    .DBInstances[0] |
    "db_id=\(.DBInstanceIdentifier)
status=\(.DBInstanceStatus)
engine=\(.Engine) \(.EngineVersion)
class=\(.DBInstanceClass)
storage=\(.AllocatedStorage)GB \(.StorageType)
endpoint=\(.Endpoint.Address // "pending"):\(.Endpoint.Port // 5432)
public=\(.PubliclyAccessible)
az=\(.AvailabilityZone // "n/a")
subnet_group=\(.DBSubnetGroup.DBSubnetGroupName // "n/a")
sg=\(.VpcSecurityGroups | map(.VpcSecurityGroupId) | join(","))
encrypted=\(.StorageEncrypted)"
  '
  echo "secret_name=$SECRET_NAME"
  echo "secret_arn=$(read_state "$STATE_SECRET")"
  echo "local_sg_file=$(read_state "$STATE_SG")"
  [[ "$status" == "available" ]]
}

cmd_connstr() {
  need jq
  local endpoint pw port
  endpoint="$(read_state "$STATE_ENDPOINT")"
  if [[ -z "$endpoint" ]]; then
    endpoint="$(aws rds describe-db-instances --region "$REGION" \
      --db-instance-identifier "$DB_ID" \
      --query 'DBInstances[0].Endpoint.Address' --output text)"
    write_state "$STATE_ENDPOINT" "$endpoint"
  fi
  port=5432
  pw="$(fetch_password)"
  # Percent-encode is skipped: password alphabet is URL-safe by construction.
  echo "postgresql://${DB_USER}:${pw}@${endpoint}:${port}/${DB_NAME}?sslmode=require"
  echo "# export DATABASE_URL=\$(./scripts/rho_rds.sh connstr | head -1)" >&2
  echo "# Or: RHO_DP_DSN=...  (password also in Secrets Manager $SECRET_NAME or $STATE_PASSWORD)" >&2
}

cmd_migrate() {
  need psql
  local url
  url="$(cmd_connstr 2>/dev/null | head -1)"
  [[ -f "$SCHEMA_SQL" ]] || die "missing $SCHEMA_SQL"
  echo "applying $SCHEMA_SQL ..."
  psql "$url" -v ON_ERROR_STOP=1 -f "$SCHEMA_SQL"
  echo "schema ok"
  psql "$url" -c "SELECT version, applied_at, note FROM schema_migrations ORDER BY version;"
}

cmd_allow_sg() {
  local worker_sg="${1:-}"
  [[ -n "$worker_sg" ]] || die "usage: $0 allow-sg <sg-xxxxxxxx>"
  local sg
  sg="$(ensure_sg)"
  aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$sg" \
    --protocol tcp --port 5432 --source-group "$worker_sg"
  echo "allowed 5432 from $worker_sg → $sg"
}

cmd_allow_cidr() {
  local cidr="${1:-}"
  [[ -n "$cidr" ]] || die "usage: $0 allow-cidr <x.x.x.x/32>   # laptop debug; keep tight"
  local sg
  sg="$(ensure_sg)"
  aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$sg" \
    --protocol tcp --port 5432 --cidr "$cidr"
  echo "allowed 5432 from $cidr → $sg"
  echo "note: with --no-publicly-accessible, laptop still needs VPN/SSM/bastion or RHO_RDS_PUBLICLY_ACCESSIBLE=true recreate"
}

cmd_destroy() {
  need aws
  local confirm="${1:-}"
  [[ "$confirm" == "--yes" ]] || die "refusing: pass --yes to destroy RDS $DB_ID (irreversible for the instance; final snapshot skipped)"
  echo "deleting DB instance $DB_ID (skip final snapshot) ..."
  aws rds delete-db-instance --region "$REGION" \
    --db-instance-identifier "$DB_ID" \
    --skip-final-snapshot \
    --delete-automated-backups || true
  echo "waiting for deletion ..."
  aws rds wait db-instance-deleted --region "$REGION" --db-instance-identifier "$DB_ID" || true
  # Keep SG (shared); optionally delete subnet group + secret
  if [[ "${RHO_RDS_DESTROY_SUBNET_GROUP:-0}" == "1" ]]; then
    aws rds delete-db-subnet-group --region "$REGION" --db-subnet-group-name "$SUBNET_GROUP" || true
  fi
  if [[ "${RHO_RDS_DESTROY_SECRET:-0}" == "1" ]]; then
    aws secretsmanager delete-secret --region "$REGION" --secret-id "$SECRET_NAME" \
      --force-delete-without-recovery || true
  fi
  rm -f "$STATE_ENDPOINT" "$STATE_PASSWORD"
  echo "destroyed $DB_ID (SG $(read_state "$STATE_SG") retained)"
}

cmd_store_secret() {
  # Re-upload local password to Secrets Manager after IAM is fixed.
  [[ -f "$STATE_PASSWORD" ]] || die "no $STATE_PASSWORD"
  store_password "$(cat "$STATE_PASSWORD")"
}

usage() {
  cat <<EOF
usage: $0 <command>

  create       Create subnet group + RDS Postgres (waits until available)
  status       Show instance / endpoint / SG
  migrate      Apply scripts/rho_dp/schema.sql via psql
  connstr      Print postgresql:// URL (sslmode=require)
  allow-sg SG  Open 5432 from a worker security group
  allow-cidr C Open 5432 from a CIDR (prefer YOUR_IP/32 for laptop debug)
  store-secret Push local .rho_rds_password into Secrets Manager
  destroy --yes  Delete the RDS instance (no final snapshot)

Environment overrides: AWS_REGION, RHO_RDS_DB_ID, RHO_RDS_INSTANCE_CLASS,
  RHO_RDS_STORAGE_GB, RHO_RDS_PUBLICLY_ACCESSIBLE=true|false, RHO_RDS_VPC

Cost (order of magnitude, us-west-2 on-demand, 2026): db.t4g.micro ≈ \$12–15/mo
  + 20GB gp3 ≈ \$2–3/mo + light backup ≈ \$15–25/mo. Stop/destroy when idle.
EOF
}

cmd="${1:-}"
shift || true
case "$cmd" in
  create)       cmd_create "$@" ;;
  status)       cmd_status "$@" ;;
  migrate)      cmd_migrate "$@" ;;
  connstr)      cmd_connstr "$@" ;;
  allow-sg)     cmd_allow_sg "$@" ;;
  allow-cidr)   cmd_allow_cidr "$@" ;;
  store-secret) cmd_store_secret "$@" ;;
  destroy)      cmd_destroy "$@" ;;
  -h|--help|help|"") usage ;;
  *) die "unknown command: $cmd (try --help)" ;;
esac
