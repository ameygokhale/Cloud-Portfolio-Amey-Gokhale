#!/bin/bash
BUCKET="lz-central-logs"
awslocal s3 mb s3://$BUCKET
awslocal cloudtrail create-trail --name org-trail --s3-bucket-name $BUCKET --is-multi-region-trail
awslocal cloudtrail start-logging --name org-trail
