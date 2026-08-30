#!/bin/bash
set -e

# ------------------------------------------------------------
# Bitwarden Initialization
# ------------------------------------------------------------

status=$(bw status 2>/dev/null | jq -r '.status // "locked"')

if [ "$status" != "unlocked" ]; then
  echo "🔒 Bitwarden vault is locked. Please enter your master password:"
  export BW_SESSION=$(bw unlock --raw)
fi

# ------------------------------------------------------------
# Retrieve Ansible sudo pass
# ------------------------------------------------------------

export ANSIBLE_BECOME_PASS="$(
  bw get item pngx-ansible |
  jq -r '.fields[] | select(.name=="become_password").value'
)"

# ------------------------------------------------------------
# Retrieve Paperless PostgreSQL password
# ------------------------------------------------------------

PAPERLESS_DATABASE_PASSWORD="$(
  bw get item pngx-ansible |
  jq -r '.fields[] | select(.name=="PAPERLESS_DATABASE_PASSWORD").value'
)"

# ------------------------------------------------------------
# Retrieve Paperless application secret key
# ------------------------------------------------------------

PAPERLESS_SECRET_KEY="$(
  bw get item pngx-ansible |
  jq -r '.fields[] | select(.name=="PAPERLESS_SECRET_KEY").value'
)"

# ------------------------------------------------------------
# Validate secrets
# ------------------------------------------------------------

if [ -z "$PAPERLESS_DATABASE_PASSWORD" ] || \
   [ "$PAPERLESS_DATABASE_PASSWORD" = "null" ]; then

  echo "ERROR: PAPERLESS_DATABASE_PASSWORD not found in Bitwarden under pngx-ansible."
  exit 1
fi

if [ -z "$PAPERLESS_SECRET_KEY" ] || \
   [ "$PAPERLESS_SECRET_KEY" = "null" ]; then

  echo "ERROR: PAPERLESS_SECRET_KEY not found in Bitwarden under pngx-ansible."
  exit 1
fi

# ------------------------------------------------------------
# Run Ansible Execution Pass
# ------------------------------------------------------------

ansible-playbook "$@" \
  --extra-vars "PAPERLESS_DATABASE_PASSWORD=$PAPERLESS_DATABASE_PASSWORD" \
  --extra-vars "PAPERLESS_SECRET_KEY=$PAPERLESS_SECRET_KEY"
