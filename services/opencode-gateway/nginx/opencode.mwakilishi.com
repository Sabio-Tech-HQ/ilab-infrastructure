server {
    listen 80;
    server_name opencode.mwakilishi.com;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / { return 301 https://$host$request_uri; }
}
server {
    listen 443 ssl http2;
    server_name opencode.mwakilishi.com;
    ssl_certificate /etc/letsencrypt/live/opencode.mwakilishi.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/opencode.mwakilishi.com/privkey.pem;
    auth_basic "opencode";
    auth_basic_user_file /etc/nginx/.htpasswd_opencode;
    client_max_body_size 50m;
    location / {
        proxy_pass http://10.10.10.216:4096;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
