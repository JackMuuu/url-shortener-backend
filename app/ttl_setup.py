from app.database import db

async def ensure_ttl_index():
    # Create TTL index on the expires_at field (only once)
    await db.urls.create_index("expires_at", expireAfterSeconds=0)