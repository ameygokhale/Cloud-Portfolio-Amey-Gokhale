#!/usr/bin/env python3
# Lambda-compatible handler that runs scanner and calls reporter to send to Slack.
import os
import json
import datetime
from botocore.config import Config
import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")
DAYS_CPU = int(os.environ.get("CPU_LOOKBACK_DAYS", "14"))
SNAPSHOT_AGE_DAYS = int(os.environ.get("SNAPSHOT_AGE_DAYS", "90"))

sess = boto3.Session(region_name=REGION)
ec2 = sess.client("ec2", config=Config(retries={'max_attempts': 5}))
cw = sess.client("cloudwatch", config=Config(retries={'max_attempts': 5}))
rds = sess.client("rds", config=Config(retries={'max_attempts': 5}))
ce = sess.client("ce", config=Config(retries={'max_attempts': 5}))

def now_utc():
    return datetime.datetime.utcnow()

def iso(dt): return dt.isoformat()+"Z"

def detect_idle_ec2():
    instances = ec2.describe_instances(
        Filters=[{"Name":"instance-state-name","Values":["running","stopped","stopping"]}]
    )["Reservations"]
    results = []
    start = now_utc() - datetime.timedelta(days=DAYS_CPU)
    for r in instances:
        for i in r["Instances"]:
            iid = i["InstanceId"]
            state = i["State"]["Name"]
            entry = {"InstanceId": iid, "State": state, "InstanceType": i.get("InstanceType"), "Tags": i.get("Tags", [])}
            if state in ("stopped", "stopping"):
                entry["Reason"] = f"state={state}"
                results.append(entry); continue
            resp = cw.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName="CPUUtilization",
                Dimensions=[{"Name":"InstanceId","Value":iid}],
                StartTime=start,
                EndTime=now_utc(),
                Period=3600*24,
                Statistics=["Average"]
            )
            datapoints = resp.get("Datapoints", [])
            avg = 0.0
            if datapoints:
                avg = sum(d["Average"] for d in datapoints)/len(datapoints)
            entry["AvgCPU"] = round(avg, 3)
            if avg < 3.0:
                entry["Reason"] = f"low_cpu_avg_{avg}%"
                results.append(entry)
    return results

def detect_unattached_volumes():
    vols = ec2.describe_volumes(Filters=[{"Name":"status","Values":["available"]}])["Volumes"]
    out = []
    for v in vols:
        out.append({"VolumeId": v["VolumeId"], "SizeGiB": v["Size"], "CreateTime": str(v["CreateTime"]), "Tags": v.get("Tags", [])})
    return out

def detect_aged_snapshots():
    snaps = ec2.describe_snapshots(OwnerIds=["self"])["Snapshots"]
    cutoff = now_utc() - datetime.timedelta(days=SNAPSHOT_AGE_DAYS)
    out = []
    for s in snaps:
        st = s["StartTime"]
        if getattr(st, "tzinfo", None) is not None:
            st = st.replace(tzinfo=None)
        if st < cutoff:
            out.append({"SnapshotId": s["SnapshotId"], "VolumeId": s.get("VolumeId"), "StartTime": str(s["StartTime"]), "Tags": s.get("Tags", [])})
    return out

def detect_unused_eips():
    addrs = ec2.describe_addresses()["Addresses"]
    out = []
    for a in addrs:
        if not a.get("AssociationId") and not a.get("InstanceId"):
            out.append({"PublicIp": a["PublicIp"], "AllocationId": a.get("AllocationId"), "Tags": a.get("Tags", [])})
    return out

def detect_underutilized_rds():
    instances = rds.describe_db_instances()["DBInstances"]
    start = now_utc() - datetime.timedelta(days=DAYS_CPU)
    out = []
    for inst in instances:
        dbid = inst["DBInstanceIdentifier"]
        resp = cw.get_metric_statistics(
            Namespace="AWS/RDS",
            MetricName="CPUUtilization",
            Dimensions=[{"Name":"DBInstanceIdentifier","Value":dbid}],
            StartTime=start,
            EndTime=now_utc(),
            Period=3600*24,
            Statistics=["Average"]
        )
        datapoints = resp.get("Datapoints", [])
        avg = 0.0
        if datapoints:
            avg = sum(d['Average'] for d in datapoints)/len(datapoints)
        if avg < 5.0:
            out.append({"DBInstanceIdentifier": dbid, "DBInstanceClass": inst.get("DBInstanceClass"), "AvgCPU": round(avg,3), "Tags": inst.get("TagList", [])})
    return out

def get_cost_last_30_days():
    end = now_utc().date()
    start = end - datetime.timedelta(days=30)
    try:
        resp = ce.get_cost_and_usage(
            TimePeriod={"Start": start.isoformat(), "End": end.isoformat()},
            Granularity="MONTHLY",
            Metrics=["BlendedCost"],
            GroupBy=[{"Type":"DIMENSION","Key":"SERVICE"}]
        )
        return resp
    except Exception as e:
        return {"error": str(e)}

def generate_report():
    return {
        "generatedAt": iso(now_utc()),
        "region": REGION,
        "idle_ec2": detect_idle_ec2(),
        "unattached_volumes": detect_unattached_volumes(),
        "aged_snapshots": detect_aged_snapshots(),
        "unused_eips": detect_unused_eips(),
        "underutilized_rds": detect_underutilized_rds(),
        "cost_explorer": get_cost_last_30_days()
    }

# Lambda handler
def lambda_handler(event, context):
    report = generate_report()
    # Optionally send to Slack if webhook configured
    slack_webhook = os.environ.get("SLACK_WEBHOOK")
    if slack_webhook:
        try:
            import reporter
            reporter.send_to_slack(report, slack_webhook)
        except Exception as e:
            print("Failed to send to Slack:", e)
    return {
        "statusCode": 200,
        "body": json.dumps(report, default=str)
    }

# allow local run
if __name__ == "__main__":
    import reporter
    report = generate_report()
    print(json.dumps(report, indent=2, default=str))
    # if SLACK_WEBHOOK env var is set in local env, reporter will try to send
