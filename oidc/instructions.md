You'll run two things locally with Docker, an IdP (Keycloak) and a tiny test SP, and watch the login with SAML-tracer. Docker needs to be installed first. The SP's settings below come from its README. The Keycloak screens are from memory, so labels may differ slightly by version.

**1. Start the IdP (Keycloak)**

```
docker run -p 8080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:latest start-dev
```

Open http://localhost:8080 and log in as `admin` / `admin`.

**The idea:** a "client app" (the OIDC equivalent of the SP) sends you to Keycloak, you log in, Keycloak redirects back with a short-lived **code**, and the app trades that code for tokens.

### create realm
Create a test realm

### Register the client (Keycloak admin, realm** `test`**)**

- Clients → Create client. Client type **OpenID Connect**, Client ID `oidc-test`.
- Capability config: **Client authentication Off** (a public client, so no secret is needed), **Standard flow** on.
- Valid redirect URIs: `http://localhost:9010/callback`. Save.

### Read the IdP's "metadata"**
```
curl -s http://localhost:8080/realms/test/.well-known/openid-configuration | python3 -m json.tool
```

### Login
```
http://localhost:8080/realms/test/protocol/openid-connect/auth?client_id=oidc-test&response_type=code&scope=openid%20email%20profile&redirect_uri=http://localhost:9010/callback&state=abc123&nonce=n-0S6
```

### Above step would have redirected in browser with code, take it and pasted it below to get access token
```
curl -s -X POST http://localhost:8080/realms/test/protocol/openid-connect/token \
  -d grant_type=authorization_code -d client_id=oidc-test \
  -d code=PASTE_CODE -d redirect_uri=http://localhost:9010/callback
```

### User info

```
curl -s http://localhost:8080/realms/test/protocol/openid-connect/userinfo \
  -H "Authorization: Bearer <access_token>"
```