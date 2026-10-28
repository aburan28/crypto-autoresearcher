# Hosted deployment for local and cloud sessions

The deployment runs the same shared library behind an authenticated HTTPS MCP
endpoint. SQLite and Qdrant stay on one encrypted EBS volume. A private versioned
S3 bucket holds source bundles and backups. Agents receive per-client retrieval
tokens, not AWS credentials. A single EC2 instance is deliberately the initial
availability boundary.

## Inputs and resources

Use an AWS identity allowed to manage the resources in `infra/aws/main.tf`, a VPC
and public subnet with an internet gateway, and a hostname you control. The default
region is us-west-2. The default instance is t3.large with 100 GB encrypted gp3
data storage and a separate encrypted root disk. Resize after measuring the actual
corpus and concurrent queries. Resources also include an Elastic IP, ECR image
repository, Secrets Manager registry and an SSM instance role.

Only TCP 443 and ACME/redirect TCP 80 are open. Application port 8080 is loopback;
Qdrant ports are not published. IMDSv2 credentials are host-only: ingestion and
backup scripts use the host IAM role and containers receive no AWS credential.
The data volume has `prevent_destroy`; instance replacement preserves its bytes.
Ongoing charges cover the instance, disks, IPv4, S3 and Secrets Manager.

## Provision and publish

1. Copy `infra/aws/terraform.tfvars.example` to an ignored `.tfvars` file and fill
   in region, VPC, subnet, hostname, unique bucket name and an immutable image tag
   such as the application commit SHA. Keep Terraform state in your established
   encrypted state backend; no authentication secret values belong in it.

```sh
cd infra/aws
terraform init
terraform plan -var-file=local.tfvars -out=deployment.plan
terraform apply deployment.plan
```

2. Create client token files and the server's hash registry on your trusted
   operator machine. Choose a new empty directory and do not print the tokens:

```sh
research-kb --home /secure/research-kb-auth token create \
  --client codex-cloud --output /secure/codex-cloud.token
research-kb --home /secure/research-kb-auth token create \
  --client claude-cloud --output /secure/claude-cloud.token
```

3. Populate the newly created Secrets Manager secret with the **hash registry**:

```sh
AUTH_ARN=$(terraform output -raw auth_secret_arn)
aws secretsmanager put-secret-value --secret-id "$AUTH_ARN" \
  --secret-string file:///secure/research-kb-auth/auth.json \
  --query VersionId --output text
```

4. Build and publish the application image using the exact tag supplied to
   Terraform. These commands run from the repository root; obtain the ECR URL
   from `terraform -chdir=infra/aws output -raw repository_url`.

```sh
ECR_URL=$(terraform -chdir=infra/aws output -raw repository_url)
REGISTRY=${ECR_URL%%/*}
AWS_REGION=us-west-2
IMAGE_TAG=THE-SAME-IMMUTABLE-TAG-AS-TERRAFORM
aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin "$REGISTRY"
docker build --platform linux/amd64 -t "$ECR_URL:$IMAGE_TAG" .
docker push "$ECR_URL:$IMAGE_TAG"
```

The host's service retries startup while the image or auth secret is unavailable.
It uses `/opt/research-kb/start.sh`, checks the persistent disk is mounted, fetches
the hash registry, pulls the image and starts Compose. The image tag is immutable;
upgrade with a new tag through Terraform, retaining the data volume. Verify a
replacement against your backup before making further changes.

5. Point the hostname's DNS A record to Terraform's `public_ip` output. Caddy
obtains a certificate after DNS and inbound ACME reachability work. Verify:

```sh
curl --fail https://kb.example.com/healthz
```

The authenticated readiness endpoint stays 503 until the corpus is imported.
AWS provisioning, public DNS and live TLS must be tested in the actual account;
local container tests cannot establish their readiness.

## Import the combined collection

On a machine with the source checkouts and original papers, register all source
roots in one `sources.toml`. Set source patterns deliberately; a sparse checkout
only contributes files physically present in it. Create and upload a bundle:

```sh
research-kb bundle /tmp/research-sources.tar.gz
aws s3 cp /tmp/research-sources.tar.gz \
  s3://YOUR-BUCKET/inbox/sources-UNIQUE-REVISION.tar.gz
```

The host imports new bundles every 15 minutes. It reads them through its IAM
role, validates hashes and imports through the operator container, then publishes
the hybrid index. Bundles are additive and never remove another source's data.
Use unique object keys for new revisions. Keep bundles below the configured
512 MiB uncompressed limit or split source patterns into separate bundles.
The host job scans only direct `.tar.gz` files in the inbox; upload to its root.

For immediate import or diagnostics, use Systems Manager:

```sh
aws ssm start-session --target INSTANCE-ID
sudo /opt/research-kb/import.sh
sudo systemctl status research-kb
sudo journalctl -u research-kb --no-pager -n 40
```

There is no remote ingestion or shell MCP tool. A cloud agent's search cannot
change the library. Source-only Lean files in a bundle remain source-only. To
attach compiled proof receipts, run `audit-lean` on a registered project with its
actual toolchain and source hashes. Plan full PDF backfill separately from existing
abstract notes; preserve and review extraction failures rather than hiding them.

## Connect local and cloud agents

Replace `kb.example.com` in the client templates. Install each token value in the
corresponding client's runtime secrets as `RESEARCH_KB_TOKEN`. Configure one shared
MCP endpoint per client and remove redundant old KB registrations after canaries
pass. Leave unrelated Cairn and experiment services intact.

Codex/Claude Code cloud runtimes must permit outbound HTTPS to the hostname
during execution. Some managed products do not expose custom MCP registration;
use `clients/cloud-search.sh` or `research-kb remote-search` there. Both paths call
the same authenticated read-only library. Setup-only network access is insufficient
if the runtime later blocks the endpoint or omits the secret.

Before cutover, compare canonical source IDs and hashes for the same query from
local Codex, local Claude Code and each intended cloud runtime. Also verify a
cross-repository theorem lookup, unauthenticated rejection and original download.

## Back up, restore and rotate

The host's daily job uses SQLite's online backup API and copies immutable source
objects to versioned S3. Run `/opt/research-kb/backup.sh` manually for a recovery
point. Qdrant remains derived; rebuild it from a restored catalog with `index`.

For recovery on a mounted replacement disk: stop the API/import jobs, restore a
chosen `backups/catalog-TIMESTAMP.sqlite` to `data/catalog.sqlite`, restore the
`objects/` prefix to `data/objects/`, set ownership to UID/GID 10001, and discard
any stale `active-index.json` pointer. Run the operator `index` command and start
the API. Check source counts, original hashes and canary queries before cutover.
Backups include the catalog's compiled receipts. Keep the same model configuration
or explicitly rebuild with the intended one. A recovery drill is still required
against the actual account.

For token rotation, create a new token for the client, install the updated hash
registry in Secrets Manager and update the client's runtime secret. On the host,
run `sudo systemctl restart research-kb` to reload the mounted registry. Local
`token revoke` takes effect immediately when editing the service's mounted file;
changes made to Secrets Manager require this restart to reach the host. Original
download URLs require the same credential as search and are never public links.

The source bundle upload identity needs `s3:PutObject` on `inbox/*`. The EC2 role
can read inbox/originals/backups and write backups/originals; it cannot publish
new inbox bundles. The public service has no route accepting an upload.
