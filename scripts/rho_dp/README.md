# Pollard-rho distinguished-point (DP) RDS store
#
# Scripts:
#   scripts/rho_rds.sh              create | status | migrate | connstr | allow-sg | destroy
#   scripts/rho_dp/schema.sql       campaigns + distinguished_points + collisions + report_dp()
#   scripts/rho_dp/worker.py        register | register-ecc2k | report | smoke | run-toy |
#                                   ingest-ecc2k | watch-ecc2k
#   scripts/rho_dp/iam-policy-rho-rds.json
#   harness/rho_dp_store.py         Python adapter (psycopg or psql fallback)
#   harness/walk.py                 toy DP rho; optional `store=` → report_dp()
#
# Region / VPC: us-west-2 default VPC (`vpc-0394e002d95674fe6`), same as CADO EC2.
# Engine: PostgreSQL 16, default class `db.t4g.micro`, 20 GB gp3, single-AZ, encrypted.
#
# ## Where the rho code lives
#
# | Path | What |
# |------|------|
# | `harness/walk.py`, `harness/rho.py`, `harness/kangaroo.py` | Toy prime-field Pollard's rho / DP / kangaroo (this repo). `solve_dp()` is the van Oorschot–Wiener pattern; pass `store=` to write DPs to RDS. |
# | `harness/rho_dp_store.py` | RDS adapter + SEC1 / ECC2K limb key encoding. |
# | `/Volumes/SSD990/autolab/tasks/ecc2k130_pollard_rho/` | Harbor walk bench (`environment/solve.c`) + live Type-II walker (`research/typeii_orbit_pmull_lut_worker.c`) writing `T2QBIN1` sidecars. |
# | `/Volumes/SSD990/autolab/tasks/ecc2k130_pollard_rho/research/RHO_DP_RDS.md` | Autolab-side runbook: parallel workers + continuous ingest. |
# | `/Volumes/SSD990/autolab/tasks/ecc2k130_pollard_rho/research/rho_dp_rds_bridge.py` | Thin wrapper that calls this repo's `worker.py`. |
# | `/Volumes/SSD990/autolab/ecc2k130_campaign_state/` | JSONL campaign state for the `ecc2k130_break` Harbor loop. |
#
# There is no full ECC2K-130 solver binary in this crypto-autoresearcher tree.
# Live integration: C walkers keep writing `*.t2qbin`; `ingest-ecc2k` /
# `watch-ecc2k` (campaign `ecc2k-130`) push them into the shared collision table.
#
# ## Network model
#
# - RDS is created with `--no-publicly-accessible` (private IP only).
# - Security group `rho-dp-rds` allows TCP 5432 from existing CADO worker SGs
#   (`.cado_ec2_sg`, `.cado_ec2_client_c8i_sg`). Add more with:
#     ./scripts/rho_rds.sh allow-sg sg-xxxxxxxx
# - Laptop debugging: either SSM/bastion into a VPC host, or recreate with
#   `RHO_RDS_PUBLICLY_ACCESSIBLE=true` **and**
#   `./scripts/rho_rds.sh allow-cidr YOUR.PUBLIC.IP/32` (never 0.0.0.0/0).
#   Tradeoff: public DNS + internet path vs. convenience; keep SG to /32.
#
# ## Credentials
#
# Prefer Secrets Manager secret name `rho/dp-rds`
# (ARN e.g. `arn:aws:secretsmanager:us-west-2:123456789012:secret:rho/dp-rds-…`,
# also cached in `scripts/.rho_rds_secret_arn`). Local fallback:
# `scripts/.rho_rds_password`. CreateSecret is done **without tags** so
# `secretsmanager:TagResource` is not required.
#
# Never commit `.rho_rds_*` or passwords. Never hardcode the password in workers.
#
# ```sh
# export DATABASE_URL=$(./scripts/rho_rds.sh connstr | head -1)
# # or on EC2 with instance role / laptop AWS creds:
# #   RHO_DP_DSN=...  /  secret name rho/dp-rds
# ```
#
# Optional Python driver (faster than psql subprocess):
#   pip install 'psycopg[binary]>=3.1'
#   # or: pip install -e '.[rho-dp]'
#
# ## Schema (summary)
#
# | Table / function        | Role |
# |-------------------------|------|
# | `rho_campaigns`         | curve_id / campaign metadata |
# | `distinguished_points`  | PK `(campaign_id, point_key)` — first walk wins |
# | `rho_collisions`        | second walk with different `(a,b)` on same DP |
# | `report_dp(...)`        | atomic insert-or-collide helper |
#
# `point_key` should be a canonical encoding (e.g. SEC1 compressed). Walk
# coefficients `a`,`b` are big-endian bytea mod n. Collision ⇒ two distinct
# representations of the same group element ⇒ discrete log recovery offline.
#
# Toy Weierstrass: SEC1 compressed `0x02|0x03 || x`.
# ECC2K Type-II quotient: 48-byte little-endian limb dump (3×u64 x + 3×u64 y).
#
# ## Run a toy rho worker against RDS
#
# From a VPC host (CADO client) with this repo (or just the harness + scripts):
#
# ```sh
# export DATABASE_URL=$(./scripts/rho_rds.sh connstr | head -1)
# ./scripts/rho_rds.sh migrate   # once
#
# python3 scripts/rho_dp/worker.py smoke --campaign smoke-demo
#
# python3 scripts/rho_dp/worker.py run-toy \
#   --campaign toy-ecc-12-seed7 \
#   --seed 7 --field-bits 12 --dp-bits 2 --max-walks 512
# ```
#
# Two workers on the same `--campaign` share the DP table; a remote collision
# stops `solve_dp` when the prior `(a,b)` yields a verified scalar.
#
# ## ECC2K-130 campaign + continuous ingest
#
# Canonical campaign id: **`ecc2k-130`** (curve `certicom-ecc2k-130`).
# Point keys are 48-byte LE limb dumps; coeffs are 17-byte BE (`mod 2^131`).
# Full autolab runbook: `.../ecc2k130_pollard_rho/research/RHO_DP_RDS.md`.
#
# ```sh
# # once
# python3 scripts/rho_dp/worker.py register-ecc2k
#
# # one-shot (e.g. smoke a calibration shard; --limit keeps it cheap)
# python3 scripts/rho_dp/worker.py ingest-ecc2k \
#   --campaign ecc2k-130 \
#   --files /path/to/shard*.t2qbin \
#   --limit 64 \
#   --stop-on-collision
#
# # parallel workers: C walkers write OUT/*.t2qbin; one watcher shares the table
# python3 scripts/rho_dp/worker.py watch-ecc2k \
#   --campaign ecc2k-130 \
#   --dir /path/to/OUT \
#   --glob '*.t2qbin' \
#   --poll-seconds 2 \
#   --stop-on-collision
# ```
#
# Credentials on CADO / VPC hosts: `export DATABASE_URL=$(./scripts/rho_rds.sh connstr | head -1)`
# or leave unset and let `resolve_dsn()` read Secrets Manager `rho/dp-rds`.
#
# ## IAM unblock
#
# If `create` fails with `rds:CreateDBInstance` AccessDenied, an account admin:
#
# ```sh
# aws iam put-user-policy --user-name adam --policy-name RhoDpRds \
#   --policy-document file://scripts/rho_dp/iam-policy-rho-rds.json
# ./scripts/rho_rds.sh create
# ./scripts/rho_rds.sh migrate
# ```
#
# ## Verify
#
# ```sh
# ./scripts/rho_rds.sh status
# ./scripts/rho_rds.sh migrate
# python3 scripts/rho_dp/worker.py smoke --campaign smoke-$(date +%s)
# # or raw SQL:
# psql "$(./scripts/rho_rds.sh connstr 2>/dev/null | head -1)" \
#   -c "SELECT report_dp('demo', E'\\\\x0102', E'\\\\x01', E'\\\\x02', NULL, 1, 'w1');"
# ```
#
# ## Destroy
#
# ```sh
# ./scripts/rho_rds.sh destroy --yes
# # optional: RHO_RDS_DESTROY_SECRET=1 RHO_RDS_DESTROY_SUBNET_GROUP=1 ...
# ```
#
# Does **not** terminate CADO EC2 instances. SG `rho-dp-rds` is retained by default.
#
# ## Cost (rough)
#
# us-west-2 on-demand: **~$15–25/month** for `db.t4g.micro` + 20 GB gp3 + 1-day backup.
# Destroy when idle.
