import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.invoice import InvoiceSummary


class UploadResult(BaseModel):
    batch_id: uuid.UUID
    filename: str
    invoice_type: str
    total_rows: int
    total_amount: float
    total_iva: float
    status: str
    uploaded_at: datetime
    ai_summary: InvoiceSummary | None = None
