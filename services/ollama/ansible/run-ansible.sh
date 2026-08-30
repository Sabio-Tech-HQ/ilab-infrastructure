#!/bin/bash
set -e

# Check Bitwarden status
status=$(bw status 2>/dev/null | jq -r '.status // "locked"')

# Unlock if necessary
if [ "$status" != "unlocked" ]; then
    echo "🔒 Bitwarden vault is locked. Please enter your master password:"
    export BW_SESSION=$(bw unlock --raw)
else
    export BW_SESSION=$(bw unlock --raw 2>/dev/null || true)
fi

# Make sure we actually have a session
if [ -z "$BW_SESSION" ]; then
    echo "❌ Could not obtain Bitwarden session."
    exit 1
fi

echo "🔐 Bitwarden session available."

# Run Ansible with BW_SESSION inherited
ansible-playbook "$@"
