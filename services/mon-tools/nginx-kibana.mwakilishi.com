server {
    listen 80;
    server_name kibana.mwakilishi.com;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / { return 301 https://$host$request_uri; }
}
server {
    listen 443 ssl http2;
    server_name kibana.mwakilishi.com;
    ssl_certificate /etc/letsencrypt/live/kibana.mwakilishi.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kibana.mwakilishi.com/privkey.pem;
    auth_basic "kibana";
    auth_basic_user_file /etc/nginx/.htpasswd_opencode;
    client_max_body_size 50m;
    location / {
        proxy_pass http://10.10.10.90:5601;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
    }
}
