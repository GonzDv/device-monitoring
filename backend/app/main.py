from fastapi import FastAPI

app = FastAPI(
  titele="Device Monitoring API",
  description="API for device monitoring through SNMP",
  version="0.1.0",
)

@app.get("/healthz")
def health_check():
  """Endpont de salud: confirma que la API esta activa"""
  return {"status": "ok"}