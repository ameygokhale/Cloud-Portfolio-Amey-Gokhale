#!/bin/bash
docker-compose up -d
sleep 10
awslocal s3 ls
