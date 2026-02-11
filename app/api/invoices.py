from fastapi import APIRouter, Depends, Form, UploadFile

from app.core.logging import logger
from app.models.invoice import InvoiceType
from app.schemas.response import UploadResult
from app.services.invoice_ai_service import InvoiceAIService
from app.services.invoice_service import InvoiceService

router = APIRouter()


@router.post("/invoice/upload", response_model=UploadResult)
async def process_sat_file(
    file: UploadFile,
    invoiceType: InvoiceType = Form(...),
    invoice_service: InvoiceService = Depends(),
    ai_service: InvoiceAIService = Depends(),
) -> UploadResult:
    file_bytes = await file.read()

    result = await invoice_service.process_sat_file(
        file_bytes=file_bytes,
        filename=file.filename or "unknown",
        invoice_type=invoiceType,
    )

    try:
        summary = await ai_service.analyze_batch(
            invoices=invoice_service.last_validated_rows,
            invoice_type=invoiceType,
        )
        result.ai_summary = summary
    except Exception as e:
        logger.warning("AI analysis skipped: %s", str(e))

    return result
