# HCP Terraform (formerly Terraform Cloud) backend.
#
# The block is intentionally empty. A `cloud` block cannot refer to variables,
# locals, or anything else computed — only constants — so hardcoding the
# organization here would put one account's name in a repository that several
# people run from, and would make dev/prod a code edit rather than a
# configuration choice. Terraform reads the values from the environment when
# the corresponding attributes are absent:
#
#   TF_CLOUD_ORGANIZATION   the organization name          (required)
#   TF_WORKSPACE            the workspace to use           (required)
#   TF_CLOUD_PROJECT        the project the workspace is in
#   TF_CLOUD_HOSTNAME       for Terraform Enterprise; defaults to app.terraform.io
#
# So:
#   export TF_CLOUD_ORGANIZATION=your-org
#   export TF_WORKSPACE=crypto-kb-dev
#   terraform login && terraform init
#
# The empty block is still required — remove it and Terraform falls back to
# local state, which for this configuration means the record of what exists in
# AWS lives on one laptop. `infra/terraform/bootstrap/` creates the
# organization's project, workspaces, and credentials; see README.md.
terraform {
  required_version = ">= 1.6"

  cloud {}
}
