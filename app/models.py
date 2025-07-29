from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class URL(BaseModel):
    original_url: HttpUrl
    short_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    created_by: Optional[str] = None
    clicks: int = 0
    qr_code_path: Optional[str] = None
    custom_alias: Optional[str] = None
