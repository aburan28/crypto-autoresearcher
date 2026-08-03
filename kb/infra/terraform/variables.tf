variable "bucket_name" {
  type        = string
  description = "Corpus bucket. The source of truth; the index is derived from it."
  default     = "crypto-autoresearcher"
}

variable "environment" {
  type        = string
  description = "Deployment environment. Names every resource and tags them all."
  default     = "dev"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,15}$", var.environment))
    error_message = "environment must be lowercase alphanumeric with hyphens, 2-16 characters."
  }
}

variable "aws_region" {
  type        = string
  description = "Region for the corpus bucket, queue, and workers."
  default     = "us-west-2"
}

variable "corpus_prefix" {
  type        = string
  description = "Only this prefix produces ingestion events."
  default     = "knowledge/source/"

  validation {
    # A prefix that does not end in "/" matches sibling keys by accident, and
    # one that starts with "/" matches nothing at all in S3.
    condition     = endswith(var.corpus_prefix, "/") && !startswith(var.corpus_prefix, "/")
    error_message = "corpus_prefix must end with '/' and must not start with '/'."
  }
}

variable "create_bucket" {
  type        = bool
  description = <<-EOT
    Whether this configuration owns the corpus bucket.

    Set false in every environment that points at a bucket created elsewhere;
    the bucket is then looked up instead. The bucket holds the source of
    truth, and two workspaces both believing they own it is how a corpus gets
    removed by a `terraform destroy` in the one nobody thought was
    authoritative.
  EOT
  default     = false
}

variable "queue_visibility_timeout_seconds" {
  type        = number
  description = <<-EOT
    SQS visibility timeout. Must exceed the slowest single-document parse:
    Docling on a large mathematical PDF is minutes of CPU, and a timeout
    shorter than that makes the queue redeliver work that is still running.
  EOT
  default     = 900

  validation {
    condition     = var.queue_visibility_timeout_seconds >= 300 && var.queue_visibility_timeout_seconds <= 43200
    error_message = "visibility timeout must be between 300 and 43200 seconds."
  }
}

variable "max_receive_count" {
  type        = number
  description = "Delivery attempts before a message moves to the dead-letter queue."
  default     = 5

  validation {
    condition     = var.max_receive_count >= 1 && var.max_receive_count <= 20
    error_message = "max_receive_count must be between 1 and 20."
  }
}

variable "queue_age_alarm_seconds" {
  type        = number
  description = "Oldest-message age that means the index no longer reflects the corpus."
  default     = 3600
}

variable "alarm_topic_arn" {
  type        = string
  description = "Optional SNS topic for the queue-backlog and DLQ alarms. Empty means no notification."
  default     = ""
}
