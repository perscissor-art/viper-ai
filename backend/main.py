from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

# ==========================
# VIPER ENGINES
# ==========================

from scanner import scanner
from vision import engine as vision

app = FastAPI(
    title="VIPER AI PRO",
    version="1.0"
)

# ==========================
# CORS
# ==========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# HOME
# ==========================

@app.get("/")
def home():

    return {
        "name": "VIPER AI PRO",
        "version": "1.0",
        "status": "ONLINE",
        "mode": "ICT Screenshot Scanner"
    }

# ==========================
# LIVE MT5 SCAN
# ==========================

@app.get("/scan/{symbol}")
def live_scan(
    symbol: str,
    balance: float = 1000,
    risk: float = 1
):

    try:

        result = scanner.scan(
            symbol=symbol,
            balance=balance,
            risk=risk
        )

        return result

    except Exception as e:

        return {
            "error": True,
            "message": str(e)
        }

# ==========================
# SCREENSHOT AI SCAN
# ==========================

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...)
):

    try:

        image_bytes = await file.read()

        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

        result = vision.analyze(image)

        return {

            # Main Signal
            "signal": result.signal,
            "confidence": result.confidence,
            "grade": result.grade,
            "status": result.status,

            # Trade Levels
            "entry": result.entry,
            "stop_loss": result.stop_loss,
            "take_profit": result.take_profit,

            # Vision Quality
            "candles_detected": result.candles_detected,
            "calibration": result.calibration_confidence,

            # ICT Confluences
            "bos": result.bos,
            "choch": result.choch,
            "liquidity": result.liquidity,
            "fvg": result.fvg,
            "order_block": result.order_block,
            "premium_discount": result.premium_discount

        }

    except Exception as e:

        return {
            "error": True,
            "message": str(e)
        }

# ==========================
# HEALTH CHECK
# ==========================

@app.get("/health")
def health():

    return {
        "server": "running",
        "vision": "connected",
        "scanner": "connected"
    }