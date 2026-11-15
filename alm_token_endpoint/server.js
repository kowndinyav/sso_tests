// Tiny token issuer for the Boomi PoC. No npm packages needed.
//
//   node token_server.mjs
//
// PUBLIC  port 8081 (point ngrok here):  GET /.well-known/jwks.json   -> public key only
// PRIVATE port 8082 (localhost only):    GET /mint?email=a@b.com&expiry=300  -> signed token
//
// The mint port is NOT tunneled, so only you can mint. Never point ngrok at 8082.
// Keys: key.pem (private, created on first run, next to this script) and public key derived from it.

import crypto from "node:crypto";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ISSUER = process.env.ISSUER || "https://radiogenic-rossana-nondefiling.ngrok-free.dev/realms/test";
const AUDIENCE = process.env.AUDIENCE || "alm-integration"; // confirm the real value with Boomi
const PUBLIC_PORT = 8081;
const MINT_PORT = 8082;

// ---- Key pair (RSA-2048), stored next to this script so it never changes by accident ----
const keyFile = path.join(path.dirname(fileURLToPath(import.meta.url)), "key.pem");
let privateKey;
if (fs.existsSync(keyFile)) {
  privateKey = crypto.createPrivateKey(fs.readFileSync(keyFile));
} else {
  ({ privateKey } = crypto.generateKeyPairSync("rsa", { modulusLength: 2048 }));
  fs.writeFileSync(keyFile, privateKey.export({ type: "pkcs8", format: "pem" }), { mode: 0o600 });
  console.log("Created new key.pem");
}
const jwk = crypto.createPublicKey(privateKey).export({ format: "jwk" });
const KID = crypto.createHash("sha256").update(jwk.n).digest("base64url").slice(0, 16);
const JWKS = JSON.stringify({ keys: [{ ...jwk, kid: KID, alg: "RS256", use: "sig" }] });

// ---- Minting ----
const b64 = (o) => Buffer.from(JSON.stringify(o)).toString("base64url");
function mint(email, seconds) {
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: "RS256", typ: "JWT", kid: KID };
  const claims = {
    iss: ISSUER,
    aud: AUDIENCE,
    sub: crypto.createHash("sha256").update(email).digest("hex").slice(0, 24),
    email,
    iat: now,
    exp: now + seconds,
    jti: crypto.randomUUID(), // unique per token (Boomi rejects reuse)
  };
  const input = `${b64(header)}.${b64(claims)}`;
  return `${input}.${crypto.sign("sha256", Buffer.from(input), privateKey).toString("base64url")}`;
}

// ---- Logging (strip control characters and cap length so requests can't forge log lines) ----
const clean = (s) => String(s ?? "-").replace(/[\x00-\x1f\x7f]/g, "?").slice(0, 120);
function logRequest(req, res) {
  res.on("finish", () => {
    const from = req.headers["x-forwarded-for"] || req.socket.remoteAddress;
    console.log(
      `${new Date().toISOString()} ${clean(req.method)} ${clean(req.url)} -> ${res.statusCode}` +
        ` from=${clean(from)} ua=${clean(req.headers["user-agent"])}`
    );
  });
}

// ---- Public server: JWKS only ----
http
  .createServer((req, res) => {
    logRequest(req, res);
    const url = new URL(req.url, "http://x");
    if (req.method === "GET" && url.pathname === "/realms/test/.well-known/jwks.json") {
      res.writeHead(200, { "Content-Type": "application/json", "Cache-Control": "public, max-age=300" });
      return res.end(JWKS);
    }
    res.writeHead(404).end("not found");
  })
  .listen(PUBLIC_PORT, "127.0.0.1", () => console.log(`public  : http://127.0.0.1:${PUBLIC_PORT}/.well-known/jwks.json  (ngrok -> this)`));

// ---- Private server: minting, localhost only ----
http
  .createServer((req, res) => {
    const url = new URL(req.url, "http://x");
    // Log mint calls without the query string, so emails and tokens never reach the log
    res.on("finish", () => console.log(`${new Date().toISOString()} MINT ${clean(url.pathname)} -> ${res.statusCode}`));
    if (req.method === "GET" && url.pathname === "/mint") {
      const email = url.searchParams.get("email") || "";
      const seconds = Math.min(Math.max(Number(url.searchParams.get("expiry")) || 300, 30), 3600);
      if (!/^[^@\s]{1,64}@[^@\s]{1,255}$/.test(email)) {
        return res.writeHead(400, { "Content-Type": "text/plain" }).end("need ?email=a@b.com&expiry=seconds\n");
      }
      res.writeHead(200, { "Content-Type": "text/plain", "Cache-Control": "no-store" });
      return res.end(mint(email, seconds) + "\n");
    }
    res.writeHead(404).end("not found");
  })
  .listen(MINT_PORT, "127.0.0.1", () => console.log(`mint    : http://127.0.0.1:${MINT_PORT}/mint?email=you@adobe.com&expiry=300  (local only)`));

console.log(`issuer=${ISSUER} aud=${AUDIENCE} kid=${KID}`);