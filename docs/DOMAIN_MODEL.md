# Invoice Assistant Domain Model

This document explains the domain concepts that exist today and the domain
concepts needed for the proposed SaaS/RAG direction. **Current** means the model
is implemented in code. **Proposed** means future design only.

## Quick path

1. Use Current invoice models when changing upload, validation, or persistence.
2. Use Proposed models only when planning future SaaS/RAG work.
3. Do not assume current data has user ownership, tenant isolation, source
   documents, chunks, embeddings, or citations.

## Current domain summary

| Concept | Current role | Evidence |
|---------|--------------|----------|
| `InvoiceType` | Accepts `expenses` and `incomes` as upload categories. | `app/models/invoice.py`, `app/api/invoices.py` |
| `InvoiceRowSchema` | Validates normalized SAT spreadsheet rows before persistence. | `app/models/invoice.py`, `app/services/invoice_service.py` |
| `UploadBatch` | Tracks one uploaded file, invoice type, totals, status, and upload timestamp. | `app/models/db_models.py` |
| `Company` | Represents the invoice issuer/vendor keyed by unique NIT. | `app/models/db_models.py`, `app/infrastructure/repositories.py` |
| `Invoice` | Stores validated invoice facts linked to an upload batch and company. | `app/models/db_models.py` |
| `InvoiceTaxDetail` | Stores per-invoice tax detail amounts. | `app/models/db_models.py` |
| `InvoiceSummary` | Pydantic response model for Anthropic batch analysis. | `app/models/invoice.py`, `app/services/invoice_ai_service.py` |
| `UploadResult` | API response for invoice upload totals and optional AI summary. | `app/schemas/response.py` |

## Current entity relationships

```text
UploadBatch 1 ── * Invoice * ── 1 Company
Invoice    1 ── 0..1 InvoiceTaxDetail
```

| Relationship | Current behavior | Evidence |
|--------------|------------------|----------|
| Batch to invoices | Each invoice stores `batch_id`; `UploadBatch.invoices` is a relationship. | `app/models/db_models.py` |
| Company to invoices | Each invoice stores `company_id`; companies are reused by unique NIT. | `app/models/db_models.py`, `app/infrastructure/repositories.py` |
| Invoice to tax detail | Each tax detail stores a unique `invoice_id`. | `app/models/db_models.py` |

## Current validation model

`InvoiceRowSchema` is the boundary between a normalized spreadsheet row and the
persistence workflow.

| Field group | Current examples | Notes |
|-------------|------------------|-------|
| Identity | `authorization_number`, `serie`, `dte_number`, `dte_type` | Stored on `Invoice`. |
| Dates and status | `date`, `state`, `is_voided`, `voided_date` | `is_voided` converts the SAT value `No` to `False`; other values become `True`. |
| Issuer/company | `company_nit`, `company_name`, `company_description`, `company_code` | `company_nit` is converted to string and used for company reuse. |
| Customer/certifier | `customer_nit`, `customer_name`, `certificator_nit`, `certificator_name` | NIT-like fields are converted to strings. |
| Amounts | `total`, `iva`, and specific tax fields | Totals feed `UploadResult` and `UploadBatch`. |

## Current upload aggregate

During upload processing, the service builds an aggregate around one
`UploadBatch`:

1. Create the batch with `processing` status.
2. Reuse or create `Company` rows for validated issuer NITs.
3. Create `Invoice` rows for each validated invoice.
4. Create `InvoiceTaxDetail` rows for each invoice.
5. Update batch totals and mark the batch `completed`.
6. Commit the transaction and return `UploadResult`.

The tests cover row validation, repository creation/reuse, tax detail creation,
and upload behavior with AI summary failure.

## Current AI summary model

`InvoiceSummary` is a structured AI output model, not a persisted RAG document.

| Field | Current meaning |
|-------|-----------------|
| `total_invoices`, `total_amount`, `total_iva` | Aggregate values requested from Anthropic. |
| `date_range` | Summary date range. |
| `top_vendors` | List of `VendorSummary` items. |
| `anomalies` | List of `AnomalyFlag` items. |
| `voided_count` | Count of voided invoices. |
| `category_suggestions` | Suggested categories derived by the AI prompt. |

The prompt sends a reduced list of invoice fields and caps displayed invoice data
to the first 100 records. This is batch analysis, not retrieval over a document
corpus.

## Proposed SaaS and RAG domain concepts

The concepts below are required for the target product direction but are not in
the current codebase.

| Proposed concept | Proposed responsibility | Current status |
|------------------|-------------------------|----------------|
| User | Owns sessions and actions. | **Proposed** — no user model exists. |
| Tenant or organization | Groups users and scopes data access. | **Proposed** — no tenant key exists on invoice tables. |
| Membership/role | Defines who can upload, query, administer, or audit tenant data. | **Proposed** — no authorization model exists. |
| Source document | Represents the original uploaded file and storage metadata. | **Proposed** — current upload stores filename and parsed records, not durable object metadata. |
| Document chunk | Searchable text segment linked to a source document and tenant. | **Proposed** — no chunk table or chunking service exists. |
| Embedding | Vector representation of a chunk or invoice fact. | **Proposed** — no embedding service or vector index exists. |
| Retrieval result | Authorized chunk/fact selected for answer generation. | **Proposed** — no retriever exists. |
| Citation | Source reference returned with an answer. | **Proposed** — no citation contract exists. |
| Invoice chat session | Conversation over a tenant-scoped invoice corpus. | **Proposed** — current chat is generic prompt streaming. |

## Proposed relationship sketch

```text
Tenant 1 ── * UserMembership * ── 1 User
Tenant 1 ── * UploadBatch 1 ── * Invoice
Tenant 1 ── * SourceDocument 1 ── * DocumentChunk 1 ── * Embedding
InvoiceChatSession 1 ── * Message
Message * ── * Citation -> Invoice or DocumentChunk
```

This sketch is a planning aid only. A future implementation must choose exact
table names, indexes, migrations, authorization checks, and deletion semantics.

## Modeling rules for future work

- Tenant/user ownership must be enforced before proposed retrieval or chat.
- Proposed document and chunk records should link back to upload batches when
  they originate from invoice uploads.
- Proposed citations should identify enough source metadata for a user to verify
  an answer.
- Proposed RAG models must not replace current structured invoice facts; they
  should complement them.

## Non-goals for this documentation slice

- No new SQLModel tables or migrations.
- No auth, tenant, document, chunk, embedding, retrieval, citation, or chat
  session implementation.
- No change to current invoice upload validation or persistence behavior.

## Current claim cross-check

The Current model claims in this document were checked against
`app/models/invoice.py`, `app/models/db_models.py`, `app/schemas/response.py`,
`app/services/invoice_service.py`, `app/services/invoice_ai_service.py`,
`app/infrastructure/repositories.py`, and the invoice/repository tests. Missing
SaaS and RAG concepts remain labeled **Proposed**.
