# S3 -> EventBridge -> SQS -> ECS worker, plus the IAM boundaries from the
# plan's Phase 14. Written to be read as well as applied: the interesting
# decisions are the ones that keep a derived index from becoming a second
# source of truth, and the ones that keep agents away from the write path.
#
# Not applied by CI. Review it before running it against a real account.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "bucket_name" {
  type        = string
  default     = "crypto-autoresearcher"
  description = "Corpus bucket. The source of truth; the index is derived from it."
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "corpus_prefix" {
  type        = string
  default     = "knowledge/source/"
  description = "Only this prefix produces ingestion events."
}

locals {
  name = "crypto-kb-${var.environment}"
}

# --------------------------------------------------------------------------
# Corpus bucket
# --------------------------------------------------------------------------

resource "aws_s3_bucket" "corpus" {
  bucket = var.bucket_name
}

# Versioning is not optional here. The manifest records the version id it
# indexed, which is what makes "which bytes produced this chunk" answerable
# after the object has been overwritten.
resource "aws_s3_bucket_versioning" "corpus" {
  bucket = aws_s3_bucket.corpus.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "corpus" {
  bucket                  = aws_s3_bucket.corpus.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "corpus" {
  bucket = aws_s3_bucket.corpus.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_notification" "corpus" {
  bucket      = aws_s3_bucket.corpus.id
  eventbridge = true
}

# --------------------------------------------------------------------------
# Queue
# --------------------------------------------------------------------------

resource "aws_sqs_queue" "dlq" {
  name                      = "${local.name}-ingest-dlq"
  message_retention_seconds = 1209600 # 14 days: long enough to notice and replay
}

resource "aws_sqs_queue" "ingest" {
  name = "${local.name}-ingest"

  # Docling on a large mathematical PDF is minutes of CPU. The visibility
  # timeout has to exceed the slowest document, or the queue redelivers work
  # that is still running and the worker duplicates effort.
  visibility_timeout_seconds = 900
  message_retention_seconds  = 345600
  receive_wait_time_seconds  = 20 # long polling

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 5
  })
}

resource "aws_sqs_queue_policy" "ingest" {
  queue_url = aws_sqs_queue.ingest.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "events.amazonaws.com" }
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.ingest.arn
      Condition = {
        ArnEquals = { "aws:SourceArn" = aws_cloudwatch_event_rule.corpus_changes.arn }
      }
    }]
  })
}

# Only the source prefix produces events. Without this filter the pipeline's
# own writes to normalized/ and manifests/ would re-enter the queue and the
# worker would ingest its own output forever.
resource "aws_cloudwatch_event_rule" "corpus_changes" {
  name        = "${local.name}-corpus-changes"
  description = "S3 object changes under the corpus source prefix"
  event_pattern = jsonencode({
    source        = ["aws.s3"]
    "detail-type" = ["Object Created", "Object Deleted"]
    detail = {
      bucket = { name = [aws_s3_bucket.corpus.id] }
      object = { key = [{ prefix = var.corpus_prefix }] }
    }
  })
}

resource "aws_cloudwatch_event_target" "to_sqs" {
  rule = aws_cloudwatch_event_rule.corpus_changes.name
  arn  = aws_sqs_queue.ingest.arn
}

# --------------------------------------------------------------------------
# IAM: the two roles are deliberately asymmetric
# --------------------------------------------------------------------------

data "aws_iam_policy_document" "ecs_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "worker" {
  name               = "${local.name}-worker"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

# The worker reads sources and writes only derived artifacts. It cannot write
# to source/ -- an ingestion bug must not be able to modify the corpus it is
# indexing.
data "aws_iam_policy_document" "worker" {
  statement {
    actions   = ["s3:GetObject", "s3:GetObjectVersion"]
    resources = ["${aws_s3_bucket.corpus.arn}/${var.corpus_prefix}*"]
  }
  statement {
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.corpus.arn]
  }
  statement {
    actions = ["s3:PutObject", "s3:DeleteObject"]
    resources = [
      "${aws_s3_bucket.corpus.arn}/knowledge/normalized/*",
      "${aws_s3_bucket.corpus.arn}/knowledge/manifests/*",
      "${aws_s3_bucket.corpus.arn}/knowledge/stats/*",
      "${aws_s3_bucket.corpus.arn}/knowledge/rejected/*",
    ]
  }
  statement {
    actions   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
    resources = [aws_sqs_queue.ingest.arn]
  }
}

resource "aws_iam_role_policy" "worker" {
  role   = aws_iam_role.worker.id
  policy = data.aws_iam_policy_document.worker.json
}

resource "aws_iam_role" "mcp" {
  name               = "${local.name}-mcp"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

# The retrieval service has no S3 write access at all, and no queue access.
# Read access is bounded to normalized artifacts: search results carry an
# s3:// URI, and following one should never require the reader's credentials
# to be able to change anything.
data "aws_iam_policy_document" "mcp" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.corpus.arn}/knowledge/normalized/*"]
  }
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.qdrant_api_key.arn]
  }
}

resource "aws_iam_role_policy" "mcp" {
  role   = aws_iam_role.mcp.id
  policy = data.aws_iam_policy_document.mcp.json
}

# Agents get neither role. They reach the corpus only through the MCP
# service, which exposes no write tool -- see src/crypto_kb/mcp/server.py.

resource "aws_secretsmanager_secret" "qdrant_api_key" {
  name = "${local.name}/qdrant-api-key"
}

# --------------------------------------------------------------------------
# Alarms: the failures that are silent without them
# --------------------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "queue_backlog" {
  alarm_name          = "${local.name}-queue-age"
  namespace           = "AWS/SQS"
  metric_name         = "ApproximateAgeOfOldestMessage"
  statistic           = "Maximum"
  period              = 300
  evaluation_periods  = 2
  threshold           = 3600
  comparison_operator = "GreaterThanThreshold"
  dimensions          = { QueueName = aws_sqs_queue.ingest.name }
  alarm_description   = "Ingestion is behind: the index no longer reflects the corpus."
}

resource "aws_cloudwatch_metric_alarm" "dlq_not_empty" {
  alarm_name          = "${local.name}-dlq"
  namespace           = "AWS/SQS"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  statistic           = "Maximum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 0
  comparison_operator = "GreaterThanThreshold"
  dimensions          = { QueueName = aws_sqs_queue.dlq.name }
  alarm_description   = "Documents failed ingestion repeatedly and are not in the index."
}

output "queue_url" {
  value = aws_sqs_queue.ingest.id
}

output "worker_role_arn" {
  value = aws_iam_role.worker.arn
}

output "mcp_role_arn" {
  value = aws_iam_role.mcp.arn
}
