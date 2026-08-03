variable "organization" {
  type        = string
  description = "HCP Terraform organization name. Must already exist."
}

variable "hostname" {
  type        = string
  description = "app.terraform.io, or your Terraform Enterprise hostname."
  default     = "app.terraform.io"
}

variable "project_name" {
  type        = string
  description = "Project the workspaces live in."
  default     = "crypto-kb"
}

variable "workspace_prefix" {
  type        = string
  description = "Workspace names are <prefix>-dev and <prefix>-prod."
  default     = "crypto-kb"
}

variable "working_directory" {
  type        = string
  description = <<-EOT
    Directory the runs execute in, relative to the repository root. Also used
    as the trigger prefix: without it, every commit to the research ledger
    queues a plan that cannot differ.
  EOT
  default     = "kb/infra/terraform"
}

variable "terraform_version" {
  type        = string
  description = "Pinned so a workspace does not silently move to a new Terraform release."
  default     = "1.9.8"
}

variable "aws_region" {
  type        = string
  default     = "us-west-2"
  description = "Region for the workspaces' AWS credentials and resources."
}

variable "corpus_bucket" {
  type        = string
  description = "Production corpus bucket. dev gets '<name>-dev' and creates it."
  default     = "crypto-autoresearcher"
}

# -- VCS connection --------------------------------------------------------

variable "vcs_repo_identifier" {
  type        = string
  description = <<-EOT
    "org/repo" to drive runs from version control. Empty leaves the workspaces
    CLI-driven, which is the right starting point: it works before any VCS
    connection exists and can be attached later without recreating anything.
  EOT
  default     = ""
}

variable "vcs_branch" {
  type        = string
  description = "Branch that triggers runs. Empty means the repository default."
  default     = ""
}

variable "vcs_oauth_token_id" {
  type        = string
  description = <<-EOT
    OAuth token id of the VCS connection (ot-xxxxxxxx), from the organization's
    VCS Providers settings. Required when vcs_repo_identifier is set.
  EOT
  default     = ""
}

# -- credentials -----------------------------------------------------------

variable "aws_access_key_id" {
  type        = string
  description = <<-EOT
    Fallback only. Prefer dynamic credentials (OIDC): leave this empty, apply,
    then follow the OIDC section of README.md so no long-lived AWS key exists.
    Supplying it writes a sensitive variable into the variable set.
  EOT
  default     = ""
  sensitive   = true
}

variable "aws_secret_access_key" {
  type        = string
  description = "Fallback only. See aws_access_key_id."
  default     = ""
  sensitive   = true
}

variable "notification_email" {
  type        = string
  description = "Notified on errored and needs-attention runs in prod. Empty disables."
  default     = ""
}
