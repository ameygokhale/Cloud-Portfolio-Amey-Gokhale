#!/usr/bin/env python3
import json, os, sys, requests
from datetime import datetime

def pretty_summary(report):
    lines = []
    lines.append(f"*FinOps Bot Report* — {report.get('generatedAt')}")
    def short(listname):
        return f"{len(report.get(listname, []))} {listname.replace('_',' ')}"
    lines.append(short("idle_ec2"))
    lines.append(short("unattached_volumes"))
    lines.append(short("aged_snapshots"))
    lines.append(short("unused_eips"))
    lines.append(short("underutilized_rds"))
    ce = report.get("cost_explorer", {})
    if isinstance(ce, dict) and "ResultsByTime" in ce:
        total = 0.0
        for g in ce.get("ResultsByTime", []):
            for r in g.get("Total", {}).values():
                try:
                    total += float(r.get("Amount",0.0))
                except:
                    pass
        lines.append(f"Estimated cost last 30d: ${round(total,2)}")
    elif isinstance(ce, dict) and "error" in ce:
        lines.append(f"Cost Explorer: ERROR: {ce['error']}")
    return "\n".join(lines)

def send_to_slack(report, webhook_url=None):
    url = webhook_url or os.environ.get("SLACK_WEBHOOK")
    if not url:
        print("No SLACK_WEBHOOK configured; skipping Slack send.")
        return
    payload = {"text": pretty_summary(report)}
    r = requests.post(url, json=payload, timeout=10)
    print("Slack response:", r.status_code, r.text)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        report = json.load(open(sys.argv[1]))
    else:
        report = json.load(sys.stdin)
    print(pretty_summary(report))
    send_to_slack(report)
