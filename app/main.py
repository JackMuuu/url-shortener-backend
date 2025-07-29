from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import shortener
from fastapi.staticfiles import StaticFiles
from app.database import db

from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from datetime import datetime
from app.ttl_setup import ensure_ttl_index
from contextlib import asynccontextmanager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_ttl_index()  # TTL index setup
    yield

app.include_router(shortener.router)


@app.get("/{short_id}")
async def redirect_to_original(short_id: str):
    url = await db.urls.find_one({"short_id": short_id})
    if not url:
        return {"error": "URL not found"}
    if url.get("expires_at") and datetime.utcnow() > url["expires_at"]:
        return {"error": "URL expired"}
    await db.urls.update_one({"short_id": short_id}, {"$inc": {"clicks": 1}})
    return RedirectResponse(url["original_url"])