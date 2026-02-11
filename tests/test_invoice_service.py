import pandas as pd
import pytest

from app.models.invoice import InvoiceType
from app.services.invoice_service import InvoiceService


def _make_df_row(**overrides) -> dict:
    base = {
        "date": "2024-01-15",
        "authorization_number": "AUTH-001",
        "dte_type": "FACT",
        "serie": "A",
        "dte_number": "12345",
        "exportation": False,
        "company_nit": "123456-7",
        "company_name": "Test Company",
        "company_description": "Test Desc",
        "company_code": 1,
        "customer_nit": "987654-3",
        "customer_name": "Customer",
        "certificator_nit": "111111-1",
        "certificator_name": "Cert Name",
        "state": "Vigente",
        "money": "GTQ",
        "total": 112.0,
        "iva": 12.0,
        "is_voided": "No",
        "voided_date": "",
        "petroleum": 0.0,
        "hotel": 0.0,
        "tickets": 0.0,
        "press_stamp": 0.0,
        "firefighters": 0.0,
        "municipal_tax": 0.0,
        "alcoholic_tax": 0.0,
        "tobacco_tax": 0.0,
        "cement_tax": 0.0,
        "no_alcoholic_tax": 0.0,
        "port_tariff_tax": 0.0,
    }
    base.update(overrides)
    return base


class TestValidateChunk:
    def test_validates_good_chunk(self, session):
        service = InvoiceService.__new__(InvoiceService)
        df = pd.DataFrame([_make_df_row()])
        result = service._validate_chunk(df, offset=0)
        assert len(result) == 1
        assert result[0].company_nit == "123456-7"

    def test_rejects_bad_chunk(self, session):
        service = InvoiceService.__new__(InvoiceService)
        df = pd.DataFrame([{"bad_column": "bad_value"}])
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            service._validate_chunk(df, offset=0)
        assert exc_info.value.status_code == 400


@pytest.mark.asyncio
class TestProcessValidatedRows:
    async def test_processes_rows_to_db(self, session):
        from app.infrastructure.repositories import (
            CompanyRepository,
            InvoiceRepository,
            TaxDetailRepository,
        )
        from app.models.invoice import InvoiceRowSchema

        service = InvoiceService.__new__(InvoiceService)
        service.session = session
        service.company_repo = CompanyRepository(session)
        service.invoice_repo = InvoiceRepository(session)
        service.tax_detail_repo = TaxDetailRepository(session)
        service.last_validated_rows = []

        rows = [
            InvoiceRowSchema.model_validate(_make_df_row()),
            InvoiceRowSchema.model_validate(
                _make_df_row(
                    company_nit="999-1",
                    company_name="Other Co",
                    total=200.0,
                    iva=24.0,
                )
            ),
        ]

        result = await service._process_validated_rows(
            rows=rows,
            filename="test.xlsx",
            invoice_type=InvoiceType.EXPENSES,
        )

        assert result.total_rows == 2
        assert result.total_amount == 312.0
        assert result.total_iva == 36.0
        assert result.status == "completed"
