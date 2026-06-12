# Invoice RAG Documentation

This folder is the documentation entry point for the invoice assistant. The
current application supports SAT invoice upload, persistence, and optional AI
batch summaries. SaaS tenancy, authentication, invoice chat, vector search, and
RAG are **Proposed** product direction unless a later implementation adds them.

## Quick path

1. Start with [`PRD.md`](./PRD.md) for product scope and non-goals.
2. Use the technical docs below when reviewing or planning future work.
3. Check whether a section says **Current** or **Proposed** before treating it
   as implemented behavior.

## Documentation map

| Document | Status in this stacked change | Reader job |
|----------|-------------------------------|------------|
| [`PRD.md`](./PRD.md) | Current slice | Understand product direction, current scope, proposed scope, and non-goals. |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Current slice | Review current FastAPI layers and proposed SaaS/RAG evolution. |
| [`DOMAIN_MODEL.md`](./DOMAIN_MODEL.md) | Current slice | Review current invoice entities and proposed document/RAG concepts. |
| [`RAG_STRATEGY.md`](./RAG_STRATEGY.md) | Current slice | Plan proposed retrieval, chunking, embeddings, grounding, and citations. |
| [`API_DESIGN.md`](./API_DESIGN.md) | Current slice | Compare current endpoints with proposed invoice query/chat APIs. |
| [`IMPLEMENTATION_PLAN.md`](./IMPLEMENTATION_PLAN.md) | Current slice | Follow the reviewable implementation roadmap. |

## Current implementation summary

| Area | Current behavior | Source |
|------|------------------|--------|
| Health | `GET /health` returns `{"status": "ok"}`. | `app/api/routes.py` |
| Invoice upload | `POST /invoice/upload` accepts an uploaded SAT spreadsheet and `invoiceType`. | `app/api/invoices.py` |
| Invoice parsing | Excel files are parsed with pandas, SAT columns are renamed, and rows are validated with Pydantic. | `app/services/invoice_service.py`, `app/models/invoice.py` |
| Persistence | Upload batches, companies, invoices, and invoice tax details are persisted through SQLModel repositories. | `app/models/db_models.py`, `app/infrastructure/repositories.py` |
| AI summary | Uploads attempt an Anthropic-backed batch analysis; failures are logged and the upload result can still succeed without `ai_summary`. | `app/api/invoices.py`, `app/services/invoice_ai_service.py`, `tests/test_invoice_upload.py` |
| Generic AI | `/summarize`, `/chat/stream`, and `/agent/stream` are generic Anthropic flows, not invoice RAG flows. | `app/api/routes.py`, `app/api/chat.py`, `app/api/agent.py` |

## Proposed direction summary

The target product direction is a multi-user SaaS invoice assistant with secure
document ownership, tenant-aware retrieval, grounded answers, citations, and a
reviewable API surface for invoice Q&A. These capabilities are **Proposed** and
are not implemented by this documentation change.

## Non-goals for this documentation change

- No runtime upload, chat, authentication, tenancy, vector search, or RAG
  behavior changes.
- No database migrations, object storage, embeddings, or frontend changes.
- No new endpoints or placeholder implementation code.
