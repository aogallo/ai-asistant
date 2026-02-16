from fastapi.testclient import TestClient

from app.main import app
from app.services.accounting_classifier_service import (
    AccountingClassifierService,
)

client = TestClient(app)


def test_accounting_classify_endpoint():
    AccountingClassifierService._feedback_rules = []
    payload = {
        "transactions": [
            {
                "transaction_id": "tx-1",
                "description": "Subscription sale - annual plan",
                "vendor": "Acme Corp",
                "amount": 1200.0,
            }
        ],
        "chart_of_accounts": [
            {
                "code": "4000",
                "name": "Product Revenue",
                "category": "revenue",
                "keywords": ["subscription", "sale", "plan"],
                "vendors": [],
                "is_active": True,
            },
            {
                "code": "6100",
                "name": "Software Expense",
                "category": "expense",
                "keywords": ["hosting", "cloud"],
                "vendors": ["aws"],
                "is_active": True,
            },
        ],
        "mapping_rules": [],
        "target_system": "quickbooks",
    }

    response = client.post("/accounting/classify", json=payload)
    assert response.status_code == 200
    body = response.json()

    assert body["results"][0]["transaction_type"] == "revenue"
    assert body["results"][0]["account_code"] == "4000"
    assert body["results"][0]["integration_payload"]["system"] == ("quickbooks")
    assert body["results"][0]["explanation"]


def test_accounting_feedback_endpoint():
    AccountingClassifierService._feedback_rules = []
    response = client.post(
        "/accounting/feedback",
        json={"pattern": "stripe", "account_code": "4000"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["total_rules"] == 1
