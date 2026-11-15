# Token Server API (Boomi PoC)

A tiny token issuer. It signs JWTs (RS256) and publishes the public key so Boomi can verify them.
Run: `node token_server.mjs` (Node 18+, no packages).

| Setting | Value |
|---|---|
| Issuer (`iss`) / Auth Server URL | `https://radiogenic-rossana-nondefiling.ngrok-free.dev` (override: `ISSUER` env) |
| Audience (`aud`) | `boomi-spaces` (override: `AUDIENCE` env; confirm real value with Boomi) |
| Signing key | RSA-2048, `key.pem` next to the script, created on first run |
| Key ID (`kid`) | First 16 chars of SHA-256 of the public key modulus; printed at startup |

## Two servers

| Server | Address | Exposed via ngrok? |
|---|---|---|
| Public | `127.0.0.1:8081` | Yes: `ngrok http 8081 --url https://radiogenic-rossana-nondefiling.ngrok-free.dev` |
| Mint (private) | `127.0.0.1:8082` | **Never.** Anyone who reaches it can mint tokens. |

---

## GET /.well-known/jwks.json  (public, port 8081)

Returns the public key. Boomi calls this to verify token signatures.

**Request:** no parameters, no authentication.

**Response 200** `application/json`, cached 300 s:

```json
{ "keys": [ { "kty": "RSA", "n": "...", "e": "AQAB", "kid": "<kid>", "alg": "RS256", "use": "sig" } ] }
```

**Other paths:** `404 not found`.

```
curl https://radiogenic-rossana-nondefiling.ngrok-free.dev/.well-known/jwks.json
```

---

## GET /mint  (private, port 8082)

Creates and signs a token for the given email.

**Query parameters**

| Name | Required | Description |
|---|---|---|
| `email` | yes | Email of the user. Must look like `name@domain`, max 64 chars before `@`, 255 after. |
| `expiry` | no | Seconds the token stays valid. Default `300`. Clamped to 30–3600. Non-numeric falls back to 300. |

**Response 200** `text/plain`, `Cache-Control: no-store`: the token, one line (`header.claims.signature`).

**Response 400** `text/plain`: `email` missing or invalid.

```
curl "http://localhost:8082/mint?email=you@adobe.com&expiry=300"
```

**Token header**

```json
{ "alg": "RS256", "typ": "JWT", "kid": "<kid>" }
```

**Token claims**

| Claim | Value |
|---|---|
| `iss` | The issuer above. Must equal the Auth Server URL registered in Boomi. |
| `aud` | The audience above. |
| `sub` | First 24 hex chars of SHA-256 of the email (stable per email, not the email itself). |
| `email` | The email you passed. |
| `iat` | Issue time (Unix seconds). |
| `exp` | `iat` + `expiry`. |
| `jti` | Random UUID, unique per token. Boomi rejects a reused `jti`, so mint a fresh token per embed load. |

---

## Using the token with Boomi

```
https://spaces-embed-service.boomi.com/embed?token=<token>
```

URL-encode the token if you build the URL in code (`encodeURIComponent`).

## Security notes

- Keep `key.pem` secret and out of git. Changing or deleting it changes the `kid`; old tokens then stop verifying.
- The mint endpoint has no authentication because it is localhost-only. If you ever expose it, add authentication first.
- A token in a URL can end up in logs and browser history. Keep expiry short.
- PoC only. In production the mint step runs inside ALM, behind the user's existing session, with the key in key management.