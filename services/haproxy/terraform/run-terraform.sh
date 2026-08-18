#!/bin/bash
set -e

# Automatically check and unlock if necessary
status=$(bw status 2>/dev/null | jq -r '.status // "locked"')
if [ "$status" != "unlocked" ]; then
  echo "🔒 Bitwarden vault is locked. Please enter your master password:"
  export BW_SESSION=$(bw unlock --raw)
fi

# Fetch variables from Vaultwarden item 'haproxy-terraform'
export TF_VAR_proxmox_api_url=$(bw get item haproxy-terraform | jq -r '.fields[] | select(.name=="proxmox_api_url").value')
export TF_VAR_proxmox_api_token_id=$(bw get item haproxy-terraform | jq -r '.fields[] | select(.name=="proxmox_api_token_id").value')
export TF_VAR_proxmox_api_token_secret=$(bw get item haproxy-terraform | jq -r '.fields[] | select(.name=="proxmox_api_token_secret").value')
export TF_VAR_ssh_public_key=$(bw get item haproxy-terraform | jq -r '.fields[] | select(.name=="ssh_public_key").value')
export TF_VAR_ssh_public_keys=$(bw get item haproxy-terraform | jq -r '.fields[] | select(.name=="ssh_public_keys").value')
export TF_VAR_ssh_user=$(bw get item haproxy-terraform | jq -r '.fields[] | select(.name=="ssh_user").value')
export TF_VAR_ssh_password=$(bw get item haproxy-terraform | jq -r '.fields[] | select(.name=="ssh_password").value')
export TF_VAR_gateway=$(bw get item haproxy-terraform | jq -r '.fields[] | select(.name=="gateway").value')


# Run terraform with any passed arguments
terraform "$@"