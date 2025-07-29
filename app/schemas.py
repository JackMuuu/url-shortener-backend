from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class URLRequest(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None
    expiration: Optional[str] = None