#!/bin/bash
source ./scripts/helper-functions.sh
ORG_JSON='{"Organization":{"Id":"o-local","MasterAccountId":"000000000000","FeatureSet":"ALL"}}'
save_json "organization" "$ORG_JSON"
