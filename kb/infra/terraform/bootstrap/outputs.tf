output "project_id" {
  description = "HCP Terraform project holding the crypto-kb workspaces."
  value       = tfe_project.crypto_kb.id
}

output "workspace_names" {
  description = "Values for TF_WORKSPACE when running the root module."
  value       = { for key, workspace in tfe_workspace.this : key => workspace.name }
}

output "workspace_ids" {
  description = "Needed to configure dynamic credentials or attach further variable sets."
  value       = { for key, workspace in tfe_workspace.this : key => workspace.id }
}

output "variable_set_id" {
  description = "AWS credential variable set, scoped to this project."
  value       = tfe_variable_set.aws.id
}

output "next_steps" {
  description = "What to run once this configuration has applied."
  value       = <<-EOT
    Workspaces created. To use them:

      export TF_CLOUD_ORGANIZATION=${var.organization}
      export TF_WORKSPACE=${tfe_workspace.this["dev"].name}
      cd ${abspath(path.module)}/..
      terraform login   # once per machine
      terraform init
      terraform plan

    If aws_access_key_id was left empty (the recommended path), configure
    dynamic credentials before the first plan — see the OIDC section of
    ../README.md. Until then the plan will fail on missing AWS credentials,
    which is the correct failure: no long-lived key was created.
  EOT
}
