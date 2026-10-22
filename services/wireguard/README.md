# WireGuard site-to-site (home <-> AWS)

Deploy: ansible/deploy-site-to-site.yaml


## Tunnel watchdog — ~/bin/tunnel-watch (devops box)

Every public gateway rides on this tunnel. Cron (/etc/cron.d/tunnel-watch,
every 2 min, flock): pings the AWS peer 10.20.20.2 FROM wireguard-01 (the
tunnel subnet is only routed there), and on 3x failure runs passwordless
`systemctl restart wg-quick@wg1` on wireguard-01 (sudoers.d/tunnel-watch,
exact-command rule), then re-checks and emails mwakilishi@gmail.com
(recovered / still-down). 2026-10-22 drill: stopped tunnel on purpose ->
detected, restarted, gateways back in 13s.
