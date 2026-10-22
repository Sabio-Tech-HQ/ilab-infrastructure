
## EC2 log shipping (sabiogolf / mwakilishi / diaspora.love → ELK)

`filebeat` container on the EC2 (34.200.25.124) ships ALL docker container logs +
/var/log/nginx to Logstash (10.10.10.90:5044 over the WireGuard tunnel).
Logstash routes by container name → ES data streams `logs-<container>-default`
(e.g. logs-sabiogolf_api-default, logs-mwakilishi_php-default,
logs-diaspora_love_app-default, logs-nginx_ec2-default). View in Kibana
(https://kibana.mwakilishi.com, Discover).

Deploy notes (BOTH gotchas cost hours — do not skip):
1. Config file must be owned by root (`sudo tee`), or filebeat refuses to start.
2. Container MUST run with `--user 0:0` — the arm64 image's default user cannot
   read the docker socket, and autodiscover fails SILENTLY (no manager line, no
   inputs, no errors).
3. Logrotate on the EC2 was set to 644 for nginx logs (was 640 root:adm).

docker run -d --name filebeat --restart unless-stopped --user 0:0 \
  -v /home/ubuntu/filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro \
  -v /var/lib/docker/containers:/var/lib/docker/containers:ro \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /var/log/nginx:/var/log/nginx:ro \
  docker.elastic.co/beats/filebeat:9.2.2

## EC2 metrics (metricbeat) + public Kibana

metricbeat on the EC2 (same --user 0:0 + root-owned config rules as filebeat,
plus --pid host and /hostfs mounts): system module (host) + docker module
(32 containers) -> ES directly over the tunnel. Shows up in Kibana Metrics
inventory as host `ec2-prod` with per-container metrics (container.name field).

kibana.mwakilishi.com is PUBLIC via the EC2 gateway pattern, behind basic auth
(shared htpasswd with ai.mwakilishi.com — Vaultwarden item `ai.mwakilishi.com`).
LAN stays on the internal Traefik via Pi-hole override.


## Kibana alerting + email notifier

Basic license has NO email connector, so: Kibana rules do detection
(Alerts tab) and `~/bin/stack-alerts` (cron /etc/cron.d/stack-alerts, every
5 min, on devops) polls /api/alerting/rules/_find and emails
mwakilishi@gmail.com on firing (hourly re-notify) + one recovery notice.

Rules (created via API, visible in Kibana → Alerts):
- Container CPU >90% (10m avg, group by container.name, metricbeat-*)
- Filesystem >85% used (15m max, group by host.name, metricbeat-*)
- Log dataset quiet >20m (ES|QL absence check: nginx_ec2, mwakilishi_php,
  sabiogolf_api, diaspora_love_app)
