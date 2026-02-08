
from fastapi import FastAPI, Depends, HTTPException, status 
from fastapi.security import APIKeyHeader   
from pydantic import BaseModel  
from datetime import datetime
from collections import defaultdict
import time 
import mi_paquete  # Tu paquete instalado   
app = FastAPI(title="Mi Paquete API 💰", version="1.0.0")
# Rate limiting en memoria
request_counts = defaultdict(list)      
# API KEYS
FREE_KEYS = ["demo123"]  # 100 req/día  
PAID_KEYS = {"user1": "sk_live_user1"}  # Ilimitado
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)   
class InputData(BaseModel):
    texto: str  
class OutputData(BaseModel):
    resultado: str
    version: str = "0.1.0"  
def requests_today(api_key: str) -> int:
    """Cuenta requests del día para free tier"""
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    count = sum(1 for t in request_counts[api_key] if t >= today.timestamp())
    return count    
@app.get("/")       
async def home(api_key: str | None = Depends(api_key_header)):
    return {"mensaje": "¡API PAGA funcionando! 🚀", "paquete": "mi_paquete 0.1.0"   }   
@app.post("/procesar/", response_model=OutputData)  
async def procesar(input: InputData, api_key: str | None = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=401, detail="Falta header X-API-Key")
    
    # FREE TIER: 100 req/día
    if api_key in FREE_KEYS:
        count = requests_today(api_key)
        if count >= 100:
            raise HTTPException(status_code=429, detail="Free tier: máximo 100 req/día")
        request_counts[api_key].append(time.time())
    
    # PAID TIER - COBRO REAL
    elif api_key not in PAID_KEYS.values():
        raise HTTPException(status_code=401, detail="API Key inválida. Compra: mi-paquete.com")
    
    # 💰 COBRO STRIPE REAL €29
    import os
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    
    payment = stripe.PaymentIntent.create(
        amount=2900,  # €29.00
        currency="eur",
        metadata={
            "api_key": api_key,
            "texto": input.texto[:100]
        }
    )
    
    # TU PAQUETE + COBRO CONFIRMADO
    resultado = f"💰 COBRADO €29 | {mi_paquete.hola()} | {input.texto.upper()}"
    
    return OutputData(resultado=resultado, version=mi_paquete.__version__)  
@app.get("/info")
async def info():
    return {"free_limit": "100 req/día", "paid": "Ilimitado $29/mes"}   
