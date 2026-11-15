```
docker run --rm --name jwks-proxy -p 8081:8081 -v "$PWD/nginx.conf":/etc/nginx/conf.d/default.conf:ro nginx:alpine
```


```
ngrok http 8081 --url https://radiogenic-rossana-nondefiling.ngrok-free.dev
```