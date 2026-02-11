from io import BytesIO
from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest


def _create_test_excel() -> bytes:
    """Create a minimal SAT-format Excel file."""
    data = {
        "Fecha de emisión": ["2024-01-15"],
        "Número de Autorización": ["AUTH-001"],
        "Tipo de DTE (nombre)": ["FACT"],
        "Serie": ["A"],
        "Número del DTE": ["12345"],
        "Clasificación emisor": ["Normal"],
        "Exportación": [False],
        "NIT del emisor": ["123456-7"],
        "Nombre completo del emisor": ["Test Co"],
        "Código de establecimiento": [1],
        "Nombre del establecimiento": ["Test Desc"],
        "ID del receptor": ["987654-3"],
        "Nombre completo del receptor": ["Customer"],
        "NIT del Certificador": ["111111-1"],
        "Nombre completo del Certificador": ["Cert Name"],
        "Estado": ["Vigente"],
        "Moneda": ["GTQ"],
        "Gran Total (Moneda Original)": [112.0],
        "IVA (monto de este impuesto)": [12.0],
        "Marca de anulado": ["No"],
        "Fecha de anulación": [""],
        "Petróleo (monto de este impuesto)": [0.0],
        "Turismo Hospedaje (monto de este impuesto)": [0.0],
        "Turismo Pasajes (monto de este impuesto)": [0.0],
        "Timbre de Prensa (monto de este impuesto)": [0.0],
        "Bomberos (monto de este impuesto)": [0.0],
        "Tasa Municipal (monto de este impuesto)": [0.0],
        "Bebidas alcohólicas (monto de este impuesto)": [0.0],
        "Tabaco (monto de este impuesto)": [0.0],
        "Cemento (monto de este impuesto)": [0.0],
        "Bebidas no Alcohólicas (monto de este impuesto)": [0.0],
        "Tarifa Portuaria (monto de este impuesto)": [0.0],
    }
    df = pd.DataFrame(data)
    buf = BytesIO()
    df.to_excel(buf, index=False)
    return buf.getvalue()


@pytest.mark.asyncio
class TestInvoiceUploadEndpoint:
    @patch(
        "app.services.invoice_ai_service.InvoiceAIService.analyze_batch",
        new_callable=AsyncMock,
        side_effect=Exception("AI unavailable"),
    )
    async def test_upload_happy_path(self, mock_ai, client):
        excel_bytes = _create_test_excel()

        response = await client.post(
            "/invoice/upload",
            files={
                "file": (
                    "test.xlsx",
                    excel_bytes,
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet",
                )
            },
            data={"invoiceType": "expenses"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["total_rows"] == 1
        assert body["total_amount"] == 112.0
        assert body["status"] == "completed"
        assert body["ai_summary"] is None

    async def test_upload_bad_format(self, client):
        response = await client.post(
            "/invoice/upload",
            files={
                "file": (
                    "bad.xlsx",
                    b"not an excel file",
                    "application/octet-stream",
                )
            },
            data={"invoiceType": "expenses"},
        )
        assert response.status_code == 500
