#!/bin/bash
set -e

# Check Bitwarden CLI status
status=$(bw status 2>/dev/null | jq -r '.status // "locked"')

if [ "$status" = "unauthenticated" ]; then
  echo "🔑 Bitwarden session is unauthenticated. Please log in first:"
  bw login
  status="locked"
fi

if [ "$status" != "unlocked" ]; then
  echo "🔒 Bitwarden vault is locked. Please enter your master password:"
  export BW_SESSION=$(bw unlock --raw)
fi

# Fetch secrets from your Bitwarden item
export ANSIBLE_BECOME_PASS=$(bw get item vaultwarden-ansible | jq -r '.fields[] | select(.name=="become_password").value')
DB_PASSWORD=$(bw get item vaultwarden-ansible | jq -r '.fields[] | select(.name=="db_password").value')

# Run ansible-playbook, injecting the DB password as an extra-var
ansible-playbook "$@" --extra-vars "vaultwarden_db_password=$DB_PASSWORD"