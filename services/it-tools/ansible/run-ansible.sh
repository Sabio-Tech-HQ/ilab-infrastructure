#!/bin/bash
set -e

# Automatically check and unlock if necessary
status=$(bw status 2>/dev/null | jq -r '.status // "locked"')
if [ "$status" != "unlocked" ]; then
  echo "🔒 Bitwarden vault is locked. Please enter your master password:"
  export BW_SESSION=$(bw unlock --raw)
fi

# Fetch variables from your Bitwarden item (e.g., 'ansible-secrets')
export ANSIBLE_BECOME_PASS=$(bw get item ittools-ansible | jq -r '.fields[] | select(.name=="become_password").value')
# Add any other required secrets here...

# Run ansible-playbook with any passed arguments
ansible-playbook "$@"