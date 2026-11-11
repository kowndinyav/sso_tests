You'll run two things locally with Docker, an IdP (Keycloak) and a tiny test SP, and watch the login with SAML-tracer. Docker needs to be installed first. The SP's settings below come from its README. The Keycloak screens are from memory, so labels may differ slightly by version.

**1. Start the IdP (Keycloak)**

```
docker run -p 8080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:latest start-dev
```

Open http://localhost:8080 and log in as `admin` / `admin`.

**2. Create a realm and a user**

- Create a realm named `test`.
- Under Users, add `alice`. In Credentials, set a password with Temporary turned off.

**3. Copy the IdP's signing certificate.** This is the trust step.

- Go to Realm settings → Keys. On the RS256 row, click Certificate and copy the text.

**4. Start the SP, using that cert**

```
 mkdir ./idp-meta && cd ./idp-meta
 curl -o idp.xml http://localhost:8080/realms/test/protocol/saml/descriptor
 python3 -m http.server 8000 --bind 127.0.0.1

docker run --rm -p 9009:9009 \
   -e SP_ENTITY_ID=saml-test-sp \
   -e SP_METADATA_URL=http://host.docker.internal:8000/idp.xml \
   ghcr.io/beryju/saml-test-sp
```

http://localhost:8080/realms/test/protocol/saml/descriptor

```
docker run --rm -p 9009:9009 \
  -e SP_ENTITY_ID=saml-test-sp \
  -e SP_SSO_URL=http://localhost:8080/realms/test/protocol/saml \
  -e SP_SIGNING_CERT='MIIClzCCAX8CBgGhxf3i1zANBgkqhkiG9w0BAQsFADAPMQ0wCwYDVQQDDAR0ZXN0MB4XDTI2MTExMDE1MDMzMloXDTM2MTExMDE1MDUxMlowDzENMAsGA1UEAwwEdGVzdDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAPSR+7vVN0jVGXqoXaXsl6oRQR9A/5uIfp2/wFbXtWlHugT3F30eCdlr026Hu309gJGItWi8ZTW9+kkJdsBO76PORuXmQRpr4BNlQH2LkZc92yhdBNfyYx0JUK7V05boxQgnYXHFFI75bcXhcpzDcUHVGoaY5ZXYgbz6tVAZAtxqshW89fmY2D3P1f89cVLHuJAkNhqFJW3UuE3YCS+IyuwILVxGgLs65ndFMQgoq059KIHuuBwEvuoKXq+nynv0E3XE5eZe+DKdAvUiiBygdGPCp5HUVpG5ZqOBkxFi0doN8QQ4T8428CFs7l3urFE823WiJTDz2Oum34Duv18JgA8CAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAI/8AWuq/e4jLCw/Pa2sS/rW9U764DvyjI6Myck9KZHdGOILr2TCWXmUQk4vzczmu6hxAQSxNEp3ey7h9HlQeiyQTYbzzssu2jZsgKnHtFRlktcWCntOabPau+rUhLRulkfhy+WB2SHYdnVr93jCSd/aT+bLLq5P5tCtK0Aj/Ktf0DSRIeA7rmos76icVBFeo2JTQn6D9BPR+nvj/tFsmh1Hp6i7ZOR223aBRb3UIFPy2suOjbFygq9UFQeXFIf0bsH7Y7x8gB9o7HE7zNZEPAkXGfOz2To3WLn4t1Ih5ZPR1tubMjhb9tNNaodHgNtchS1+d5jTwKpN+Ztgw70X9iA==' \
  ghcr.io/beryju/saml-test-sp
```

**5. Register the SP in Keycloak (the metadata exchange)**

- In Keycloak, go to Clients → Import client and upload `sp.xml`, then save.
- Open the client's Keys tab and turn off Client signature required, because this test SP doesn't sign its requests.

**6. Watch it happen**

- Open SAML-tracer in your browser.
- Visit http://localhost:9009/ and log in as `alice`.
- In the tracer, find the entries marked SAML. The first is the AuthnRequest (step 3 of the diagram), and the POST to `/saml/acs` carries the SAMLResponse (step 6).

If step 6 shows an error, paste it here and I'll help debug. Signature and audience mismatches are the usual causes.