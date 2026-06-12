# Invoice RAG Product Requirements

This product baseline describes the invoice assistant as it exists today and the
SaaS-ready RAG direction it should evolve toward. **Current** means the behavior
is supported by inspected code or tests. **Proposed** means product direction
only; it is not implemented by this documentation change.

## Product outcome

Help users upload SAT invoice files, preserve the parsed invoice data, and move
toward trusted invoice Q&A with citations. The near-term product must stay
honest about the current system: it is an invoice upload and AI batch summary
service, not yet a multi-user RAG SaaS.

## Current scope

| Capability | Current behavior | Evidence |
|------------|------------------|----------|
| Invoice upload | Users can upload SAT Excel files to `POST /invoice/upload` with `invoiceType` set to `expenses` or `incomes`. | `app/api/invoices.py`, `app/models/invoice.py` |
| SAT row normalization | The service maps Spanish SAT column names to internal field names, validates rows, and rejects invalid or empty files. | `app/services/invoice_service.py`, `tests/test_invoice_service.py` |
| Persistence | The service stores upload batches, companies, invoices, and invoice tax detail rows. | `app/models/db_models.py`, `app/infrastructure/repositories.py`, `tests/test_repositories.py` |
| Batch totals | Upload results include row count, total amount, IVA total, status, upload timestamp, and optional AI summary. | `app/services/invoice_service.py`, `tests/test_invoice_upload.py` |
| AI batch analysis | After upload, the API attempts an Anthropic-backed structured invoice summary over validated rows. If AI analysis fails, upload can still return successfully with no summary. | `app/api/invoices.py`, `app/services/invoice_ai_service.py`, `tests/test_invoice_upload.py` |
| Generic AI endpoints | The app exposes generic summarization, streaming chat, and agent streaming endpoints. These flows do not retrieve invoice records today. | `app/api/routes.py`, `app/api/chat.py`, `app/api/agent.py` |

## Proposed SaaS and RAG scope

| Capability | Proposed behavior | Current status |
|------------|-------------------|----------------|
| Authentication | Users sign in and every invoice action is scoped to the authenticated user or tenant. | **Proposed** — no auth boundary is implemented. |
| Tenant isolation | Data access is filtered by tenant and enforced before retrieval, summarization, or chat. | **Proposed** — current invoice records are not tenant-scoped. |
| Invoice document storage | Original uploads are stored durably and linked to parsed records. | **Proposed** — no object storage contract is implemented. |
| Invoice RAG | Users ask questions over their invoice corpus and receive grounded answers with citations. | **Proposed** — no embeddings, vector index, retriever, or citation pipeline exists. |
| Conversation history | Invoice Q&A sessions preserve context while respecting tenant boundaries. | **Proposed** — current chat is generic prompt streaming. |
| Configurable AI providers | Tenants can choose the AI provider used for summaries, chat, and future RAG generation, including using their own paid provider subscription when supported. | **Proposed** — current AI integration is Anthropic-specific. |
| Admin operations | Operators can inspect ingestion health, retrieval quality, and failed jobs. | **Proposed** — no admin surface is implemented. |

## Target users

| User | Job to be done |
|------|----------------|
| Business owner | Upload SAT invoice files and understand spending or income patterns. |
| Accountant | Review invoice totals, voided invoices, vendor concentration, and anomalies. |
| SaaS tenant admin | **Proposed**: manage team access and data boundaries. |
| Future coding agent | Use this documentation to extend the system without overclaiming missing behavior. |

## Requirements

### Current requirements

- The system MUST continue accepting supported SAT invoice spreadsheets through
  `POST /invoice/upload`.
- The upload response MUST preserve existing totals and status fields.
- AI summary failure MUST NOT turn an otherwise valid upload into a failed
  upload.
- Generic AI endpoints MUST NOT be described as invoice RAG endpoints.

### Proposed requirements

- The future SaaS system SHOULD require authentication before invoice upload,
  invoice retrieval, or invoice chat.
- Tenant and user ownership checks MUST happen before any proposed RAG retrieval.
- Proposed answers SHOULD cite source invoices or uploaded documents.
- Proposed retrieval SHOULD separate parsed structured invoice facts from raw
  document text when both become available.
- Proposed AI features SHOULD be provider-agnostic so the system can support
  Anthropic, OpenAI, Google, or another compatible provider without changing
  invoice-domain behavior.
- Proposed tenant settings SHOULD allow a user or tenant to select a supported
  AI provider and, where appropriate, use their own provider subscription or API
  credentials.
- Proposed provider switching MUST preserve tenant isolation, auditability, and
  answer-grounding requirements.

## Non-goals

- This documentation change does not add authentication, tenancy, migrations,
  object storage, embeddings, vector search, invoice chat, RAG retrieval, or
  multi-provider AI configuration.
- This documentation change does not alter application code or runtime behavior.
- Current invoice upload must not be treated as production-grade SaaS isolation.

## Success criteria for the documentation baseline

- Readers can identify which capabilities are **Current** and which are
  **Proposed**.
- The canonical PRD source is this `docs/PRD.md` file; the old lowercase
  `docs/prd.md` file no longer remains as a competing PRD source.
- Future implementation work can be split into reviewable slices without
  confusing proposed RAG behavior with current upload behavior.
