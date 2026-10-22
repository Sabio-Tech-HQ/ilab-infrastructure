
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
