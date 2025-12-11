#!/usr/bin/env bash
set -e
# Helper script to build & deploy with AWS SAM CLI.
# You need: awscli configured, and sam cli installed (brew install aws-sam-cli)
STACK_NAME=finops-cost-bot-stack
S3_BUCKET_PLACEHOLDER=YOUR_S3_BUCKET_FOR_SAM_ARTIFACTS

if [ -z "$S3_BUCKET_PLACEHOLDER" ] || [ "$S3_BUCKET_PLACEHOLDER" = "YOUR_S3_BUCKET_FOR_SAM_ARTIFACTS" ]; then
  echo "Please edit deploy.sh and set S3_BUCKET_PLACEHOLDER to a pre-existing S3 bucket in your account."
  exit 1
fi

sam build
sam package --s3-bucket "$S3_BUCKET_PLACEHOLDER" --output-template-file packaged.yaml
sam deploy --template-file packaged.yaml --stack-name "$STACK_NAME" --capabilities CAPABILITY_IAM
