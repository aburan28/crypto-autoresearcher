terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = { Application = "research-kb", ManagedBy = "terraform" }
  }
}

variable "region" {
  type    = string
  default = "us-west-2"
}
variable "vpc_id" { type = string }
variable "public_subnet_id" { type = string }
variable "hostname" {
  type        = string
  description = "DNS name controlled by the operator; point its A record to public_ip."
  validation {
    condition     = can(regex("^[a-zA-Z0-9][a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.hostname))
    error_message = "Supply a public DNS hostname for automatic HTTPS."
  }
}
variable "bucket_name" {
  type        = string
  description = "New globally unique private bucket for inbox bundles and backups."
}
variable "instance_type" {
  type    = string
  default = "t3.large"
}
variable "data_gb" {
  type    = number
  default = 100
}
variable "ssh_key_name" {
  type        = string
  default     = null
  description = "Optional recovery key; SSH ingress stays closed. Use Systems Manager."
}

data "aws_subnet" "selected" { id = var.public_subnet_id }
data "aws_ssm_parameter" "ubuntu" {
  name = "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id"
}
data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "library" { bucket = var.bucket_name }
resource "aws_s3_bucket_versioning" "library" {
  bucket = aws_s3_bucket.library.id
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_public_access_block" "library" {
  bucket                  = aws_s3_bucket.library.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_server_side_encryption_configuration" "library" {
  bucket = aws_s3_bucket.library.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}
resource "aws_s3_bucket_policy" "tls" {
  bucket = aws_s3_bucket.library.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Sid = "DenyInsecureTransport", Effect = "Deny", Principal = "*", Action = "s3:*",
      Resource = [aws_s3_bucket.library.arn, "${aws_s3_bucket.library.arn}/*"],
    Condition = { Bool = { "aws:SecureTransport" = "false" } } }]
  })
}

# Populate the value out of band. Client token secrets never enter Terraform state.
resource "aws_secretsmanager_secret" "auth" {
  name                    = "research-kb/auth"
  recovery_window_in_days = 7
}

resource "aws_ecr_repository" "application" {
  name                 = "research-kb"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
  encryption_configuration { encryption_type = "AES256" }
}

resource "aws_iam_role" "host" {
  name = "research-kb-host"
  assume_role_policy = jsonencode({ Version = "2012-10-17", Statement = [{
    Effect = "Allow", Action = "sts:AssumeRole", Principal = { Service = "ec2.amazonaws.com" }
  }] })
}
resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.host.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
resource "aws_iam_role_policy" "host" {
  role = aws_iam_role.host.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [
    { Effect = "Allow", Action = ["s3:ListBucket"], Resource = aws_s3_bucket.library.arn },
    { Effect = "Allow", Action = ["s3:GetObject"], Resource = ["${aws_s3_bucket.library.arn}/inbox/*", "${aws_s3_bucket.library.arn}/backups/*", "${aws_s3_bucket.library.arn}/objects/*"] },
    { Effect = "Allow", Action = ["s3:PutObject"], Resource = ["${aws_s3_bucket.library.arn}/backups/*", "${aws_s3_bucket.library.arn}/objects/*"] },
    { Effect = "Allow", Action = ["secretsmanager:GetSecretValue"], Resource = aws_secretsmanager_secret.auth.arn },
    { Effect = "Allow", Action = ["ecr:GetAuthorizationToken"], Resource = "*" },
    { Effect = "Allow", Action = ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer", "ecr:BatchCheckLayerAvailability"], Resource = aws_ecr_repository.application.arn }
  ] })
}
resource "aws_iam_instance_profile" "host" {
  name = "research-kb-host"
  role = aws_iam_role.host.name
}

resource "aws_security_group" "host" {
  name   = "research-kb-https"
  vpc_id = var.vpc_id
  ingress {
    description = "HTTPS for local and cloud clients"
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "ACME validation and HTTPS redirects"
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ebs_volume" "data" {
  availability_zone = data.aws_subnet.selected.availability_zone
  size              = var.data_gb
  type              = "gp3"
  encrypted         = true
  tags              = { Name = "research-kb-data" }
  lifecycle { prevent_destroy = true }
}

variable "image_tag" {
  type        = string
  description = "Immutable ECR image tag to publish after apply, such as a Git commit."
}

resource "aws_instance" "host" {
  ami                         = data.aws_ssm_parameter.ubuntu.value
  instance_type               = var.instance_type
  subnet_id                   = var.public_subnet_id
  vpc_security_group_ids      = [aws_security_group.host.id]
  iam_instance_profile        = aws_iam_instance_profile.host.name
  key_name                    = var.ssh_key_name
  associate_public_ip_address = true
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }
  root_block_device {
    volume_size = 30
    volume_type = "gp3"
    encrypted   = true
  }
  user_data_replace_on_change = true
  user_data = templatefile("${path.module}/user-data.sh.tftpl", {
    region        = var.region
    hostname      = var.hostname
    bucket        = aws_s3_bucket.library.id
    auth_secret   = aws_secretsmanager_secret.auth.arn
    image         = "${aws_ecr_repository.application.repository_url}:${var.image_tag}"
    registry      = split("/", aws_ecr_repository.application.repository_url)[0]
    volume_serial = replace(aws_ebs_volume.data.id, "-", "")
    compose       = base64encode(file("${path.module}/../../compose.yaml"))
    compose_aws   = base64encode(file("${path.module}/../../compose.aws.yaml"))
    caddy         = base64encode(file("${path.module}/../../Caddyfile"))
  })
  tags = { Name = "research-kb" }
}
resource "aws_volume_attachment" "data" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.data.id
  instance_id = aws_instance.host.id
}
resource "aws_eip" "host" {
  domain   = "vpc"
  instance = aws_instance.host.id
}

output "instance_id" { value = aws_instance.host.id }
output "public_ip" { value = aws_eip.host.public_ip }
output "mcp_url" { value = "https://${var.hostname}/mcp" }
output "repository_url" { value = aws_ecr_repository.application.repository_url }
output "auth_secret_arn" { value = aws_secretsmanager_secret.auth.arn }
output "bucket" { value = aws_s3_bucket.library.id }
