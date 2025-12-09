#!/usr/bin/env bash
set -e
EP=${AWS_ENDPOINT_URL:-http://localhost:4566}
PROFILE=${AWS_PROFILE:-localstack}
SRC=myapp-source-bucket
DR=myapp-dr-bucket

echo "Syncing s3://$SRC -> s3://$DR"
aws --endpoint-url=$EP --profile $PROFILE s3 sync s3://$SRC s3://$DR

echo "Sync complete."
