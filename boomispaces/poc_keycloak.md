## Ngrok for public domain and a nasty hack for public cert endpoint

Folder : `certproxy`
```
docker run --rm --name jwks-proxy -p 8081:8081 -v "$PWD/nginx.conf":/etc/nginx/conf.d/default.conf:ro nginx:alpine
```

```
ngrok http 8081 --url https://radiogenic-rossana-nondefiling.ngrok-free.dev
```

## Run IDP
```
docker run --rm --name keycloak -p 8080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  -e KC_HOSTNAME=https://radiogenic-rossana-nondefiling.ngrok-free.dev \
  -e KC_PROXY_HEADERS=xforwarded \
  -e KC_HTTP_ENABLED=true \
  -e KC_HTTP_ACCESS_LOG_ENABLED=true \
  -v keycloak_saml_idp_data:/opt/keycloak/data \
  quay.io/keycloak/keycloak:latest start-dev
```

#### Test
```
localhost:8080 - must be working
```

## Run OIDC SP
Folder : `oidc`
```
python3 server.py

http://localhost:3000/login
```

## Run the BoomiEmbed App
Folder : `boomispaces`
```
# update the emded token inside server.js

node server.js
```
