from uuid import UUID

from pydantic import BaseModel


class OrderResponse(BaseModel):
    id: UUID
    customer_name: str