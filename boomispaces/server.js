const https = require('node:https');
const fs = require('node:fs');
const path = require('node:path');

const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Boomi Marketplace</title>
  <style>
    html, body { margin: 0; height: 100%; }
    iframe { display: block; width: 100%; height: 100%; border: 0; }
  </style>
</head>
<body>
  <h1>Boomi Marketplace</h1>
  <iframe src="https://spaces-embed-service.boomi.com/embed?token=eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ0MElNR3o4MFZ1SVZLNlNxYmtmeDM0WlczWVQwVFBWbzdkVEtsYWpqRjNRIn0.eyJleHAiOjE3OTQ0NTQ1MDIsImlhdCI6MTc5NDQ1NDIwMiwiYXV0aF90aW1lIjoxNzk0NDU0MTY0LCJqdGkiOiIyYTFlZDJlMi1iNjJjLTMxMjgtNTE3Ni03NjgzNjNlZjYyOGUiLCJpc3MiOiJodHRwczovL2RlZmluZS1yYWxlaWdoLXRlbGxzLXRvbi50cnljbG91ZGZsYXJlLmNvbS9yZWFsbXMvdGVzdCIsImF1ZCI6Im9pZGMtdGVzdCIsInN1YiI6IjVkMDUwNjNmLTg4OTMtNDA4Ni05MzRiLWU3Yjk3ZmRiYjVjOSIsInR5cCI6IklEIiwiYXpwIjoib2lkYy10ZXN0Iiwibm9uY2UiOiJuLTBTNiIsInNpZCI6IjAzYS0teG43aDJmUS0tWnBCMGVuYy1RciIsImF0X2hhc2giOiJScFkzZ25Jb1VVTGFOMnFNSVFKUzN3IiwiYWNyIjoiMSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6Im1vaGl0IG0iLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJtb2hpdCIsImdpdmVuX25hbWUiOiJtb2hpdCIsImZhbWlseV9uYW1lIjoibSIsImVtYWlsIjoibW1hbGxhbXBhdGlAYWRvYmUuY29tIn0.Y42njCvqUQDqwP_BLdPvtwDhtl79c_i4pcfMED-THDxqyePzAn55q4IaBdP2iSA9-KEm2RM1S_KtV5NzB55ll79TxY3W-NPfaovdfpfv41dmPCPXRRLgtjui0O2Wn5YT2Xz21O4mnoTIoI2kZkmLXMuNYiaH0D483oiVEicm6W9mDDewuZBoB0V6EJubyoK1nuM35Cq-mu-ei406KIXr4o1pJkN2GwvP8oqkxRdDcTu3EoveXLOMvUtoLmO6pxX1R0_6rTDm6-TWz7Tmisyba29ImNVzl5jPW53eHJ2F52YXlNgpYJGBwsB5vrbA6bq7YVEhB0_lhcFMGljQPQguNg" title="Boomi Marketplace"></iframe>
</body>
</html>`;

const port = 8443;
const server = https.createServer({
  key: fs.readFileSync(path.join(__dirname, 'vkalmapp.com-key.pem')),
  cert: fs.readFileSync(path.join(__dirname, 'vkalmapp.com.pem')),
}, (req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(html);
});

server.on('error', (error) => {
  console.error(`Unable to start server on port ${port}:`, error.message);
  process.exitCode = 1;
});

server.on('listening', () => {
  console.log(`Server running at https://vkalmapp.com:${port}`);
});

server.listen(port);
