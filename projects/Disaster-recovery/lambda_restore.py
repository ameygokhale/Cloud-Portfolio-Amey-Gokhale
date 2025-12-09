#!/usr/bin/env python3
"""
lambda_restore.py (LocalStack-friendly)

This version **does not** use boto3.Session(profile_name=...), which
avoids ProfileNotFound errors inside Lambda. Instead it constructs
clients with credentials taken from environment variables (falls back
to 'test' which LocalStack accepts).
"""

import os
import boto3
import json
from typing import Dict, Any

EP = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566")
REGION_SRC = os.environ.get("SRC_REGION", "us-east-1")
REGION_DR = os.environ.get("DR_REGION", "us-west-2")

# credentials - default to 'test' for LocalStack
AWS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY", "test")
AWS_SESSION = os.environ.get("AWS_SESSION_TOKEN", None)

SRC_BUCKET = os.environ.get("SRC_BUCKET", "myapp-source-bucket")
DR_BUCKET = os.environ.get("DR_BUCKET", "myapp-dr-bucket")

def make_s3_client(region: str):
    kwargs = dict(
        region_name=region,
        endpoint_url=EP,
        aws_access_key_id=AWS_KEY,
        aws_secret_access_key=AWS_SECRET
    )
    if AWS_SESSION:
        kwargs["aws_session_token"] = AWS_SESSION
    return boto3.client("s3", **kwargs)

def copy_s3_objects(s3_src, s3_dr, src_bucket: str, dr_bucket: str) -> Dict[str, Any]:
    resp = {"copied_keys": [], "skipped_keys": []}
    paginator = s3_src.get_paginator("list_objects_v2")
    page_iter = paginator.paginate(Bucket=src_bucket)
    total = 0
    for page in page_iter:
        contents = page.get("Contents", [])
        for obj in contents:
            key = obj["Key"]
            total += 1
            try:
                copy_source = {"Bucket": src_bucket, "Key": key}
                s3_dr.copy(CopySource=copy_source, Bucket=dr_bucket, Key=key)
                resp["copied_keys"].append(key)
                print(f"[s3] copied {key}")
            except Exception as e:
                resp["skipped_keys"].append({"Key": key, "Error": str(e)})
                print(f"[s3] failed copy {key}: {e}")
    resp["total_found"] = total
    return resp

def find_snapshots(s3_src, src_bucket: str):
    snaps = []
    try:
        objs = s3_src.list_objects_v2(Bucket=src_bucket, Prefix="rds-snapshots/")
        for item in objs.get("Contents", []):
            snaps.append(item["Key"])
    except Exception:
        # ignore if no snapshots
        pass
    return snaps

def main(event: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    ev = event or {}
    src_bucket = ev.get("src_bucket", ev.get("SRC_BUCKET", SRC_BUCKET))
    dr_bucket = ev.get("dr_bucket", ev.get("DR_BUCKET", DR_BUCKET))
    snapshot_id = ev.get("snapshot_id")
    ami_id = ev.get("ami_id")

    s3_src = make_s3_client(REGION_SRC)
    s3_dr = make_s3_client(REGION_DR)

    result = {
        "src_bucket": src_bucket,
        "dr_bucket": dr_bucket,
        "actions": [],
        "errors": []
    }

    # 1) copy S3 objects
    try:
        s3_res = copy_s3_objects(s3_src, s3_dr, src_bucket, dr_bucket)
        result["actions"].append({"s3_copy": s3_res})
    except Exception as e:
        err = f"s3_copy_error: {str(e)}"
        result["errors"].append(err)
        print(err)

    # 2) find rds snapshot metadata files
    snaps = find_snapshots(s3_src, src_bucket)
    result["snapshot_files_found"] = snaps
    if snaps:
        result["actions"].append({"snapshots": snaps})

    # 3) simulated actions for AMI and RDS
    if ami_id:
        msg = f"SIMULATION: would copy AMI {ami_id} from {REGION_SRC} to {REGION_DR}"
        result["actions"].append({"ami_action": msg})
        print(msg)
    else:
        result["actions"].append({"ami_action": "no_ami_provided (simulation skipped)"})

    if snapshot_id or snaps:
        msg = f"SIMULATION: would restore RDS in {REGION_DR} using snapshot {snapshot_id or 'latest from s3 metadata'}"
        result["actions"].append({"rds_action": msg})
        print(msg)
    else:
        result["actions"].append({"rds_action": "no_snapshot_provided (simulation skipped)"})

    return result

if __name__ == "__main__":
    out = main()
    print("DR orchestrator (demo) finished")
    print(json.dumps(out, indent=2))
