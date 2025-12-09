#!/bin/bash
LZ_STATE="localstack/state"
mkdir -p $LZ_STATE
function save_json() { echo "$2" > "$LZ_STATE/$1.json"; }
function load_json() { cat "$LZ_STATE/$1.json"; }
