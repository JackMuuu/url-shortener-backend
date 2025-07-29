from fastapi import APIRouter, HTTPException, Request
from app.database import db
from app.models import URL
from datetime import datetime, timedelta
from app.schemas import URLRequest
import string, random
import qrcode
from io import BytesIO
import base64
import os
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

def generate_short_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@router.post("/shorten")
async def shorten_url(payload: URLRequest):
    original_url = payload.original_url
    custom_alias = payload.custom_alias
    expiration_choice = payload.expiration
    collection = db.urls

    short_id = custom_alias or generate_short_id()

    if await collection.find_one({"short_id": short_id}):
        raise HTTPException(status_code=400, detail="Alias already exists")

    # Map expiration strings to time deltas
    duration_map = {
        "10min": timedelta(minutes=10),
        "1hour": timedelta(hours=1),
        "1day": timedelta(days=1),
        "1week": timedelta(weeks=1),
    }

    # Default to 1 day if not found or custom
    if expiration_choice in duration_map:
        expires_at = datetime.utcnow() + duration_map[expiration_choice]
    else:
        try:
            expires_at = datetime.fromisoformat(expiration_choice)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid expiration format")

    url_data = {
        "original_url": str(original_url),
        "short_id": short_id,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "clicks": 0,
    }

    # Generate QR code in memory
    short_url = f"{BASE_URL}/{short_id}"
    qr = qrcode.make(short_url)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    img_bytes = buf.getvalue()
    qr_base64 = base64.b64encode(img_bytes).decode("utf-8")

    await collection.insert_one(url_data)
    return {"short_url": short_url, "qr_code_base64": qr_base64}