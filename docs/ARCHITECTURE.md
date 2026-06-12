# Invoice Assistant Architecture

This document describes the architecture that exists today and the SaaS/RAG
architecture the product can evolve toward. **Current** means implemented in the
repository. **Proposed** means future direction only.

## Quick path

1. Use the Current architecture map to understand the running FastAPI app.
2. Use the Current flows to verify invoice upload, AI summary, and generic chat
   behavior.
3. Treat every SaaS, tenant, vector, retrieval, or invoice chat reference as
   **Proposed** unless this document marks it Current with source evidence.

## Current architecture map

The application uses a layered FastAPI structure with dependency injection at
the API boundary.

```text
app/main.py
  -> app/api/                  FastAPI routers
  -> app/services/             business workflows and AI orchestration
  -> app/infrastructure/       database, repositories, Anthropic client factory
  -> app/models/               SQLModel tables and Pydantic domain models
  -> app/schemas/              request/response DTOs
  -> app/utils/                Anthropic stream parsing helpers
```

| Layer | Current responsibility | Evidence |
|-------|------------------------|----------|
| API | Mounts `/health`, `/summarize`, `/chat/stream`, `/agent/stream`, and `/invoice/upload`. | `app/main.py`, `app/api/routes.py`, `app/api/chat.py`, `app/api/agent.py`, `app/api/invoices.py` |
| Services | Parse SAT files, validate invoice rows, persist batches, call Anthropic for summaries, stream generic chat, and run the agent loop. | `app/services/invoice_service.py`, `app/services/invoice_ai_service.py`, `app/services/llm_service.py`, `app/services/ll_stream_service.py`, `app/agents/agent_loop.py` |
| Infrastructure | Creates the async database engine/session, repository objects, and Anthropic client. | `app/infrastructure/database.py`, `app/infrastructure/repositories.py`, `app/infrastructure/anthropic_client.py` |
| Models | Defines upload batches, companies, invoices, invoice tax details, invoice row validation, and AI summary shapes. | `app/models/db_models.py`, `app/models/invoice.py` |

## Current invoice upload flow

```text
POST /invoice/upload
  -> app/api/invoices.py reads UploadFile and invoiceType
  -> InvoiceService.process_sat_file reads Excel bytes with pandas
  -> SAT columns are renamed to internal field names
  -> each row is validated as InvoiceRowSchema
  -> UploadBatch, Company, Invoice, and InvoiceTaxDetail rows are persisted
  -> batch totals and status are committed
  -> InvoiceAIService attempts a structured Anthropic summary
  -> UploadResult returns totals, status, timestamp, and optional ai_summary
```

| Step | Current behavior | Evidence |
|------|------------------|----------|
| Upload input | The route accepts `file: UploadFile` and `invoiceType: InvoiceType` from form data. | `app/api/invoices.py` |
| File parsing | `.xls` uses `xlrd`; other Excel files use `openpyxl`; pandas reads the uploaded bytes. | `app/services/invoice_service.py` |
| Column normalization | Spanish SAT column names are renamed by `COLUMN_RENAME_MAP`. | `app/services/invoice_service.py` |
| Validation | Rows are validated with `InvoiceRowSchema`; invalid rows raise HTTP 400. | `app/services/invoice_service.py`, `tests/test_invoice_service.py` |
| Persistence | The service creates or reuses companies, creates invoices and tax details, updates the upload batch, then commits. | `app/services/invoice_service.py`, `app/infrastructure/repositories.py`, `tests/test_repositories.py` |
| Response | `UploadResult` includes `batch_id`, filename, invoice type, totals, status, upload timestamp, and optional `ai_summary`. | `app/schemas/response.py` |
| AI failure handling | If AI analysis fails after upload processing, the route logs a warning and returns the upload result without a summary. | `app/api/invoices.py`, `tests/test_invoice_upload.py` |

## Current generic AI flows

These endpoints are implemented, but they are not invoice RAG endpoints.

| Endpoint | Current flow | Invoice data access? | Evidence |
|----------|--------------|----------------------|----------|
| `POST /summarize` | Builds a summary prompt and calls Anthropic messages API through `LLMService`. | No. | `app/api/routes.py`, `app/services/llm_service.py` |
| `POST /chat/stream` | Streams a single prompt through Anthropic and yields text chunks. | No. | `app/api/chat.py`, `app/services/ll_stream_service.py` |
| `POST /agent/stream` | Runs a Claude tool-use loop and dispatches tools through the registry. | No invoice-specific tools are present. | `app/api/agent.py`, `app/agents/agent_loop.py`, `app/agents/tools.py` |

## Current persistence and startup

- `app/main.py` initializes the database during FastAPI lifespan startup.
- `app/infrastructure/database.py` builds an async SQLAlchemy engine from
  `settings.database_url` and exposes `get_session()` for dependency injection.
- SQLModel metadata is created at startup through `init_db()`.
- Repository methods use the injected `AsyncSession`; commit control remains in
  `InvoiceService._process_validated_rows()` for the invoice upload workflow.

## Proposed SaaS/RAG evolution

The target architecture is a multi-user SaaS invoice assistant with grounded
invoice Q&A. None of the components below are implemented by this documentation
change.

| Proposed area | Proposed responsibility | Current status |
|---------------|-------------------------|----------------|
| Authentication | Identify users before upload, retrieval, or chat. | **Proposed** — no auth middleware, user model, or session contract exists. |
| Tenant isolation | Scope invoices, uploads, documents, chunks, and chat sessions by tenant/user. | **Proposed** — current persisted invoice records have no tenant key. |
| Object storage | Store original uploaded files outside the relational invoice tables. | **Proposed** — no object storage client or document table exists. |
| Ingestion jobs | Turn uploaded files into durable documents, chunks, embeddings, and searchable metadata. | **Proposed** — current upload parses structured rows only. |
| Vector retrieval | Search tenant-authorized chunks and structured invoice facts before answering. | **Proposed** — no embedding model, vector index, or retriever exists. |
| Grounded invoice chat | Answer invoice questions with citations and retrieval metadata. | **Proposed** — current chat streams from a raw prompt only. |

## Proposed target flow

```text
Authenticated user uploads invoice file
  -> tenant ownership is checked
  -> current structured SAT parsing persists invoice facts
  -> proposed document storage saves the original upload
  -> proposed ingestion jobs create chunks and embeddings
  -> proposed invoice chat retrieves authorized facts/chunks
  -> proposed answer generation cites source invoices/documents
```

## Non-goals for this documentation slice

- No application code, endpoint, database, migration, or runtime behavior change.
- No placeholder auth, tenant, document, embedding, vector, or RAG implementation.
- No claim that current generic chat can retrieve invoice records.

## Current claim cross-check

The Current claims in this document were checked against `app/api/`,
`app/services/`, `app/infrastructure/`, `app/models/`, `app/schemas/`, and the
invoice/repository tests. Future SaaS and RAG behavior remains labeled
**Proposed** because those components were not found in the inspected code.
