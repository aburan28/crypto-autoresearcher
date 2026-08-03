# Creates the HCP Terraform project, workspaces, and credentials that the
# root module in ../ runs inside.
#
# This is the one configuration that cannot itself live in HCP Terraform: it
# builds the workspaces, so it has to run before any workspace exists. It
# keeps local state, and that state is not important — every resource here is
# `terraform import`-able from the HCP Terraform API, and losing the file
# costs a re-import, not the infrastructure.
#
# Run once, by a person, with a user token:
#
#   cd kb/infra/terraform/bootstrap
#   cp terraform.tfvars.example terraform.tfvars   # then edit it
#   export TFE_TOKEN=$(…)                          # a user or team API token
#   terraform init && terraform apply

locals {
  # dev creates its own bucket; prod attaches to the corpus bucket that
  # already exists and must not be owned by a Terraform workspace.
  workspaces = {
    dev = {
      description   = "crypto-kb retrieval index — development"
      auto_apply    = true
      bucket_name   = "${var.corpus_bucket}-dev"
      create_bucket = "true"
      queue_age     = "900"
    }
    prod = {
      description   = "crypto-kb retrieval index — production"
      auto_apply    = false # production applies are reviewed by a human
      bucket_name   = var.corpus_bucket
      create_bucket = "false"
      queue_age     = "3600"
    }
  }
}

resource "tfe_project" "crypto_kb" {
  organization = var.organization
  name         = var.project_name
  description  = "Derived retrieval index over the ECDLP research corpus (kb/)."
}

resource "tfe_workspace" "this" {
  for_each = local.workspaces

  organization = var.organization
  project_id   = tfe_project.crypto_kb.id
  name         = "${var.workspace_prefix}-${each.key}"
  description  = each.value.description

  # Only this directory. Without it every commit to the research ledger — which
  # is most commits in this repository — queues a plan that cannot differ.
  working_directory = var.working_directory
  trigger_prefixes  = [var.working_directory]

  auto_apply = each.value.auto_apply

  # Speculative plans on pull requests: the review shows the diff in AWS, not
  # only the diff in HCL.
  speculative_enabled           = true
  structured_run_output_enabled = true
  assessments_enabled           = each.key == "prod"

  # Refuse a destroy unless someone deliberately allows it. The prod workspace
  # attaches to the bucket holding the source of truth.
  allow_destroy_plan = each.key != "prod"

  terraform_version = var.terraform_version

  dynamic "vcs_repo" {
    for_each = var.vcs_repo_identifier == "" ? [] : [1]
    content {
      identifier     = var.vcs_repo_identifier
      branch         = var.vcs_branch
      oauth_token_id = var.vcs_oauth_token_id
    }
  }

  tags = {
    project   = "crypto-kb"
    component = "retrieval-index"
  }
}

# Execution mode belongs here rather than on tfe_workspace, where the
# attribute is deprecated. Remote: Terraform runs on HCP Terraform's own
# workers, so no AWS credentials are ever needed on a laptop.
resource "tfe_workspace_settings" "this" {
  for_each = local.workspaces

  workspace_id   = tfe_workspace.this[each.key].id
  execution_mode = "remote"
}

# --------------------------------------------------------------------------
# Per-workspace inputs
#
# These mirror workspaces/*.tfvars in the root module. They are set here so
# the VCS-driven workflow has them without reading a tfvars file out of the
# repository, and so a change to one is an auditable HCP Terraform event.
# --------------------------------------------------------------------------

resource "tfe_variable" "environment" {
  for_each = local.workspaces

  workspace_id = tfe_workspace.this[each.key].id
  category     = "terraform"
  key          = "environment"
  value        = each.key
  description  = "Names and tags every resource in this workspace."
}

resource "tfe_variable" "aws_region" {
  for_each = local.workspaces

  workspace_id = tfe_workspace.this[each.key].id
  category     = "terraform"
  key          = "aws_region"
  value        = var.aws_region
}

resource "tfe_variable" "bucket_name" {
  for_each = local.workspaces

  workspace_id = tfe_workspace.this[each.key].id
  category     = "terraform"
  key          = "bucket_name"
  value        = each.value.bucket_name
  description  = "The corpus bucket. Holds the source of truth."
}

resource "tfe_variable" "create_bucket" {
  for_each = local.workspaces

  workspace_id = tfe_workspace.this[each.key].id
  category     = "terraform"
  key          = "create_bucket"
  value        = each.value.create_bucket
  hcl          = true
  description  = "False where the bucket is owned outside this configuration."
}

resource "tfe_variable" "queue_age_alarm_seconds" {
  for_each = local.workspaces

  workspace_id = tfe_workspace.this[each.key].id
  category     = "terraform"
  key          = "queue_age_alarm_seconds"
  value        = each.value.queue_age
  hcl          = true
}

# --------------------------------------------------------------------------
# AWS credentials
#
# A variable set rather than per-workspace variables: rotating a key should be
# one edit, not one per environment. Scoped to this project, not global — a
# global set would hand these credentials to every workspace in the
# organization, including ones this repository knows nothing about.
# --------------------------------------------------------------------------

resource "tfe_variable_set" "aws" {
  organization = var.organization
  name         = "${var.workspace_prefix}-aws"
  description  = "AWS credentials for the crypto-kb workspaces."
  global       = false
}

resource "tfe_project_variable_set" "aws" {
  variable_set_id = tfe_variable_set.aws.id
  project_id      = tfe_project.crypto_kb.id
}

# Written only when supplied. The recommended path is OIDC — leave these empty,
# apply, then configure dynamic credentials so no long-lived key exists at all
# (see README.md). Static keys are the fallback, not the default.
resource "tfe_variable" "aws_access_key_id" {
  count = var.aws_access_key_id == "" ? 0 : 1

  variable_set_id = tfe_variable_set.aws.id
  category        = "env"
  key             = "AWS_ACCESS_KEY_ID"
  value           = var.aws_access_key_id
  sensitive       = true
}

resource "tfe_variable" "aws_secret_access_key" {
  count = var.aws_secret_access_key == "" ? 0 : 1

  variable_set_id = tfe_variable_set.aws.id
  category        = "env"
  key             = "AWS_SECRET_ACCESS_KEY"
  value           = var.aws_secret_access_key
  sensitive       = true
}

resource "tfe_variable" "aws_default_region" {
  variable_set_id = tfe_variable_set.aws.id
  category        = "env"
  key             = "AWS_DEFAULT_REGION"
  value           = var.aws_region
}

# --------------------------------------------------------------------------
# Notifications
# --------------------------------------------------------------------------

resource "tfe_notification_configuration" "prod_runs" {
  count = var.notification_email == "" ? 0 : 1

  name             = "${var.workspace_prefix}-prod-runs"
  enabled          = true
  destination_type = "email"
  email_addresses  = [var.notification_email]
  workspace_id     = tfe_workspace.this["prod"].id

  # An apply that errored halfway has left AWS in a state nobody has looked
  # at, and a plan needing approval is blocking the index from tracking the
  # corpus. Both are worth an interruption; a successful apply is not.
  triggers = ["run:errored", "run:needs_attention"]
}
