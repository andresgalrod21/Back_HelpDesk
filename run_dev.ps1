# Ejecuta el backend con TLS si hay certificado dev
$key = "..\certificates\dev-selfsigned\server.key"
$crt = "..\certificates\dev-selfsigned\server.crt"
if ((Test-Path $key) -and (Test-Path $crt)) {
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8443 --ssl-keyfile $key --ssl-certfile $crt
} else {
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}