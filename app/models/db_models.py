import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel


class BatchStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadBatch(SQLModel, table=True):
    __tablename__ = "upload_batch"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    filename: str
    invoice_type: str
    total_rows: int = 0
    total_amount: float = 0.0
    total_iva: float = 0.0
    status: str = BatchStatus.PROCESSING
    uploaded_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )

    invoices: list["Invoice"] = Relationship(
        back_populates="batch",
    )


class Company(SQLModel, table=True):
    __tablename__ = "company"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    nit: str = Field(unique=True, index=True)
    name: str
    description: str = ""

    invoices: list["Invoice"] = Relationship(
        back_populates="company",
    )


class Invoice(SQLModel, table=True):
    __tablename__ = "invoice"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    batch_id: uuid.UUID = Field(foreign_key="upload_batch.id")
    company_id: uuid.UUID = Field(foreign_key="company.id")
    authorization_number: str
    dte_type: str
    serie: str
    dte_number: str
    date: str
    customer_nit: str
    customer_name: str
    certificator_nit: str
    certificator_name: str
    state: str
    money: str
    total: float
    iva: float
    is_voided: bool = False
    voided_date: str = ""
    exportation: bool = False

    batch: Optional[UploadBatch] = Relationship(  # noqa: UP007
        back_populates="invoices",
    )
    company: Optional[Company] = Relationship(  # noqa: UP007
        back_populates="invoices",
    )
    tax_detail: Optional["InvoiceTaxDetail"] = Relationship(
        back_populates="invoice",
    )


class InvoiceTaxDetail(SQLModel, table=True):
    __tablename__ = "invoice_tax_detail"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    invoice_id: uuid.UUID = Field(foreign_key="invoice.id", unique=True)
    petroleum: float = 0.0
    hotel: float = 0.0
    tickets: float = 0.0
    press_stamp: float = 0.0
    firefighters: float = 0.0
    municipal_tax: float = 0.0
    alcoholic_tax: float = 0.0
    tobacco_tax: float = 0.0
    cement_tax: float = 0.0
    no_alcoholic_tax: float = 0.0
    port_tariff_tax: float = 0.0

    invoice: Optional[Invoice] = Relationship(  # noqa: UP007
        back_populates="tax_detail",
    )
