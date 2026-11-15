// Decode a token and VERIFY its signature with the key from token_server.mjs.
// (A JWT is signed, not encrypted: anyone can read it; the signature proves who made it.)
//
//   pbpaste | node verify_token.mjs
//
// Uses key.pem next to this script (same folder as token_server.mjs). No npm packages.
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const token = fs.readFileSync(0, "utf8").trim().slice(0, 16384);
const parts = token.split(".");
if (parts.length !== 3 || /\s/.test(token)) {
  console.error("error: expected one line with 3 dot-separated parts");
  process.exit(2);
}

let header, claims;
try {
  header = JSON.parse(Buffer.from(parts[0], "base64url"));
  claims = JSON.parse(Buffer.from(parts[1], "base64url"));
} catch {
  console.error("error: header/claims are not valid base64url JSON");
  process.exit(2);
}
console.log("== HEADER ==\n" + JSON.stringify(header, null, 2));
console.log("\n== CLAIMS ==\n" + JSON.stringify(claims, null, 2));
const t = (s) => (Number.isFinite(s) ? new Date(s * 1000).toISOString() : "n/a");
console.log(`\niat ${t(claims.iat)}\nexp ${t(claims.exp)}\nnow ${new Date().toISOString()}`);

// ---- Checks ----
const results = [];
const keyFile = path.join(path.dirname(fileURLToPath(import.meta.url)), "key.pem");
if (!fs.existsSync(keyFile)) {
  results.push(["FAIL", "key.pem not found next to this script"]);
} else {
  const publicKey = crypto.createPublicKey(crypto.createPrivateKey(fs.readFileSync(keyFile)));
  const kid = crypto.createHash("sha256").update(publicKey.export({ format: "jwk" }).n).digest("base64url").slice(0, 16);
  const algOk = header.alg === "RS256"; // only accept the algorithm we issue
  const sigOk = algOk && crypto.verify("sha256", Buffer.from(`${parts[0]}.${parts[1]}`), publicKey, Buffer.from(parts[2], "base64url"));
  results.push([algOk ? "ok" : "FAIL", algOk ? "alg is RS256" : `unexpected alg ${JSON.stringify(header.alg)}`]);
  results.push([sigOk ? "ok" : "FAIL", sigOk ? "signature is VALID (made by this key)" : "signature is INVALID"]);
  results.push([header.kid === kid ? "ok" : "FAIL", header.kid === kid ? "kid matches this key" : `kid ${header.kid} does not match this key (${kid})`]);
}
const now = Date.now() / 1000;
results.push([claims.exp > now ? "ok" : "FAIL", claims.exp > now ? `not expired (${Math.floor(claims.exp - now)}s left)` : "EXPIRED"]);
for (const c of ["iss", "aud", "sub", "email", "jti"]) if (!claims[c]) results.push(["FAIL", `missing claim ${c}`]);

console.log("\n== CHECKS ==");
for (const [s, m] of results) console.log(`[${s.padStart(4)}] ${m}`);
process.exit(results.some(([s]) => s === "FAIL") ? 1 : 0);