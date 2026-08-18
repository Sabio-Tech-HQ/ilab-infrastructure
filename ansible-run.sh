#!/bin/bash
set -e

# Automatically check and unlock if necessary
status=$(bw status 2>/dev/null | jq -r '.status // "locked"')
if [ "$status" != "unlocked" ]; then
  echo "🔒 Bitwarden vault is locked. Please enter your master password:"
  export BW_SESSION=$(bw unlock --raw)
fi

# Run ansible-playbook passing all your usual arguments (inventory, playbook, etc.)
ansible-playbook "$@"