import pytest

from app.infrastructure.repositories import (
    CompanyRepository,
    InvoiceRepository,
    TaxDetailRepository,
)
from app.models.db_models import (
    BatchStatus,
    Invoice,
    InvoiceTaxDetail,
)


@pytest.mark.asyncio
class TestCompanyRepository:
    async def test_create_new_company(self, session):
        repo = CompanyRepository(session)
        company = await repo.get_or_create(
            nit="123456-7",
            name="Test Co",
            description="Desc",
        )
        assert company.nit == "123456-7"
        assert company.name == "Test Co"
        assert company.id is not None

    async def test_get_existing_company(self, session):
        repo = CompanyRepository(session)
        first = await repo.get_or_create(
            nit="999-1",
            name="Existing",
            description="Desc",
        )
        second = await repo.get_or_create(
            nit="999-1",
            name="Existing",
            description="Desc",
        )
        assert first.id == second.id


@pytest.mark.asyncio
class TestInvoiceRepository:
    async def test_create_batch(self, session):
        repo = InvoiceRepository(session)
        batch = await repo.create_batch(
            filename="test.xlsx",
            invoice_type="expenses",
        )
        assert batch.filename == "test.xlsx"
        assert batch.status == BatchStatus.PROCESSING

    async def test_update_batch(self, session):
        repo = InvoiceRepository(session)
        batch = await repo.create_batch(
            filename="test.xlsx",
            invoice_type="expenses",
        )
        updated = await repo.update_batch(
            batch=batch,
            total_rows=10,
            total_amount=1000.0,
            total_iva=120.0,
            status=BatchStatus.COMPLETED,
        )
        assert updated.total_rows == 10
        assert updated.status == BatchStatus.COMPLETED

    async def test_create_many_invoices(self, session):
        repo = InvoiceRepository(session)
        company_repo = CompanyRepository(session)

        batch = await repo.create_batch(
            filename="test.xlsx",
            invoice_type="expenses",
        )
        company = await company_repo.get_or_create(
            nit="111-2",
            name="Vendor",
            description="Desc",
        )

        invoices = [
            Invoice(
                batch_id=batch.id,
                company_id=company.id,
                authorization_number="AUTH-1",
                dte_type="FACT",
                serie="A",
                dte_number="1",
                date="2024-01-01",
                customer_nit="222-3",
                customer_name="Client",
                certificator_nit="333-4",
                certificator_name="Cert",
                state="Vigente",
                money="GTQ",
                total=100.0,
                iva=12.0,
            )
        ]
        result = await repo.create_many(invoices)
        assert len(result) == 1
        assert result[0].id is not None


@pytest.mark.asyncio
class TestTaxDetailRepository:
    async def test_create_many_details(self, session):
        invoice_repo = InvoiceRepository(session)
        company_repo = CompanyRepository(session)
        tax_repo = TaxDetailRepository(session)

        batch = await invoice_repo.create_batch(
            filename="test.xlsx",
            invoice_type="expenses",
        )
        company = await company_repo.get_or_create(
            nit="444-5",
            name="V",
            description="D",
        )
        invoice = Invoice(
            batch_id=batch.id,
            company_id=company.id,
            authorization_number="AUTH-2",
            dte_type="FACT",
            serie="B",
            dte_number="2",
            date="2024-02-01",
            customer_nit="555-6",
            customer_name="C",
            certificator_nit="666-7",
            certificator_name="Cert",
            state="Vigente",
            money="GTQ",
            total=200.0,
            iva=24.0,
        )
        session.add(invoice)
        await session.flush()

        details = [
            InvoiceTaxDetail(
                invoice_id=invoice.id,
                petroleum=5.0,
                municipal_tax=3.0,
            )
        ]
        result = await tax_repo.create_many(details)
        assert len(result) == 1
        assert result[0].petroleum == 5.0
