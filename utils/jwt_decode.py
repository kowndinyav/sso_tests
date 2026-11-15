#!/usr/bin/env python3
"""Decode a JWT (such as an OIDC id_token) and sanity-check its claims.

IMPORTANT: this tool only DECODES the token. It does NOT verify the signature,
so never use its output to decide whether a token can be trusted.

Usage (preferred: read the token from stdin so it stays out of shell history):
    pbpaste | python3 jwt_decode.py
    python3 jwt_decode.py < token.txt

Optional checks:
    --expect-iss URL        issuer must equal this (e.g. your Auth Server URL)
    --expect-aud VALUE      audience must contain this
    --expect-email ADDRESS  email claim must equal this
    --jwks-url URL          fetch the JWKS (https only) and confirm the token's
                            `kid` is one of the published keys (catches tokens
                            signed by a key that no longer exists)

Exit codes: 0 = all checks passed, 1 = a check failed, 2 = bad input.
"""

import argparse
import base64
import binascii
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

MAX_TOKEN_CHARS = 16_384
MAX_JWKS_BYTES = 262_144
FETCH_TIMEOUT_SECONDS = 10
# Claims the Boomi Spaces Embed Service documents as required or checked.
BOOMI_CLAIMS = ("email", "sub", "iss", "aud", "jti")


def decode_part(part: str, name: str) -> dict:
    """Base64url-decode one JWT part and parse it as a JSON object."""
    if not part:
        raise ValueError(f"{name} part is empty")
    try:
        raw = base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))
        obj = json.loads(raw)
    except (binascii.Error, ValueError) as exc:  # JSON/UTF-8 errors are ValueErrors
        raise ValueError(f"{name} is not valid base64url-encoded JSON") from exc
    if not isinstance(obj, dict):
        raise ValueError(f"{name} must be a JSON object")
    return obj


def parse_token(token: str):
    """Return (header, claims) or raise ValueError. Never returns the signature."""
    token = token.strip()
    if not token:
        raise ValueError("no token provided")
    if len(token) > MAX_TOKEN_CHARS:
        raise ValueError("token is unreasonably long")
    if any(ch.isspace() for ch in token):
        raise ValueError("token contains whitespace; paste it as a single line")
    parts = token.split(".")
    if len(parts) == 5:
        raise ValueError("5 parts: this looks like an encrypted JWT (JWE); it cannot be decoded here")
    if len(parts) != 3:
        raise ValueError(f"expected 3 dot-separated parts, found {len(parts)}")
    return decode_part(parts[0], "header"), decode_part(parts[1], "claims")


def utc(ts) -> str:
    """Format a numeric timestamp as ISO-8601 UTC, or explain why not."""
    if isinstance(ts, bool) or not isinstance(ts, (int, float)):
        return "not a number"
    try:
        return datetime.fromtimestamp(ts, timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return "out of range"


def fetch_jwks_kids(url: str) -> set:
    """Fetch a JWKS over HTTPS (certificate verification on) and return its key IDs."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("--jwks-url must be an https:// URL")
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as resp:  # noqa: S310 (https enforced above)
        if not resp.geturl().startswith("https://"):
            raise ValueError("JWKS request was redirected to a non-https URL")
        body = resp.read(MAX_JWKS_BYTES + 1)
    if len(body) > MAX_JWKS_BYTES:
        raise ValueError("JWKS response is unreasonably large")
    try:
        keys = json.loads(body).get("keys", [])
    except (ValueError, AttributeError) as exc:
        raise ValueError("response was not a JWKS document (got something other than JSON)") from exc
    return {k.get("kid") for k in keys if isinstance(k, dict) and k.get("kid")}


def audiences(claims: dict) -> list:
    aud = claims.get("aud")
    if isinstance(aud, list):
        return [a for a in aud if isinstance(a, str)]
    return [aud] if isinstance(aud, str) else []


def run_checks(header: dict, claims: dict, args) -> list:
    """Return a list of (status, message). status is 'ok', 'FAIL' or 'warn'."""
    results = []
    now = time.time()

    exp, iat, nbf = claims.get("exp"), claims.get("iat"), claims.get("nbf")
    if isinstance(exp, (int, float)) and not isinstance(exp, bool):
        if now >= exp:
            results.append(("FAIL", f"token is EXPIRED ({int(now - exp)}s ago)"))
        else:
            life = f", lifetime {int(exp - iat)}s" if isinstance(iat, (int, float)) else ""
            results.append(("ok", f"not expired, {int(exp - now)}s remaining{life}"))
    else:
        results.append(("FAIL", "no usable `exp` claim"))
    if isinstance(nbf, (int, float)) and not isinstance(nbf, bool) and now < nbf:
        results.append(("FAIL", f"token not valid yet (`nbf` is {int(nbf - now)}s in the future)"))

    missing = [c for c in BOOMI_CLAIMS if not claims.get(c)]
    if missing:
        results.append(("FAIL", "missing claims Boomi's embed service needs: " + ", ".join(missing)))
    else:
        results.append(("ok", "has email, sub, iss, aud, jti"))
    if header.get("alg") not in ("RS256", "RS384", "RS512", "ES256", "ES384", "ES512", "PS256", "PS384", "PS512"):
        results.append(("warn", f"unusual signing algorithm: {header.get('alg')!r}"))

    if args.expect_iss is not None:
        same = claims.get("iss") == args.expect_iss
        results.append(("ok" if same else "FAIL", "issuer matches" if same else
                        f"issuer mismatch: token has {claims.get('iss')!r}, expected {args.expect_iss!r}"))
    if args.expect_aud is not None:
        has = args.expect_aud in audiences(claims)
        results.append(("ok" if has else "FAIL", "audience matches" if has else
                        f"audience mismatch: token has {claims.get('aud')!r}, expected {args.expect_aud!r}"))
    if args.expect_email is not None:
        same = claims.get("email") == args.expect_email
        results.append(("ok" if same else "FAIL", "email matches" if same else
                        f"email mismatch: token has {claims.get('email')!r}, expected {args.expect_email!r}"))

    if args.jwks_url is not None:
        kid = header.get("kid")
        try:
            kids = fetch_jwks_kids(args.jwks_url)
        except (ValueError, OSError) as exc:  # URLError and timeouts are OSErrors
            results.append(("FAIL", f"could not read JWKS: {exc}"))
        else:
            if kid in kids:
                results.append(("ok", "token's `kid` is published in the JWKS"))
            else:
                results.append(("FAIL", f"token's `kid` {kid!r} is NOT in the JWKS (signed by a key that no longer exists?)"))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Decode a JWT and sanity-check its claims (no signature verification).")
    parser.add_argument("token", nargs="?", help="the token; if omitted it is read from stdin (preferred)")
    parser.add_argument("--expect-iss")
    parser.add_argument("--expect-aud")
    parser.add_argument("--expect-email")
    parser.add_argument("--jwks-url")
    args = parser.parse_args()

    raw = args.token if args.token is not None else sys.stdin.read(MAX_TOKEN_CHARS + 1)
    try:
        header, claims = parse_token(raw)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print("== HEADER ==")
    print(json.dumps(header, indent=2))
    print("\n== CLAIMS ==")
    print(json.dumps(claims, indent=2))
    print("\n== TIMES (UTC) ==")
    for name in ("iat", "auth_time", "nbf", "exp"):
        if name in claims:
            print(f"{name:<10} {utc(claims[name])}")
    print(f"{'now':<10} {utc(time.time())}")

    results = run_checks(header, claims, args)
    print("\n== CHECKS ==")
    for status, message in results:
        print(f"[{status:>4}] {message}")
    print("[note] signature NOT verified; this tool only decodes")
    return 1 if any(status == "FAIL" for status, _ in results) else 0


if __name__ == "__main__":
    sys.exit(main())