# Static domain setup
```
ngrok config add-authtoken 2B61NnXtbIR3wEs4wBYxhMvojQD_HqjxeCej45N4gBYA2S5A
ngrok http 8080 --url https://radiogenic-rossana-nondefiling.ngrok-free.dev
```


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

# Create Realm
```
place holder for creating test realm (only once)
```


# Run the SP side of things now

```
docker run --rm -p 9009:9009 \
   -e SP_ENTITY_ID=saml-test-sp \
   -e SP_METADATA_URL=https://radiogenic-rossana-nondefiling.ngrok-free.dev/realms/test/protocol/saml/descriptor \
   ghcr.io/beryju/saml-test-sp
```

# create sp metadata xml
```
cd /Users/kowndiny/work/github_personal/sso_tests/saml/sp
curl -o sp.xml http://localhost:9009/saml/metadata
```


# import sp metadata into 
```
Ensure that "Encryption keys config" -> "Encrypt assertions" is off
```

# Add user
```
add user
```

# Ready now for testing the SP login
```
http://localhost:9009
```
