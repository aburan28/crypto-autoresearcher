# --------------------------------------------------------------------------
# Polynomial working store
# --------------------------------------------------------------------------
#
# Redis OSS is used as a bounded, low-latency working store for serialized
# Gröbner bases and summation polynomials. The source artifacts remain in S3;
# ElastiCache snapshots and replicas improve recovery but are not the
# authoritative copy.

variable "cache_vpc_id" {
  type        = string
  description = "VPC ID containing the private subnets and the cache clients."
}

variable "cache_private_subnet_ids" {
  type        = list(string)
  description = "At least two private subnet IDs in distinct availability zones."

  validation {
    condition     = length(var.cache_private_subnet_ids) >= 2
    error_message = "cache_private_subnet_ids must contain at least two subnets for Multi-AZ failover."
  }
}

variable "cache_client_security_group_id" {
  type        = string
  description = "Security group ID of the worker/application clients allowed to reach Redis."
}

variable "cache_auth_token" {
  type        = string
  sensitive   = true
  description = "Redis AUTH token (16-128 characters). Supply through TF_VAR_cache_auth_token or a tfvars file excluded from git."

  validation {
    condition     = length(var.cache_auth_token) >= 16 && length(var.cache_auth_token) <= 128
    error_message = "cache_auth_token must be between 16 and 128 characters."
  }
}

variable "cache_node_type" {
  type        = string
  default     = "cache.t4g.small"
  description = "ElastiCache node type for the polynomial working store."
}

variable "cache_engine_version" {
  type        = string
  default     = "7.2"
  description = "Redis OSS engine version."
}

variable "cache_num_nodes" {
  type        = number
  default     = 2
  description = "Number of cache nodes. Two enables a primary and a replica for automatic failover."

  validation {
    condition     = var.cache_num_nodes >= 2
    error_message = "cache_num_nodes must be at least 2 when automatic failover is enabled."
  }
}

variable "cache_snapshot_retention_days" {
  type        = number
  default     = 7
  description = "Number of days to retain automatic Redis snapshots."

  validation {
    condition     = var.cache_snapshot_retention_days >= 0 && var.cache_snapshot_retention_days <= 35
    error_message = "cache_snapshot_retention_days must be between 0 and 35."
  }
}

resource "aws_elasticache_subnet_group" "polynomial" {
  name        = "${local.name}-polynomial"
  description = "Private subnets for the Gröbner basis and summation polynomial Redis store."
  subnet_ids  = var.cache_private_subnet_ids
}

resource "aws_security_group" "polynomial_cache" {
  name        = "${local.name}-polynomial-cache"
  description = "Private Redis access for polynomial workers"
  vpc_id      = var.cache_vpc_id

  ingress {
    description     = "Redis from the polynomial workers"
    protocol        = "tcp"
    from_port       = 6379
    to_port         = 6379
    security_groups = [var.cache_client_security_group_id]
  }

  egress {
    description = "Allow Redis response traffic"
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${local.name}-polynomial-cache"
    Purpose = "grobner-bases-and-summation-polynomials"
  }
}

resource "aws_elasticache_parameter_group" "polynomial" {
  name   = "${local.name}-redis7"
  family = "redis7"

  # Never silently evict a basis or polynomial while workers are using it.
  # Capacity exhaustion should be observable as a failed write instead.
  parameter {
    name  = "maxmemory-policy"
    value = "noeviction"
  }
}

resource "aws_elasticache_replication_group" "polynomial" {
  replication_group_id = "${local.name}-poly"
  description          = "Redis OSS working store for Gröbner bases and summation polynomials"

  engine               = "redis"
  engine_version       = var.cache_engine_version
  node_type            = var.cache_node_type
  num_cache_clusters    = var.cache_num_nodes
  port                 = 6379
  parameter_group_name  = aws_elasticache_parameter_group.polynomial.name
  subnet_group_name     = aws_elasticache_subnet_group.polynomial.name
  security_group_ids    = [aws_security_group.polynomial_cache.id]
  auth_token            = var.cache_auth_token

  automatic_failover_enabled = true
  multi_az_enabled            = true
  transit_encryption_enabled  = true
  at_rest_encryption_enabled  = true

  snapshot_retention_limit = var.cache_snapshot_retention_days
  snapshot_window          = "03:00-04:00"
  maintenance_window       = "sun:04:00-sun:05:00"
  apply_immediately         = false

  tags = {
    Name    = "${local.name}-polynomial"
    Purpose = "grobner-bases-and-summation-polynomials"
  }
}

output "polynomial_cache_primary_endpoint" {
  description = "TLS Redis endpoint for writes and primary reads."
  value       = aws_elasticache_replication_group.polynomial.primary_endpoint_address
}

output "polynomial_cache_reader_endpoint" {
  description = "TLS Redis reader endpoint for read-heavy polynomial workloads."
  value       = aws_elasticache_replication_group.polynomial.reader_endpoint_address
}

output "polynomial_cache_port" {
  description = "TLS Redis port."
  value       = aws_elasticache_replication_group.polynomial.port
}

output "polynomial_cache_security_group_id" {
  description = "Security group attached to the polynomial Redis replication group."
  value       = aws_security_group.polynomial_cache.id
}
