# Values for the crypto-kb-dev workspace.
#
# In the VCS-driven workflow these are set as HCP Terraform workspace
# variables, not read from this file — a workspace variable is auditable and a
# tfvars file in a repository is not. The file is here so the CLI-driven
# workflow (`terraform plan -var-file=workspaces/dev.tfvars`) and code review
# see the same numbers.

environment   = "dev"
aws_region    = "us-west-2"
bucket_name   = "crypto-autoresearcher-dev"
create_bucket = true

# Dev parses the same documents as production, so the timeout is the same:
# a shorter one here would make dev fail on exactly the large PDFs that are
# worth testing against.
queue_visibility_timeout_seconds = 900
max_receive_count                = 5

# Louder than production on purpose — in dev a backlog means something is
# broken, not that the corpus grew.
queue_age_alarm_seconds = 900
