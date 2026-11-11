## The problem SAML solves

Without SSO, every app stores its own passwords and logs users in itself. SAML lets apps **delegate login to one trusted system**. The app gets a signed statement saying "this person has been authenticated", and never handles the credentials.

## Assumptions SAML makes

1. **The browser is untrusted but is the only messenger.** The app and the IdP rarely talk directly. Everything passes through the user's browser, so messages must protect themselves (signatures).
2. **Trust is set up in advance, out of band.** An admin configures both sides before any user logs in.
3. **Proof of identity is a digital signature.** Whoever holds the IdP's private key can vouch for users.
4. **Clocks are roughly in sync.** Assertions have validity windows.
5. **TLS protects the transport.** SAML signs messages but still expects HTTPS.

## The parties

- **User / principal:** the person.
- **User agent:** the browser.
- **Identity Provider (IdP):** authenticates users and issues assertions (Okta, Entra ID).
- **Service Provider (SP):** the app that consumes assertions.

## Artifacts, in the order they appear

| Artifact | What it is | Who makes it |
|---|---|---|
| **Metadata XML** | A config file describing an entity: its entity ID, endpoints (URLs), and public certificate. Exchanged during setup. | Both |
| **Entity ID** | A unique name for the IdP or SP, usually a URL-like string. Used to say "this is for me". | Both |
| **Key pair + certificate** | Private key (kept secret) signs. The public cert (shared in metadata) verifies. | IdP (always), SP (optional) |
| **AuthnRequest** | SP's "please authenticate this user" message. | SP |
| **RelayState** | An opaque value passed through the whole flow, usually the page the user wanted. | SP |
| **SAML Response** | The IdP's reply envelope: status, issuer, and the assertion. | IdP |
| **Assertion** | The core payload: who the user is, how they logged in, attributes, validity window, audience. Signed. | IdP |
| **Session cookie** | The SP's own login session, created after validating the assertion. SAML is then out of the picture. | SP |

## Key endpoints (URLs in metadata)

- **SSO URL:** the IdP endpoint that receives AuthnRequests.
- **ACS URL (Assertion Consumer Service):** the SP endpoint that receives the SAML Response.
- **SLO URL:** optional endpoint for Single Logout.

## Inside an assertion

- **Issuer:** who created it.
- **Subject / NameID:** the user's identifier (email, ID, and so on).
- **Conditions:** `NotBefore`, `NotOnOrAfter`, and `Audience` (which SP it's for).
- **AuthnStatement:** when and how the user authenticated, including the `SessionIndex`.
- **AttributeStatement:** extra claims such as name, email, and groups.
- **Signature:** the XMLDSig over the above.

## Concepts worth knowing

- **Federation:** two separate organizations or systems agreeing to trust each other's identities.
- **Authentication vs authorization:** SAML proves *who you are*. What you can do in the app is the SP's decision, often based on attributes like groups.
- **Binding:** how a message is physically carried over HTTP. *HTTP-Redirect* puts it in the URL (used for requests). *HTTP-POST* uses an auto-submitted form (used for responses, which are too big for URLs).
- **Profile:** a recipe combining messages and bindings. Web Browser SSO is the one you've been studying.
- **SP-initiated vs IdP-initiated:** whether the flow starts at the app or at the IdP's dashboard.
- **Signing vs encryption:** signing proves origin and integrity. Encryption hides content. They're separate and independent.
- **Attribute mapping:** matching IdP attribute names (`groups`) to what the SP expects (`roles`). A classic source of config bugs.
- **JIT provisioning:** the SP creates the user account at first login from the assertion. The alternative is pre-provisioning, e.g. with SCIM.
- **SLO (Single Logout):** logging out of the IdP and all connected apps. It's notoriously unreliable in practice.

## Common pitfalls

- Expired or rotated IdP certificates.
- Clock skew rejecting assertions.
- Wrong Entity ID or ACS URL (audience mismatch).
- Attribute names not matching.
- NameID format mismatch (email vs persistent ID).
- Trusting a cert from inside the response rather than the pinned one.
- XML signature wrapping attacks. Use a well-tested library and never hand-roll validation.

## Where it sits among related standards

SAML (2005, XML, enterprise) and OIDC (2014, JSON/JWT, built on OAuth 2.0) solve the same login-delegation problem. If you understand SAML's pieces, OIDC maps over directly: assertion becomes ID token, ACS URL becomes redirect URI, metadata becomes the discovery document.

I can go deeper on any piece, such as reading an actual raw SAML Response XML line by line, which is the best way to make this concrete.