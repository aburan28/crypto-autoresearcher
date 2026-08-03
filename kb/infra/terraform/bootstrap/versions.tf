# Local state on purpose. This configuration creates the workspaces, so it
# cannot run inside one. See the note at the top of main.tf: every resource
# here is importable from the HCP Terraform API, so the state file is
# convenience rather than a record that must survive.
terraform {
  required_version = ">= 1.6"

  required_providers {
    tfe = {
      source  = "hashicorp/tfe"
      version = "~> 0.79"
    }
  }
}

provider "tfe" {
  hostname = var.hostname
  # Token comes from TFE_TOKEN, or from the credentials `terraform login`
  # writes. It is deliberately not a variable: a token in a tfvars file is a
  # token in a shell history and, eventually, in a repository.
}
