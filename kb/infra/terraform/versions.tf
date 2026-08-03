terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  # Applied to everything this configuration creates, so a stray resource can
  # be traced back to the workspace that made it — and so the derived index's
  # infrastructure is distinguishable from the research program's own.
  default_tags {
    tags = {
      Project     = "crypto-kb"
      Environment = var.environment
      ManagedBy   = "terraform"
      Repository  = "aburan28/crypto-autoresearcher"
    }
  }
}
