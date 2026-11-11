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


**3. Setup saml descriptor or metadataurl
```
 mkdir ./idp-meta && cd ./idp-meta
 curl -o idp.xml http://localhost:8080/realms/test/protocol/saml/descriptor
 python3 -m http.server 8000 --bind 127.0.0.1
```

**4. Start the SP, using that saml descriptor**

```
docker run --rm -p 9009:9009 \
   -e SP_ENTITY_ID=saml-test-sp \
   -e SP_METADATA_URL=http://host.docker.internal:8000/idp.xml \
   ghcr.io/beryju/saml-test-sp
```


**5. Register the SP in Keycloak (the metadata exchange)**
```
curl -o sp.xml http://localhost:9009/saml/metadata
```

- In Keycloak, go to Clients → Import client and upload `sp.xml`, then save.
- Open the client's Keys tab and turn off Client signature required, because this test SP doesn't sign its requests.

**6. Watch it happen**

- Open SAML-tracer in your browser.
- Visit http://localhost:9009/ and log in as `alice`.
- In the tracer, find the entries marked SAML. The first is the AuthnRequest (step 3 of the diagram), and the POST to `/saml/acs` carries the SAMLResponse (step 6).

If step 6 shows an error, paste it here and I'll help debug. Signature and audience mismatches are the usual causes.