# OpenCode Gateway — opencode.mwakilishi.com

Public entry point for the OpenCode instance that runs **on the devops VM**
(10.10.10.216:4096, the same instance served locally as ai.mwakilishi.com).

## Architecture

```
any device / any network
  -> https://opencode.mwakilishi.com          (basic auth, Let's Encrypt)
     -> EC2 34.200.25.124 nginx               (TLS terminator + auth only)
        -> WireGuard site-to-site tunnel      (services/wireguard)
           -> devops VM opencode web :4096    (the real instance)
```

Commands, files, sessions, MCPs (HomeAssistant, Proxmox) and git all execute
on the devops VM. The EC2 holds no state.

## Components

| File | Purpose |
|---|---|
| `nginx/opencode.mwakilishi.com` | vhost on the EC2: 80 (ACME + redirect), 443 (basic auth -> proxy to 10.10.10.216:4096, WebSocket upgrade, 1h timeouts) |
| `systemd/opencode-web.service` | DISABLED fallback: a standalone opencode on the EC2 itself (127.0.0.1:4096). Kept for emergencies; gateway mode made it redundant |

## Credentials

- Basic auth (username `jthairu`): Vaultwarden item `opencode.mwakilishi.com`,
  and AWS SSM `/mwakilishi/prod/opencode_web_{username,password}` (SecureString).
- The htpasswd file lives at `/etc/nginx/.htpasswd_opencode` on the EC2 —
  NOT in this repo.

Rotate: `echo 'USER:'$(openssl passwd -apr1 'NEWPASS') | sudo tee /etc/nginx/.htpasswd_opencode && sudo systemctl reload nginx`
(then update Vaultwarden + SSM).

## Deploy notes (already live — reference for rebuild)

1. DNS: Route53 `opencode.mwakilishi.com` A -> 34.200.25.124 (mwakilishi.com zone)
2. Cert: certbot webroot (`/var/www/html`), auto-renews via existing certbot cron
3. Symlink vhost into sites-enabled, `nginx -t && systemctl reload nginx`
4. Tunnel must be up: EC2 reaches 10.10.10.216 via wg0 (see services/wireguard).
   LAN-bound traffic is masqueraded as 10.10.10.20 by the home WG VM.

## Historical note

An earlier design (Oct 13-15) planned a container ("ocode") running opencode
on the EC2 directly; it was never deployed — DNS + cert existed, nothing else,
which made the hostname fall through to nginx's default vhost (the sabiogolf
site). Gateway mode (2026-10-21) replaced that plan entirely.

An SSHFS mount of the devops home (`/mnt/devops`) was trialled and is
DISABLED: fstab entry commented out on the EC2, restricted key
(`from="10.10.10.20"`, `~/.ssh/id_devops` on the EC2) remains in the devops
VM's authorized_keys for potential future use.
