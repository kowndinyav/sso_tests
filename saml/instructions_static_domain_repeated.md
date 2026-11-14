# Start SAML IdP
```
docker run -p 8080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  -e KC_HOSTNAME=https://radiogenic-rossana-nondefiling.ngrok-free.dev \
  -e KC_PROXY_HEADERS=xforwarded \
  -e KC_HTTP_ENABLED=true \
  -v keycloak_saml_idp_data:/opt/keycloak/data \
  quay.io/keycloak/keycloak:latest start-dev
```

# Run the SP side of things now

```
docker run --rm -p 9009:9009 \
   -e SP_ENTITY_ID=saml-test-sp \
   -e SP_METADATA_URL=https://radiogenic-rossana-nondefiling.ngrok-free.dev/realms/test/protocol/saml/descriptor \
   ghcr.io/beryju/saml-test-sp
```

# Ready now for testing the SP login
```
http://localhost:9009
```
