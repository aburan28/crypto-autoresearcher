# Infrastructure

Two configurations:

| directory | what it manages | state | who runs it |
| --- | --- | --- | --- |
| `.` (root) | AWS: corpus bucket notifications, EventBridge rule, SQS + DLQ, IAM roles, alarms | HCP Terraform | HCP Terraform, per workspace |
| `bootstrap/` | HCP Terraform itself: project, workspaces, variables, credentials | local | a person, once |

`bootstrap/` exists because the root module runs *inside* a workspace, so
something has to create the workspace first. Its local state is not precious —
every resource it makes is importable from the HCP Terraform API.

---

## Setup

### 1. An organization

Create one at <https://app.terraform.io/app/organizations/new> if you do not
have one. The free tier covers everything here. Note the name; it is the only
value you must supply.

### 2. Authenticate

```bash
terraform login          # writes a token to ~/.terraform.d/credentials.tfrc.json
```

For the bootstrap step you can instead export a user or team API token as
`TFE_TOKEN`. It needs permission to create projects and workspaces in the
organization.

### 3. Create the project and workspaces

```bash
cd kb/infra/terraform/bootstrap
cp terraform.tfvars.example terraform.tfvars
$EDITOR terraform.tfvars          # set `organization` at minimum
terraform init
terraform apply
```

That creates:

- project `crypto-kb`;
- workspaces `crypto-kb-dev` and `crypto-kb-prod`, both scoped to
  `kb/infra/terraform` as working directory *and* trigger prefix — without
  that, every commit to the research ledger would queue a plan that cannot
  differ;
- their Terraform variables (`environment`, `aws_region`, `bucket_name`,
  `create_bucket`, `queue_age_alarm_seconds`);
- a project-scoped variable set for AWS credentials.

Two deliberate asymmetries between the workspaces:

- **`crypto-kb-prod` does not auto-apply and refuses destroy plans.** It
  attaches to the bucket holding the research corpus — the source of truth for
  everything the index derives — and `allow_destroy_plan = false` is what stops
  a stray `terraform destroy` from reaching it.
- **`crypto-kb-dev` creates its own bucket; prod does not.** `create_bucket` is
  false in production, so Terraform looks the bucket up and attaches
  notifications to it rather than claiming ownership. Two workspaces both
  believing they own the corpus is the failure worth engineering against.

### 4. Give the workspaces AWS credentials

**Dynamic credentials (recommended).** No long-lived key exists at all;
HCP Terraform exchanges a signed OIDC token for a short-lived AWS role
session. In AWS:

1. Create an IAM OIDC identity provider for `app.terraform.io`, audience
   `aws.workload.identity`.
2. Create a role trusting it, with a condition on
   `app.terraform.io:sub` matching
   `organization:<org>:project:crypto-kb:workspace:crypto-kb-prod:run_phase:*`
   — scoped per workspace, so dev cannot assume prod's role.
3. Attach a policy allowing the resources this module manages (S3
   notifications, SQS, EventBridge, IAM roles, Secrets Manager, CloudWatch
   alarms).

Then set these as **environment** variables on the variable set (or per
workspace) — `bootstrap/` creates the set and leaves it empty for exactly
this:

```text
TFC_AWS_PROVIDER_AUTH  = true
TFC_AWS_RUN_ROLE_ARN   = arn:aws:iam::<account>:role/<role>
```

Current details: <https://developer.hashicorp.com/terraform/cloud-docs/workspaces/dynamic-provider-credentials/aws-configuration>

**Static keys (fallback).** Set `aws_access_key_id` and
`aws_secret_access_key` in `bootstrap/terraform.tfvars`. They become sensitive
variables in the variable set. This creates a key that must be rotated by hand
and that lives in HCP Terraform indefinitely — prefer OIDC.

### 5. Run the root module

```bash
cd kb/infra/terraform
export TF_CLOUD_ORGANIZATION=your-org
export TF_WORKSPACE=crypto-kb-dev
terraform init
terraform plan
```

The `cloud` block in `cloud.tf` is intentionally empty: it cannot reference
variables, so hardcoding an organization would put one account's name in a
shared repository and make dev/prod a code edit. Terraform reads
`TF_CLOUD_ORGANIZATION`, `TF_WORKSPACE`, `TF_CLOUD_PROJECT`, and
`TF_CLOUD_HOSTNAME` when the matching attributes are absent.

Forget them and the error says so precisely:

```text
Error: Invalid or missing required argument
"organization" must be set in the cloud configuration or as an environment
variable: TF_CLOUD_ORGANIZATION.
```

### 6. Wire the outputs into the services

```bash
terraform output -json service_environment
```

gives the `CRYPTO_KB_*` settings for the ECS task definitions, and
`worker_role_arn` / `mcp_role_arn` give the two task roles. They are
deliberately asymmetric: the worker can read sources and write only derived
artifacts; the MCP service has no S3 write access and no queue access at all.

---

## VCS-driven runs

Optional, and worth adding once the workspaces work. It gives speculative
plans on pull requests, so a review shows the diff in AWS and not only the
diff in HCL.

1. Connect GitHub under **Settings → Providers** in the organization.
2. Copy the OAuth token id (`ot-…`).
3. Set in `bootstrap/terraform.tfvars`:

```hcl
vcs_repo_identifier = "aburan28/crypto-autoresearcher"
vcs_branch          = "main"
vcs_oauth_token_id  = "ot-xxxxxxxxxxxxxxxx"
```

4. `terraform apply` in `bootstrap/`.

Leaving `vcs_repo_identifier` empty keeps the workspaces CLI-driven, which is
the right starting point: it works before any VCS connection exists, and
attaching one later does not recreate the workspaces.

---

## Variables

Values live in three places, and it is worth knowing which is authoritative:

- **HCP Terraform workspace variables** — what actually runs. Set by
  `bootstrap/`, editable in the UI, and every change is an audit event.
- **`workspaces/dev.tfvars`, `workspaces/prod.tfvars`** — the reviewable copy
  of the same numbers, and what a CLI-driven `terraform plan
  -var-file=workspaces/prod.tfvars` uses. Not read by remote runs.
- **`variables.tf` defaults** — the safe fallback. `create_bucket` defaults to
  `false` so a workspace configured by accident attaches to an existing bucket
  rather than trying to own one.

If you change a value, change it in the workspace *and* the tfvars file, or
the reviewable copy stops being reviewable.

---

## Verification

Both configurations are `terraform validate`-clean and `terraform fmt`-clean
against Terraform 1.9.8, with the provider lock files committed for
linux/darwin on amd64 and arm64. CI re-checks this on every change under
`kb/infra/terraform/` — `.github/workflows/terraform.yml`, which runs with no
credentials because `terraform init -backend=false` skips cloud
initialisation.

```bash
terraform fmt -check -recursive
terraform init -backend=false && terraform validate
cd bootstrap && terraform init -backend=false && terraform validate
```

**Nothing here has been applied.** No AWS resources and no HCP Terraform
objects were created — the configurations are validated, not deployed, and the
first `terraform apply` is yours to run and review.

---

## What this does not cover

The ECS services themselves. `infra/docker/Dockerfile` builds both images
(`mcp` and `worker` targets) and this module creates the roles, queue, and
secret they need, but the cluster, task definitions, service, load balancer,
and the TLS/authentication layer in front of the MCP service are not written.
The MCP server is stdio-only today; see the last section of `kb/README.md`
before exposing it over a network.
