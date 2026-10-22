# Vaultwarden Gateway — vault.mwakilishi.com

EC2 nginx gateway -> WireGuard tunnel -> HAProxy VIP 10.10.10.200:80 ->
vaultwarden-01/02/03 (.207-.208-.209). NO basic auth (Bitwarden clients
cannot prompt); Vaultwarden master password (+ user 2FA recommended) is the
auth layer, and vault data is zero-knowledge encrypted.

Before exposure, closed open signups: SIGNUPS_ALLOWED=false in
services/vaultwarden/ansible/deploy-vaultwarden.yaml AND live on all three
nodes (verified: /identity/accounts/register -> "Registration not allowed").
Admin panel disabled (no ADMIN_TOKEN env).

LAN: Pi-hole split-horizon -> 10.10.10.15 Traefik (bw CLI unaffected).
Phone Bitwarden app: set self-hosted server URL https://vault.mwakilishi.com —
now works from any network without VPN.
