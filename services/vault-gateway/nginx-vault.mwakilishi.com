
server {
    listen 80;
    server_name vault.mwakilishi.com;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / { return 301 https://$host$request_uri; }
}
server {
    listen 443 ssl http2;
    server_name vault.mwakilishi.com;
    ssl_certificate /etc/letsencrypt/live/vault.mwakilishi.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vault.mwakilishi.com/privkey.pem;
    # Vaultwarden reverse-proxy recommendations
    client_max_body_size 525M;
    location / {
        proxy_pass http://10.10.10.200:80;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 90s;
        proxy_send_timeout 90s;
    }
}
