from io import BytesIO

import pandas as pd
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.infrastructure.database import get_session
from app.infrastructure.repositories import (
    CompanyRepository,
    InvoiceRepository,
    TaxDetailRepository,
)
from app.models.db_models import (
    BatchStatus,
    Company,
    Invoice,
    InvoiceTaxDetail,
)
from app.models.invoice import InvoiceRowSchema, InvoiceType
from app.schemas.response import UploadResult

COLUMN_RENAME_MAP = {
    "Fecha de emisión": "date",
    "Número de Autorización": "authorization_number",
    "Tipo de DTE (nombre)": "dte_type",
    "Serie": "serie",
    "Número del DTE": "dte_number",
    "Clasificación emisor": "clasificacion_emisor",
    "Exportación": "exportation",
    "NIT del emisor": "company_nit",
    "Nombre completo del emisor": "company_name",
    "Código de establecimiento": "company_code",
    "Nombre del establecimiento": "company_description",
    "ID del receptor": "customer_nit",
    "Nombre completo del receptor": "customer_name",
    "NIT del Certificador": "certificator_nit",
    "Nombre completo del Certificador": "certificator_name",
    "Estado": "state",
    "Moneda": "money",
    "Gran Total (Moneda Original)": "total",
    "IVA (monto de este impuesto)": "iva",
    "Marca de anulado": "is_voided",
    "Fecha de anulación": "voided_date",
    "Petróleo (monto de este impuesto)": "petroleum",
    "Turismo Hospedaje (monto de este impuesto)": "hotel",
    "Turismo Pasajes (monto de este impuesto)": "tickets",
    "Timbre de Prensa (monto de este impuesto)": "press_stamp",
    "Bomberos (monto de este impuesto)": "firefighters",
    "Tasa Municipal (monto de este impuesto)": "municipal_tax",
    "Bebidas alcohólicas (monto de este impuesto)": ("alcoholic_tax"),
    "Tabaco (monto de este impuesto)": "tobacco_tax",
    "Cemento (monto de este impuesto)": "cement_tax",
    "Bebidas no Alcohólicas (monto de este impuesto)": ("no_alcoholic_tax"),
    "Tarifa Portuaria (monto de este impuesto)": ("port_tariff_tax"),
}

CHUNK_SIZE = 1000


class InvoiceService:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
    ) -> None:
        self.session = session
        self.company_repo = CompanyRepository(session)
        self.invoice_repo = InvoiceRepository(session)
        self.tax_detail_repo = TaxDetailRepository(session)
        self.last_validated_rows: list[InvoiceRowSchema] = []

    async def process_sat_file(
        self,
        file_bytes: bytes,
        filename: str,
        invoice_type: InvoiceType,
    ) -> UploadResult:
        try:
            engine = "xlrd" if filename.endswith(".xls") else "openpyxl"
            df = pd.read_excel(BytesIO(file_bytes), engine=engine)
            df.rename(columns=COLUMN_RENAME_MAP, inplace=True)

            all_validated: list[InvoiceRowSchema] = []

            for chunk_start in range(0, len(df), CHUNK_SIZE):
                chunk = df.iloc[chunk_start : chunk_start + CHUNK_SIZE]
                validated_rows = self._validate_chunk(chunk, chunk_start)
                all_validated.extend(validated_rows)

            if not all_validated:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No valid rows found in file",
                )

            self.last_validated_rows = all_validated

            result = await self._process_validated_rows(
                rows=all_validated,
                filename=filename,
                invoice_type=invoice_type,
            )
            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error processing file: %s", str(e))
            raise HTTPException(
                status_code=(status.HTTP_500_INTERNAL_SERVER_ERROR),
                detail="Error when processing file",
            ) from e

    def _validate_chunk(
        self, chunk: pd.DataFrame, offset: int
    ) -> list[InvoiceRowSchema]:
        """Validate rows using Pydantic, collect errors."""
        validated: list[InvoiceRowSchema] = []

        for _, row in chunk.iterrows():
            try:
                validated_row = InvoiceRowSchema.model_validate(row.to_dict())
                validated.append(validated_row)
            except Exception as e:
                logger.error(
                    "Failing creating the Invoice Row: %s",
                    str(e),
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=("Some rows do not match the expected format"),
                ) from e

        return validated

    async def _process_validated_rows(
        self,
        rows: list[InvoiceRowSchema],
        filename: str,
        invoice_type: InvoiceType,
    ) -> UploadResult:
        """Process validated rows: companies, invoices,
        tax details."""
        batch = await self.invoice_repo.create_batch(
            filename=filename,
            invoice_type=invoice_type.value,
        )

        company_cache: dict[str, Company] = {}
        invoices: list[Invoice] = []
        tax_details: list[InvoiceTaxDetail] = []

        for row in rows:
            if row.company_nit not in company_cache:
                company = await self.company_repo.get_or_create(
                    nit=row.company_nit,
                    name=row.company_name,
                    description=row.company_description,
                )
                company_cache[row.company_nit] = company

            company = company_cache[row.company_nit]

            invoice = Invoice(
                batch_id=batch.id,
                company_id=company.id,
                authorization_number=(row.authorization_number),
                dte_type=row.dte_type,
                serie=row.serie,
                dte_number=row.dte_number,
                date=row.date,
                customer_nit=row.customer_nit,
                customer_name=row.customer_name,
                certificator_nit=row.certificator_nit,
                certificator_name=row.certificator_name,
                state=row.state,
                money=row.money,
                total=row.total,
                iva=row.iva,
                is_voided=row.is_voided,
                voided_date=row.voided_date or "",
                exportation=row.exportation,
            )
            invoices.append(invoice)

        await self.invoice_repo.create_many(invoices)

        for invoice, row in zip(invoices, rows, strict=True):
            tax_detail = InvoiceTaxDetail(
                invoice_id=invoice.id,
                petroleum=row.petroleum,
                hotel=row.hotel,
                tickets=row.tickets,
                press_stamp=row.press_stamp,
                firefighters=row.firefighters,
                municipal_tax=row.municipal_tax,
                alcoholic_tax=row.alcoholic_tax,
                tobacco_tax=row.tobacco_tax,
                cement_tax=row.cement_tax,
                no_alcoholic_tax=row.no_alcoholic_tax,
                port_tariff_tax=row.port_tariff_tax,
            )
            tax_details.append(tax_detail)

        await self.tax_detail_repo.create_many(tax_details)

        total_amount = sum(r.total for r in rows)
        total_iva = sum(r.iva for r in rows)

        batch = await self.invoice_repo.update_batch(
            batch=batch,
            total_rows=len(rows),
            total_amount=total_amount,
            total_iva=total_iva,
            status=BatchStatus.COMPLETED,
        )

        await self.session.commit()

        return UploadResult(
            batch_id=batch.id,
            filename=filename,
            invoice_type=batch.invoice_type,
            total_rows=batch.total_rows,
            total_amount=batch.total_amount,
            total_iva=batch.total_iva,
            status=batch.status,
            uploaded_at=batch.uploaded_at,
        )
