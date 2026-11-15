## Ngrok for public domain and a nasty hack for public cert endpoint
```
ngrok http 8081 --url https://radiogenic-rossana-nondefiling.ngrok-free.dev
```

## Start token mint service

Folder: `alm_token_endpoint`
```
node server.js
```

## Generate the token
```
curl "http://localhost:8082/mint?email=mmallampati@adobe.com&expiry=3600"
```

## Run the BoomiEmbed App
Folder : `boomispaces`
```
# update the emded token inside server.js

node server.js
```
