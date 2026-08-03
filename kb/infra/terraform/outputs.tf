# These are the values the running services need. Everything here is
# non-sensitive on purpose: the Qdrant API key lives in Secrets Manager and is
# read at runtime, so it never passes through Terraform state.

output "queue_url" {
  description = "Set as CRYPTO_KB_SQS_QUEUE_URL on the ingestion worker."
  value       = aws_sqs_queue.ingest.id
}

output "dlq_url" {
  description = "Dead-letter queue. Non-empty means documents are not in the index."
  value       = aws_sqs_queue.dlq.id
}

output "bucket_name" {
  description = "Set as CRYPTO_KB_S3_BUCKET. The corpus, and the source of truth."
  value       = local.bucket_id
}

output "worker_role_arn" {
  description = "Task role for `crypto-kb worker`. Reads sources, writes only derived artifacts."
  value       = aws_iam_role.worker.arn
}

output "mcp_role_arn" {
  description = "Task role for `crypto-kb mcp`. No S3 writes, no queue access."
  value       = aws_iam_role.mcp.arn
}

output "qdrant_api_key_secret_arn" {
  description = "Secret the MCP service reads its Qdrant credential from."
  value       = aws_secretsmanager_secret.qdrant_api_key.arn
}

output "service_environment" {
  description = "The CRYPTO_KB_* settings implied by this workspace, for the task definitions."
  value = {
    CRYPTO_KB_STORE_BACKEND = "s3"
    CRYPTO_KB_S3_BUCKET     = local.bucket_id
    CRYPTO_KB_AWS_REGION    = var.aws_region
    CRYPTO_KB_SQS_QUEUE_URL = aws_sqs_queue.ingest.id
    CRYPTO_KB_COLLECTION    = "crypto_knowledge_v1"
  }
}
