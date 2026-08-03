# Values for the crypto-kb-prod workspace.
#
# See the note in dev.tfvars: in the VCS-driven workflow these live as HCP
# Terraform workspace variables. This file is the reviewable copy.

environment = "prod"
aws_region  = "us-west-2"
bucket_name = "crypto-autoresearcher"

# False on purpose. This bucket holds the research corpus — the source of
# truth for everything the index derives. It is not created or destroyed by
# this configuration; Terraform looks it up and attaches notifications to it.
#
# Consequence worth knowing: versioning, encryption, and the public-access
# block are then NOT managed here, because managing them would mean owning the
# bucket. Versioning in particular has to already be on — manifests record the
# S3 version id they indexed, and that is what makes "which bytes produced
# this chunk" answerable after an object is overwritten. Check before the
# first apply:
#
#   aws s3api get-bucket-versioning --bucket crypto-autoresearcher
create_bucket = false

queue_visibility_timeout_seconds = 900
max_receive_count                = 5
queue_age_alarm_seconds          = 3600
