# Plex Gateway — plex.mwakilishi.com

EC2 nginx gateway -> WireGuard tunnel -> Plex @ 10.10.10.60:32400.
NO basic auth (Plex apps cannot prompt); Plex account auth handles access.
Plex prefs hardened for this: allowedNetworks=127.0.0.1/32 (all clients must
sign in — the WG masquerade IP 10.10.10.20 is NOT trusted as LAN) and
customConnections=https://plex.mwakilishi.com. LAN: Pi-hole split-horizon ->
10.10.10.15 Traefik (unchanged, LAN speed).
Egress tripwire: CloudWatch alarm ec2-plex-egress-tripwire (>40GB/day; site
baseline 13-17GB) -> SNS ec2-egress-alerts -> mwakilishi@gmail.com.
Streaming through AWS costs ~$0.09/GB egress.
