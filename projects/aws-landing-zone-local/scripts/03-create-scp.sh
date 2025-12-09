#!/bin/bash
source ./scripts/helper-functions.sh
POLICY_CONTENT=$(cat policies/deny-unapproved-services.json)
POLICY="{\"Policies\":[{\"Id\":\"p-deny\",\"Name\":\"Deny-Unapproved-Services\",\"Type\":\"SERVICE_CONTROL_POLICY\",\"Content\":$POLICY_CONTENT}]}"
save_json "scp" "$POLICY"
