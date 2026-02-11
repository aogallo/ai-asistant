import anthropic
import instructor
from fastapi import Depends

from app.core.logging import logger
from app.infrastructure.anthropic_client import get_anthropic_client
from app.models.invoice import (
    InvoiceRowSchema,
    InvoiceSummary,
    InvoiceType,
)


class InvoiceAIService:
    def __init__(
        self,
        client: anthropic.AsyncAnthropic = Depends(get_anthropic_client),
    ) -> None:
        self.client = instructor.from_anthropic(client)

    async def analyze_batch(
        self,
        invoices: list[InvoiceRowSchema],
        invoice_type: InvoiceType,
    ) -> InvoiceSummary:
        invoice_data = [
            {
                "date": row.date,
                "company_nit": row.company_nit,
                "company_name": row.company_name,
                "dte_type": row.dte_type,
                "dte_number": row.dte_number,
                "total": row.total,
                "iva": row.iva,
                "state": row.state,
                "is_voided": row.is_voided,
            }
            for row in invoices
        ]

        prompt = f"""Analyze these {invoice_type.value} invoices
from Guatemala's SAT system. Provide a structured summary.

Invoice data ({len(invoices)} records):
{invoice_data[:100]}

{"... and more records" if len(invoices) > 100 else ""}

Provide:
1. Totals (invoices, amount, IVA)
2. Date range covered
3. Top 5 vendors by total amount
4. Any anomalies (unusually high amounts, voided invoices,
   duplicate patterns)
5. Voided invoice count
6. Suggested expense categories based on vendor names"""

        try:
            summary = await self.client.chat.completions.create(
                model="claude-sonnet-4-5-20250514",
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                response_model=InvoiceSummary,
            )
            return summary
        except Exception as e:
            logger.error("AI analysis failed: %s", str(e))
            raise
