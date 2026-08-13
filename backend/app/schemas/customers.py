import uuid
from pydantic import BaseModel
from datetime import datetime 

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str | None
    phone: str | None
    notes: str | None
    lead_id : uuid.UUID | None
    active: bool
    created_at: datetime
    updated_at: datetime

    class Congig:
        from_attributes = True
