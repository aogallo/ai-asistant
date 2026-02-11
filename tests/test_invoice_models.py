import pytest
from pydantic import ValidationError

from app.models.invoice import InvoiceRowSchema


def _make_row(**overrides) -> dict:
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


class TestInvoiceRowSchema:
    def test_valid_row(self):
        row = InvoiceRowSchema.model_validate(_make_row())
        assert row.company_nit == "123456-7"
        assert row.is_voided is False

    def test_is_voided_transforms_no(self):
        row = InvoiceRowSchema.model_validate(_make_row(is_voided="No"))
        assert row.is_voided is False

    def test_is_voided_transforms_yes(self):
        row = InvoiceRowSchema.model_validate(_make_row(is_voided="Sí"))
        assert row.is_voided is True

    def test_voided_date_nan_becomes_empty(self):
        row = InvoiceRowSchema.model_validate(
            _make_row(voided_date=float("nan"))
        )
        assert row.voided_date == ""

    def test_nit_fields_coerced_to_string(self):
        row = InvoiceRowSchema.model_validate(
            _make_row(
                company_nit=123456,
                customer_nit=789012,
                certificator_nit=111111,
            )
        )
        assert row.company_nit == "123456"
        assert row.customer_nit == "789012"
        assert row.certificator_nit == "111111"

    def test_dte_number_coerced_to_string(self):
        row = InvoiceRowSchema.model_validate(_make_row(dte_number=99999))
        assert row.dte_number == "99999"

    def test_missing_required_field_fails(self):
        data = _make_row()
        del data["total"]
        with pytest.raises(ValidationError):
            InvoiceRowSchema.model_validate(data)
