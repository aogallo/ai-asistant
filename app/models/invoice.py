import math
from enum import Enum

from pydantic import BaseModel, field_validator


class InvoiceType(str, Enum):
    EXPENSES = "expenses"
    INCOMES = "incomes"


class VendorSummary(BaseModel):
    nit: str
    name: str
    total_amount: float
    invoice_count: int


class AnomalyFlag(BaseModel):
    invoice_ref: str
    reason: str
    severity: str


class InvoiceSummary(BaseModel):
    total_invoices: int
    total_amount: float
    total_iva: float
    date_range: str
    top_vendors: list[VendorSummary]
    anomalies: list[AnomalyFlag]
    voided_count: int
    category_suggestions: list[str]


class InvoiceRowSchema(BaseModel):
    """Schema for invoice row."""

    date: str
    authorization_number: str
    dte_type: str
    serie: str
    dte_number: str
    exportation: bool
    company_nit: str
    company_name: str
    company_description: str
    company_code: int
    customer_nit: str
    customer_name: str
    certificator_nit: str
    certificator_name: str
    state: str
    money: str
    total: float
    iva: float
    is_voided: bool
    voided_date: str
    petroleum: float
    hotel: float
    tickets: float
    press_stamp: float
    firefighters: float
    municipal_tax: float
    alcoholic_tax: float
    tobacco_tax: float
    cement_tax: float
    no_alcoholic_tax: float
    port_tariff_tax: float

    @field_validator("is_voided", mode="before")
    @classmethod
    def transform_is_voided(cls, v: str) -> bool:
        """Transform is_voided to Boolean."""
        if v == "No":
            return False
        else:
            return True

    @field_validator("voided_date", mode="before")
    @classmethod
    def transform_voided_date(cls, v: str) -> str | None:
        """Transform voided_date to string."""
        if isinstance(v, float) and math.isnan(v):
            return ""
        return v

    @field_validator("customer_nit", mode="before")
    @classmethod
    def transform_customer_nit(cls, value: str):
        """Transform customer_nit to string."""
        return str(value)

    @field_validator("company_nit", mode="before")
    @classmethod
    def transform_company_nit(cls, value: str):
        """Transform company_nit to string."""
        return str(value)

    @field_validator("certificator_nit", mode="before")
    @classmethod
    def transform_certificator_nit(cls, value: str):
        """Transform certificator_nit to string."""
        return str(value)

    @field_validator("dte_number", mode="before")
    @classmethod
    def transform_dte_number(cls, value: str):
        """Transform dte_number to string."""
        return str(value)
