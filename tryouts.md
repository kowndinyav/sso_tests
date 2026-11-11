Yes, there are several ways to practice, from zero-setup to fully local.

**Easiest: samltest.id.** It hosts a free Shibboleth test IdP and test SP. You upload your own SP's metadata, log in with the test users, and read the IdP log to see what happened. That makes it a good way to try your own SP code against a real IdP. The site also offers its own test SP at `https://samltest.id/saml/sp`, for testing an IdP you control.

**Other hosted options:**
- SSOJet has a [hosted IdP simulator](https://ssojet.com/saml-tester) that covers the SAML 2.0 flows.
- A free OneLogin account includes a generic SAML test app, as pointed to by [samltool.com](https://www.samltool.com/test_sp.php).

**Local setup:** Docker-based test IdPs, such as a SimpleSAMLphp image, let you run an IdP on your machine and configure your SP's entity ID and ACS URL. [Example image](https://hub.docker.com/r/eilst/saml-idp)

**From my own knowledge, not verified in this search:**
- Keycloak runs locally in Docker and acts as a full SAML IdP, which suits a longer-term lab.
- A free Okta developer account lets you create a SAML app and see the real product behind your earlier questions. Check Okta's current signup terms.
- **SAML-tracer** is a browser extension (Firefox and Chrome) that shows each redirect and POST in the flow. Used with any of the above, it lets you see the actual AuthnRequest and SAMLResponse from steps 2, 3, 5, and 6 of the diagram.

**A learning path:**
1. Install SAML-tracer.
2. Log in to an app that uses SAML SSO, such as any test SP.
3. Find the `SAMLResponse` POST (step 6) in the tracer and decode the base64.
4. Locate the Issuer, Audience, Conditions, signature, and attributes in the XML.
5. Then set up your own small SP, using a library like `python3-saml` or `passport-saml`, against samltest.id.

I can walk through a decoded SAMLResponse with you if you paste one (with any real user data removed), or help set up a local Keycloak plus sample SP.

Sources:
- [samltest.id setup guide (Gluu)](https://gluu.org/docs/ce/4.1/integration/saas/saml_test_id/)
- [SSOJet SAML tester](https://ssojet.com/saml-tester)
- [samltool.com test SP](https://www.samltool.com/test_sp.php)
- [saml-idp Docker image](https://hub.docker.com/r/eilst/saml-idp)