import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.db_models import (
    Company,
    Invoice,
    InvoiceTaxDetail,
    UploadBatch,
)


class CompanyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(
        self, nit: str, name: str, description: str
    ) -> Company:
        stmt = select(Company).where(Company.nit == nit)
        result = await self.session.execute(stmt)
        company = result.scalar_one_or_none()

        if company is None:
            company = Company(nit=nit, name=name, description=description)
            self.session.add(company)
            await self.session.flush()

        return company


class InvoiceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_batch(
        self,
        filename: str,
        invoice_type: str,
    ) -> UploadBatch:
        batch = UploadBatch(
            filename=filename,
            invoice_type=invoice_type,
        )
        self.session.add(batch)
        await self.session.flush()
        return batch

    async def update_batch(
        self,
        batch: UploadBatch,
        total_rows: int,
        total_amount: float,
        total_iva: float,
        status: str,
    ) -> UploadBatch:
        batch.total_rows = total_rows
        batch.total_amount = total_amount
        batch.total_iva = total_iva
        batch.status = status
        self.session.add(batch)
        await self.session.flush()
        return batch

    async def create_many(self, invoices: list[Invoice]) -> list[Invoice]:
        self.session.add_all(invoices)
        await self.session.flush()
        return invoices

    async def get_batch_summary(
        self, batch_id: uuid.UUID
    ) -> UploadBatch | None:
        stmt = select(UploadBatch).where(UploadBatch.id == batch_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class TaxDetailRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_many(
        self, details: list[InvoiceTaxDetail]
    ) -> list[InvoiceTaxDetail]:
        self.session.add_all(details)
        await self.session.flush()
        return details
