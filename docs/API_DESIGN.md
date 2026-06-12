# Invoice Assistant API Design

This document separates the current FastAPI endpoints from the proposed SaaS and
invoice RAG API direction. Current endpoints are implemented in the repository.
Proposed endpoints are planning contracts only and are not added by this
documentation change.

## Quick path

1. Use Current endpoints for behavior that exists today.
2. Treat authentication, tenant-scoped invoice retrieval, invoice chat, and RAG
   response contracts as **Proposed**.
3. Do not add placeholder routes until the related implementation slice exists.

## Current endpoints

| Endpoint | Current purpose | Request shape | Response shape | Evidence |
|----------|-----------------|---------------|----------------|----------|
| `GET /health` | Health check. | None. | `{"status": "ok"}` | `app/api/routes.py` |
| `POST /summarize` | Generic text summarization through Anthropic. | `SummarizeRequest` JSON body. | `SummarizeResponse` | `app/api/routes.py`, `app/schemas/ai.py` |
| `POST /chat/stream` | Generic prompt streaming. | `prompt` parameter. | `text/plain` stream. | `app/api/chat.py` |
| `POST /agent/stream` | Generic Claude agent loop streaming. | `prompt` parameter. | `text/plain` stream. | `app/api/agent.py` |
| `POST /invoice/upload` | SAT invoice spreadsheet upload and optional AI batch summary. | Multipart file plus `invoiceType` form field. | `UploadResult` | `app/api/invoices.py`, `app/schemas/response.py` |

## Current invoice upload contract

```text
POST /invoice/upload
Content-Type: multipart/form-data

file: UploadFile
invoiceType: expenses | incomes
```

`UploadResult` currently includes:

| Field | Current meaning |
|-------|-----------------|
| `batch_id` | Upload batch identifier. |
| `filename` | Uploaded filename or `unknown`. |
| `invoice_type` | Stored invoice type string. |
| `total_rows` | Number of validated rows. |
| `total_amount` | Sum of row totals. |
| `total_iva` | Sum of IVA values. |
| `status` | Batch processing status. |
| `uploaded_at` | Batch upload timestamp. |
| `ai_summary` | Optional structured AI summary; may be absent if analysis fails. |

## Current limitations

- No authentication or tenant context is accepted by current routes.
- No current endpoint lists, filters, or fetches persisted invoices after upload.
- No current endpoint retrieves invoice documents, chunks, embeddings, or
  citations.
- Current `/chat/stream` and `/agent/stream` do not query invoice repositories.

## Proposed API principles

| Principle | Proposed rule |
|-----------|---------------|
| Auth first | Every invoice read, upload, and chat route should require authenticated context. |
| Tenant scoped | Routes should derive tenant scope from membership, not from trusted client-provided filters alone. |
| Retrieval transparency | RAG responses should expose citations and retrieval metadata. |
| Backward-safe upload | Existing upload behavior should evolve without breaking current response fields. |
| Reviewable slices | Add routes only with tests and authorization checks in the same implementation slice. |

## Proposed endpoint direction

| Endpoint | Proposed purpose | Notes |
|----------|------------------|-------|
| `POST /auth/...` | Sign in and session/token management. | Exact auth mechanism is undecided. |
| `GET /tenants/{tenant_id}/invoices` | List authorized invoice facts with filters. | Requires tenant membership checks. |
| `GET /tenants/{tenant_id}/invoices/{invoice_id}` | Fetch one invoice and related tax detail. | Must verify invoice belongs to tenant. |
| `POST /tenants/{tenant_id}/invoice-chat` | Ask a grounded question over tenant invoices. | Returns answer plus citations. |
| `GET /tenants/{tenant_id}/uploads/{batch_id}` | Inspect upload status and totals. | Extends current upload batch concept. |
| `GET /tenants/{tenant_id}/documents/{document_id}` | Fetch source document metadata. | Proposed only after object storage exists. |

## Proposed invoice chat response shape

```json
{
  "answer": "The answer grounded in authorized invoice evidence.",
  "citations": [
    {
      "source_type": "invoice",
      "source_id": "uuid",
      "label": "Invoice ABC-123 from Vendor S.A.",
      "excerpt": "Total: 1200.00, IVA: 144.00",
      "confidence": 0.92
    }
  ],
  "retrieval": {
    "tenant_id": "uuid",
    "result_count": 3,
    "strategy": "structured_filter_plus_vector"
  }
}
```

This shape is **Proposed**. No current route returns it.

## Proposed error semantics

| Case | Proposed response |
|------|-------------------|
| Missing authentication | `401 Unauthorized`. |
| Tenant membership missing | `403 Forbidden`. |
| Invoice/document outside tenant | `404 Not Found` or `403 Forbidden`, chosen consistently. |
| No supporting evidence | Successful answer that explains no authorized evidence was found. |
| Ingestion not ready | `409 Conflict` or status response indicating the upload is still processing. |

## Non-goals for this documentation change

- No route, schema, dependency, auth middleware, repository method, or runtime
  behavior is added.
- No current endpoint is reclassified as invoice RAG.
