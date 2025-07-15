server {
    listen 80;
    server_name r14-vpn.ru www.r14-vpn.ru;

    # Для Let's Encrypt challenge
    location ^~ /.well-known/acme-challenge/ {
        alias /var/www/html/.well-known/acme-challenge/;
        try_files $uri =404;
    }

    # Редирект всего остального трафика на HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name r14-vpn.ru www.r14-vpn.ru;

    ssl_certificate /etc/letsencrypt/live/r14-vpn.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/r14-vpn.ru/privkey.pem;

    # Для Let's Encrypt challenge
    location ^~ /.well-known/acme-challenge/ {
        alias /var/www/html/.well-known/acme-challenge/;
        try_files $uri =404;
    }

    # Проксирование на backend
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}