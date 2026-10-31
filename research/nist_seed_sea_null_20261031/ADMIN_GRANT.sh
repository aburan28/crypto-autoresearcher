#!/usr/bin/env bash
# Run as an ADMIN of AWS account 104186811093 (not as user/claude), from this
# directory. Grants the Claude session's IAM user what the real-field SEA null
# needs, then builds and pushes its task image. Each step prints what it changed.
# Nothing here contains a secret.
set -euo pipefail
export AWS_REGION=us-east-2
ACCT=104186811093
PRINCIPAL=arn:aws:iam::$ACCT:user/claude
CLUSTER=isolab
BUCKET=isolab-results-$ACCT-$AWS_REGION
REPO=isolab/tasks
SESSION_EGRESS_CIDR=160.79.106.18/32   # the Claude cloud session's current egress IP

# 1. IAM: cluster lookup, ECR push/pull on isolab/tasks, result reads under runs/.
cat > /tmp/isolab-claude-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": ["eks:DescribeCluster"],
     "Resource": "arn:aws:eks:$AWS_REGION:$ACCT:cluster/$CLUSTER"},
    {"Effect": "Allow", "Action": ["ecr:GetAuthorizationToken"], "Resource": "*"},
    {"Effect": "Allow",
     "Action": ["ecr:DescribeRepositories", "ecr:DescribeImages", "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability", "ecr:GetDownloadUrlForLayer",
                "ecr:InitiateLayerUpload", "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload", "ecr:PutImage"],
     "Resource": "arn:aws:ecr:$AWS_REGION:$ACCT:repository/$REPO"},
    {"Effect": "Allow", "Action": ["s3:GetObject"],
     "Resource": "arn:aws:s3:::$BUCKET/runs/*"},
    {"Effect": "Allow", "Action": ["s3:ListBucket"],
     "Resource": "arn:aws:s3:::$BUCKET",
     "Condition": {"StringLike": {"s3:prefix": ["runs/*"]}}}
  ]
}
EOF
aws iam put-user-policy --user-name claude --policy-name isolab-sea-null \
  --policy-document file:///tmp/isolab-claude-policy.json
echo "step 1: inline policy isolab-sea-null attached to user/claude"

# 2. EKS RBAC: map the principal to the existing isolab:submitters group
#    (workloads.yaml / remote/readiness-rbac.yaml bind that group in namespace isolab).
if aws eks describe-access-entry --cluster-name $CLUSTER --principal-arn $PRINCIPAL >/dev/null 2>&1; then
  aws eks update-access-entry --cluster-name $CLUSTER --principal-arn $PRINCIPAL \
    --kubernetes-groups isolab:submitters
else
  aws eks create-access-entry --cluster-name $CLUSTER --principal-arn $PRINCIPAL \
    --type STANDARD --kubernetes-groups isolab:submitters
fi
echo "step 2: access entry -> isolab:submitters"

# 3. Network route to the API server. The cluster API is private. This step adds
#    the session's egress IP to the PUBLIC endpoint allow-list, keeping the
#    private endpoint and every existing CIDR. Caution: that IP is a shared
#    cloud egress, so other tenants behind it can reach the endpoint. They still
#    need IAM auth plus RBAC. Skip this step if you route the session another
#    way (VPN, bastion) or prefer not to open the endpoint.
read -r -p "Add $SESSION_EGRESS_CIDR to the public API allow-list? [y/N] " ok
if [[ $ok == y ]]; then
  vpc=$(aws eks describe-cluster --name $CLUSTER --query cluster.resourcesVpcConfig --output json)
  if jq -e '.endpointPublicAccess and (.publicAccessCidrs | index("0.0.0.0/0"))' <<<"$vpc" >/dev/null; then
    echo "step 3: public endpoint already open to 0.0.0.0/0; nothing changed"
  else
    # Append only: existing CIDRs are kept, never narrowed.
    cidrs=$(jq -r --arg c "$SESSION_EGRESS_CIDR" \
      '(if .endpointPublicAccess then .publicAccessCidrs else [] end) + [$c] | unique | join(",")' <<<"$vpc")
    aws eks update-cluster-config --name $CLUSTER \
      --resources-vpc-config "endpointPublicAccess=true,endpointPrivateAccess=true,publicAccessCidrs=$cidrs"
    echo "step 3: public endpoint allow-list = $cidrs (update takes a few minutes)"
  fi
fi

# 4. Build and push the task image (UID 1000; PARI/GP 2.15 + seadata + awscli).
registry=$ACCT.dkr.ecr.$AWS_REGION.amazonaws.com
tag=sea-null-$(git rev-parse --short=12 HEAD)
docker build --platform linux/amd64 -t "$registry/$REPO:$tag" image
aws ecr get-login-password | docker login --username AWS --password-stdin "$registry"
docker push "$registry/$REPO:$tag"
digest=$(aws ecr describe-images --repository-name $REPO --image-ids imageTag=$tag \
  --query 'imageDetails[0].imageDigest' --output text)
echo "step 4: IMAGE=$registry/$REPO@$digest   <- give this line to the Claude session"
