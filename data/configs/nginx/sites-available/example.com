upstream final_price {
    server    localhost:8080;
    keepalive 30;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;
    return 444;
}

server {
    listen      80;
    server_name example.com www.example.com;

    location /.well-known/acme-challenge/ {
        allow all;
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen      443 ssl;
    http2       on;
    server_name example.com www.example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    include             /etc/nginx/conf.d/snippets/ssl.conf;
    include             /etc/nginx/conf.d/snippets/headers.conf;

    root /var/www/example.com;

    error_page 404 /404.html;
    location = /404.html {
        internal;
    }

    location = / {
        try_files /index.html =404;
        expires   1d;
    }

    location /assets/ {
        expires    1m;
        access_log off;
    }

    location /api/ {
        if ($cors_origin) {
            add_header Access-Control-Allow-Origin      "$cors_origin" always;
            add_header Access-Control-Allow-Credentials "true" always;
            add_header Vary                             "Origin" always;
        }
        if ($request_method = "OPTIONS") {
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD" always;
            add_header Access-Control-Allow-Headers "Accept, Content-Type, Origin" always;
            add_header Access-Control-Max-Age       1728000 always;
            return 204;
        }
        include    /etc/nginx/conf.d/snippets/proxy.conf;
        proxy_pass http://final_price;
    }

    location = /robots.txt {
        access_log off;
        return 200 "User-agent: *\nDisallow: /";
    }
}