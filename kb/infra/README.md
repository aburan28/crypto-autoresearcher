# AWS infrastructure

`terraform/` describes the AWS resources for the knowledge-base pipeline. It
is intentionally not applied by CI.

## Polynomial working store

The Terraform configuration creates a private, TLS-encrypted Redis OSS
ElastiCache replication group for serialized Gröbner bases and summation
polynomials. It has:

- a primary and replica across private subnets, with automatic failover;
- AUTH-token authentication and encryption at rest/in transit;
- `maxmemory-policy=noeviction`, so capacity pressure fails writes instead of
  silently dropping a polynomial;
- seven days of automatic snapshots by default;
- a security-group rule allowing Redis traffic only from the supplied worker
  security group.

ElastiCache is a working store, not the source of truth. Persist canonical
polynomial artifacts in the versioned S3 corpus before or alongside caching
them. Use stable key namespaces such as:

```text
grobner:v1:<curve-id>:<parameter-hash>:<basis-hash>
summation-polynomial:v1:<curve-id>:<parameter-hash>:<polynomial-hash>
```

Apply with the VPC, two private subnets, an application security group, and an
AUTH token supplied out of band:

```bash
cd kb/infra/terraform
export TF_VAR_cache_auth_token='use-a-secret-manager-generated-token'
terraform init
terraform plan \
  -var='cache_vpc_id=vpc-...' \
  -var='cache_private_subnet_ids=["subnet-...","subnet-..."]' \
  -var='cache_client_security_group_id=sg-...'
terraform apply
```

Do not put the AUTH token in a committed `.tfvars` file or in a connection URL.
The `polynomial_cache_primary_endpoint` and
`polynomial_cache_reader_endpoint` outputs are hostnames; clients should use
TLS, port `6379`, and the token separately.
