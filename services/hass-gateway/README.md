# Home Assistant Gateway — hass.mwakilishi.com

EC2 nginx gateway -> WireGuard tunnel -> HA @ 10.10.10.80:8123.
NO basic auth (companion app can't prompt); HA account auth handles access.
nginx rate-limits /auth/* endpoints (10r/m, burst 5) — HA throttles per-IP
and every gateway user shares the WG masquerade IP.

IMPORTANT: this vhost deliberately sends NO X-Forwarded-*/X-Real-IP headers.
HA runs with use_x_forwarded_for + trusted_proxies (for the internal Traefik)
and REJECTS forwarded headers from untrusted IPs (the WG masquerade 10.10.10.20)
with 400. Without the headers HA treats gateway requests as direct — works,
but HA logs show all gateway traffic from 10.10.10.20. To restore real client
IPs later: add 10.10.10.20 to HA's http.trusted_proxies AND re-add the
proxy_set_header lines (map pattern in /etc/nginx/conf.d/upgrade-map.conf).

WebSockets use the conditional $connection_upgrade map — a hardcoded
"Connection: upgrade" on plain GETs makes HA return 400.

LAN: Pi-hole split-horizon -> 10.10.10.15 Traefik (unchanged).
