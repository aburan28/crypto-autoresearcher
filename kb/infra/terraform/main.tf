# S3 -> EventBridge -> SQS -> ECS worker, plus the IAM boundaries from the
# plan's Phase 14. Written to be read as well as applied: the interesting
# decisions are the ones that keep a derived index from becoming a second
# source of truth, and the ones that keep agents away from the write path.
#
# Terraform settings are in cloud.tf and versions.tf; inputs in variables.tf.

locals {
  name = "crypto-kb-${var.environment}"

  # The bucket is either created here or looked up. Everything downstream
  # references these, so neither branch is special-cased more than once.
  bucket_id  = var.create_bucket ? aws_s3_bucket.corpus[0].id : data.aws_s3_bucket.corpus[0].id
  bucket_arn = var.create_bucket ? aws_s3_bucket.corpus[0].arn : data.aws_s3_bucket.corpus[0].arn

  alarm_actions = var.alarm_topic_arn == "" ? [] : [var.alarm_topic_arn]
}

# --------------------------------------------------------------------------
# Corpus bucket
# --------------------------------------------------------------------------

data "aws_s3_bucket" "corpus" {
  count  = var.create_bucket ? 0 : 1
  bucket = var.bucket_name
}

resource "aws_s3_bucket" "corpus" {
  count  = var.create_bucket ? 1 : 0
  bucket = var.bucket_name
}

# Versioning is not optional here. The manifest records the version id it
# indexed, which is what makes "which bytes produced this chunk" answerable
# after the object has been overwritten.
resource "aws_s3_bucket_versioning" "corpus" {
  count  = var.create_bucket ? 1 : 0
  bucket = aws_s3_bucket.corpus[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "corpus" {
  count                   = var.create_bucket ? 1 : 0
  bucket                  = aws_s3_bucket.corpus[0].id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "corpus" {
  count  = var.create_bucket ? 1 : 0
  bucket = aws_s3_bucket.corpus[0].id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_notification" "corpus" {
  bucket      = local.bucket_id
  eventbridge = true
}

# --------------------------------------------------------------------------
# Queue
# --------------------------------------------------------------------------

resource "aws_sqs_queue" "dlq" {
  name                      = "${local.name}-ingest-dlq"
  message_retention_seconds = 1209600 # 14 days: long enough to notice and replay
  sqs_managed_sse_enabled   = true
}

resource "aws_sqs_queue" "ingest" {
  name = "${local.name}-ingest"

  visibility_timeout_seconds = var.queue_visibility_timeout_seconds
  message_retention_seconds  = 345600
  receive_wait_time_seconds  = 20 # long polling
  sqs_managed_sse_enabled    = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = var.max_receive_count
  })
}

resource "aws_sqs_queue_redrive_allow_policy" "dlq" {
  queue_url = aws_sqs_queue.dlq.id
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue"
    sourceQueueArns   = [aws_sqs_queue.ingest.arn]
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
      bucket = { name = [local.bucket_id] }
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
    resources = ["${local.bucket_arn}/${var.corpus_prefix}*"]
  }
  statement {
    actions   = ["s3:ListBucket"]
    resources = [local.bucket_arn]
  }
  statement {
    actions = ["s3:PutObject", "s3:DeleteObject"]
    resources = [
      "${local.bucket_arn}/knowledge/normalized/*",
      "${local.bucket_arn}/knowledge/manifests/*",
      "${local.bucket_arn}/knowledge/stats/*",
      "${local.bucket_arn}/knowledge/rejected/*",
    ]
  }
  statement {
    actions   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
    resources = [aws_sqs_queue.ingest.arn]
  }
}

resource "aws_iam_role_policy" "worker" {
  name   = "${local.name}-worker"
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
    resources = ["${local.bucket_arn}/knowledge/normalized/*"]
  }
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.qdrant_api_key.arn]
  }
}

resource "aws_iam_role_policy" "mcp" {
  name   = "${local.name}-mcp"
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
  threshold           = var.queue_age_alarm_seconds
  comparison_operator = "GreaterThanThreshold"
  dimensions          = { QueueName = aws_sqs_queue.ingest.name }
  alarm_description   = "Ingestion is behind: the index no longer reflects the corpus."
  alarm_actions       = local.alarm_actions
  ok_actions          = local.alarm_actions
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
  alarm_actions       = local.alarm_actions
}
