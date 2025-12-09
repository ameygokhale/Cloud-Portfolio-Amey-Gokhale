#!/usr/bin/env bash
set -e
EP=${AWS_ENDPOINT_URL:-http://localhost:4566}
PROFILE=${AWS_PROFILE:-localstack}

# Buckets
aws --endpoint-url=$EP --profile $PROFILE s3api create-bucket --bucket myapp-source-bucket --region us-east-1 || true
aws --endpoint-url=$EP --profile $PROFILE s3api create-bucket --bucket myapp-dr-bucket --region us-west-2 || true

# Upload sample object
echo "Hello from PRIMARY region" > index.html
aws --endpoint-url=$EP --profile $PROFILE s3 cp index.html s3://myapp-source-bucket/index.html

# Simulate an RDS snapshot metadata file
mkdir -p snapshots
echo "snapshot-id: rds-snapshot-2025-12-09" > snapshots/rds-snapshot-2025-12-09.meta
aws --endpoint-url=$EP --profile $PROFILE s3 cp snapshots/rds-snapshot-2025-12-09.meta s3://myapp-source-bucket/rds-snapshots/rds-snapshot-2025-12-09.meta

# Show created objects
aws --endpoint-url=$EP --profile $PROFILE s3 ls s3://myapp-source-bucket --recursive
aws --endpoint-url=$EP --profile $PROFILE s3 ls s3://myapp-dr-bucket --recursive || true

echo "Demo resources created."
