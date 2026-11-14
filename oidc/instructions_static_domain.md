You'll run two things locally with Docker, an IdP (Keycloak) and a tiny test SP, and watch the login with SAML-tracer. Docker needs to be installed first. The SP's settings below come from its README. The Keycloak screens are from memory, so labels may differ slightly by version.

### Step 1 - Run IDP (Keycloak)

```
docker run -p 8080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  -e KC_HOSTNAME=https://radiogenic-rossana-nondefiling.ngrok-free.dev \
  -e KC_PROXY_HEADERS=xforwarded \
  -e KC_HTTP_ENABLED=true \
  -v keycloak_saml_idp_data:/opt/keycloak/data \
  quay.io/keycloak/keycloak:latest start-dev
```

Open https://radiogenic-rossana-nondefiling.ngrok-free.dev and log in as `admin` / `admin`.


### Step 2 - Create realm
```
placeholder
```

### Step 3 - Register the client
```
- Clients → Create client. Client type OpenID Connect, Client ID `oidc-test`.
- Capability config: **Client authentication Off** (a public client, so no secret is needed), **Standard flow** on.
- Valid redirect URIs: `http://localhost:9010/callback`. Save.
```


### Step 4 - Login
```
https://radiogenic-rossana-nondefiling.ngrok-free.dev/realms/test/protocol/openid-connect/auth?client_id=oidc-test&response_type=code&scope=openid%20email%20profile&redirect_uri=http://localhost:9010/callback&state=abc123&nonce=n-0S6
```

### Step 5 - Get Token
```
curl -s -X POST https://radiogenic-rossana-nondefiling.ngrok-free.dev/realms/test/protocol/openid-connect/token \
  -d grant_type=authorization_code -d client_id=oidc-test \
  -d code=PASTE_CODE -d redirect_uri=http://localhost:9010/callback
```

### Step 6 - Get User Info

```
curl -s https://radiogenic-rossana-nondefiling.ngrok-free.dev/realms/test/protocol/openid-connect/userinfo \
  -H "Authorization: Bearer <>"
```



### Read the IdP's "metadata"**
```
curl -s https://radiogenic-rossana-nondefiling.ngrok-free.dev/realms/test/.well-known/openid-configuration | python3 -m json.tool
```
