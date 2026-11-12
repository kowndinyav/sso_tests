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



### HTTPS

```
cloudflared tunnel --protocol http2 --url http://localhost:8080


curl -s https://define-raleigh-tells-ton.trycloudflare.com/realms/test/.well-known/openid-configuration | python3 -m json.tool

http://define-raleigh-tells-ton.trycloudflare.com/realms/test/protocol/openid-connect/auth?client_id=oidc-test&response_type=code&scope=openid%20email%20profile&redirect_uri=http://localhost:9010/callback&state=abc123&nonce=n-0S6

curl -s -X POST http://define-raleigh-tells-ton.trycloudflare.com/realms/test/protocol/openid-connect/token \
  -d grant_type=authorization_code -d client_id=oidc-test \
  -d code=40b167b3-9b52-5431-5bef-67f22da4f906.iR98Cp6YDPTK2BDb8yCLkCWK.69096c6f-4114-4ec0-b366-1a4a2ee61cb2 -d redirect_uri=http://localhost:9010/callback

curl -s http://define-raleigh-tells-ton.trycloudflare.com/realms/test/protocol/openid-connect/userinfo \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ0MElNR3o4MFZ1SVZLNlNxYmtmeDM0WlczWVQwVFBWbzdkVEtsYWpqRjNRIn0.eyJleHAiOjE3OTQ0NTA3NTksImlhdCI6MTc5NDQ1MDQ1OSwiYXV0aF90aW1lIjoxNzk0NDUwMjQ1LCJqdGkiOiJvbnJ0YWM6NTYzNDIwYzktMjFlMS00NWQ4LWM0YzUtODI3MjVmMTE1OTQ4IiwiaXNzIjoiaHR0cHM6Ly9kZWZpbmUtcmFsZWlnaC10ZWxscy10b24udHJ5Y2xvdWRmbGFyZS5jb20vcmVhbG1zL3Rlc3QiLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiOWFjODVkMzQtNWM5MS00MmVjLWJmYmYtOGUzZTFlOGQ2N2NmIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoib2lkYy10ZXN0Iiwic2lkIjoiaVI5OENwNllEUFRLMkJEYjh5Q0xrQ1dLIiwiYWNyIjoiMCIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLXRlc3QiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IkFsaWNlIFRlc3QiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJhbGljZSIsImdpdmVuX25hbWUiOiJBbGljZSIsImZhbWlseV9uYW1lIjoiVGVzdCIsImVtYWlsIjoiYWxpY2VAZXhhbXBsZS5jb20ifQ.OzdWNcd29fte4u7co2h01qF9rF0m6FN-SIMSIDTLNRp--oXN27_rWMMP-swpu6M0hy8jvJZFMZwBWQCdEdT4hDGw-1TBiSyOQYqoLqy1LV6bLlf0mNSqeN5T1hEXhz0c09I7TuMs9Qotth6naayz7Qj1On1cuJYQ7KgC_l1zHbtjrlbiI4oEMzAcqf8o1cp6DxuGHgZnMWnGwDIWDTamtVWm1welRs4FCSRRl8pNbuB-or4Z_Rozb9EQuIFNJIFoddj2nfFlnePCpLvyopn6r_7EuNktWCvjB-kkENORi8thhw0X0Mhjk9aT7m5WwfmQ9UvXaRCXivdwUDearA16Kw"

```