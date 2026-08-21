#!/bin/bash
set -e

# ------------------------------------------------------------
# Bitwarden
# ------------------------------------------------------------

status=$(bw status 2>/dev/null | jq -r '.status // "locked"')

if [ "$status" != "unlocked" ]; then
  echo "🔒 Bitwarden vault is locked. Please enter your master password:"
  export BW_SESSION=$(bw unlock --raw)
fi

# ------------------------------------------------------------
# Retrieve Ansible sudo password
# ------------------------------------------------------------

export ANSIBLE_BECOME_PASS="$(
  bw get item penpot-ansible |
  jq -r '.fields[] | select(.name=="become_password").value'
)"

# ------------------------------------------------------------
# Retrieve Penpot PostgreSQL password
# ------------------------------------------------------------

PENPOT_DATABASE_PASSWORD="$(
  bw get item penpot-ansible |
  jq -r '.fields[] | select(.name=="PENPOT_DATABASE_PASSWORD").value'
)"

# ------------------------------------------------------------
# Retrieve Penpot secret key
# ------------------------------------------------------------

PENPOT_SECRET_KEY="$(
  bw get item penpot-ansible |
  jq -r '.fields[] | select(.name=="PENPOT_SECRET_KEY").value'
)"

# ------------------------------------------------------------
# Validate secrets
# ------------------------------------------------------------

if [ -z "$PENPOT_DATABASE_PASSWORD" ] || \
   [ "$PENPOT_DATABASE_PASSWORD" = "null" ]; then

  echo "ERROR: PENPOT_DATABASE_PASSWORD not found in Bitwarden."
  exit 1
fi

if [ -z "$PENPOT_SECRET_KEY" ] || \
   [ "$PENPOT_SECRET_KEY" = "null" ]; then

  echo "ERROR: PENPOT_SECRET_KEY not found in Bitwarden."
  exit 1
fi

# ------------------------------------------------------------
# Run Ansible
# ------------------------------------------------------------

ansible-playbook "$@" \
  --extra-vars "PENPOT_DATABASE_PASSWORD=$PENPOT_DATABASE_PASSWORD" \
  --extra-vars "PENPOT_SECRET_KEY=$PENPOT_SECRET_KEY"