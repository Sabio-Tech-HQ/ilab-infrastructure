server {
    listen 80;
    server_name opencode.mwakilishi.com;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / { return 301 https://ai.mwakilishi.com$request_uri; }
}
server {
    listen 443 ssl http2;
    server_name opencode.mwakilishi.com;
    ssl_certificate /etc/letsencrypt/live/opencode.mwakilishi.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/opencode.mwakilishi.com/privkey.pem;
    return 301 https://ai.mwakilishi.com$request_uri;
}
