limit_req_zone $binary_remote_addr zone=hass_login:10m rate=10r/m;

server {
    listen 80;
    server_name hass.mwakilishi.com;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / { return 301 https://$host$request_uri; }
}
server {
    listen 443 ssl http2;
    server_name hass.mwakilishi.com;
    ssl_certificate /etc/letsencrypt/live/hass.mwakilishi.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hass.mwakilishi.com/privkey.pem;
    client_max_body_size 50m;
    location / {
        proxy_pass http://10.10.10.80:8123;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_buffering off;
    }
    # password-spray guard: HA throttles per-IP and every gateway user shares one IP
    location /auth/login {
        limit_req zone=hass_login burst=5 nodelay;
        proxy_pass http://10.10.10.80:8123;
        proxy_set_header Host $host;
    }
    location /auth/token {
        limit_req zone=hass_login burst=5 nodelay;
        proxy_pass http://10.10.10.80:8123;
        proxy_set_header Host $host;
    }
}
