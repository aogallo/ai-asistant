# Invoice RAG Strategy

This strategy defines the proposed retrieval approach for invoice Q&A. The
current application uploads SAT invoice spreadsheets, persists structured invoice
records, and can request an AI batch summary. It does not implement embeddings,
vector search, tenant-scoped retrieval, citations, or invoice chat today.

## Quick path

1. Treat every RAG component in this document as **Proposed**.
2. Keep retrieval authorization before search, not after answer generation.
3. Use citations to make answers verifiable against invoice facts or source
   documents.

## Current baseline

| Area | Current behavior | Evidence |
|------|------------------|----------|
| Structured invoice facts | SAT spreadsheet rows are normalized, validated, and stored as upload batches, companies, invoices, and tax details. | `app/services/invoice_service.py`, `app/models/db_models.py` |
| AI analysis | The upload route optionally sends validated rows to Anthropic for a structured batch summary. | `app/api/invoices.py`, `app/services/invoice_ai_service.py` |
| Generic chat | `/chat/stream` streams a raw prompt through Anthropic and does not retrieve invoice records. | `app/api/chat.py`, `app/services/ll_stream_service.py` |
| Agent tools | The agent loop exists, but the registered tool surface is not invoice-specific. | `app/api/agent.py`, `app/agents/tools.py` |

## Proposed retrieval goals

| Goal | Proposed behavior |
|------|-------------------|
| Tenant-safe answers | Retrieve only records and chunks the authenticated user is allowed to access. |
| Grounded responses | Generate answers from retrieved invoice facts and document chunks, not from the prompt alone. |
| Verifiable citations | Return references to invoice IDs, upload batches, document chunks, or source locations used by the answer. |
| Structured + unstructured search | Combine relational invoice filters with semantic document retrieval when both exist. |
| Evaluation loop | Track whether retrieved evidence supports the final answer. |

## Proposed ingestion pipeline

```text
Authenticated upload
  -> persist current structured invoice facts
  -> store original source document metadata
  -> extract normalized text from source document
  -> chunk text using deterministic rules
  -> create embeddings for chunks and selected structured facts
  -> index embeddings with tenant and authorization metadata
```

### Proposed chunking rules

- Chunk by invoice boundaries when the source format supports it.
- Keep invoice identifiers, dates, vendor NIT/name, totals, IVA, and upload batch
  metadata with every chunk.
- Prefer smaller chunks that preserve one invoice or a coherent group of invoice
  lines over large pages with unrelated vendors.
- Store a stable `source_document_id`, chunk ordinal, and source locator for
  citations.

## Proposed retrieval flow

```text
Invoice question
  -> authenticate user
  -> resolve tenant and authorization scope
  -> classify intent: aggregate, lookup, anomaly, or narrative question
  -> query structured invoice facts when filters are explicit
  -> query vector index for semantic context when narrative evidence is needed
  -> rank and deduplicate evidence
  -> generate answer with citations
  -> return answer, citations, and retrieval metadata
```

## Proposed authorization constraints

Authorization is a retrieval precondition. A future implementation should:

- Filter every structured invoice query by tenant/user ownership.
- Filter every vector query by tenant and document access metadata.
- Never retrieve globally and then remove unauthorized results afterward.
- Include authorization tests before exposing invoice chat endpoints.

## Proposed citation contract

Each cited source should include enough metadata for review:

| Citation field | Proposed meaning |
|----------------|------------------|
| `source_type` | `invoice`, `upload_batch`, or `document_chunk`. |
| `source_id` | Stable identifier for the cited record. |
| `label` | Human-readable invoice number, vendor, date, or document name. |
| `excerpt` | Short evidence text used by the answer. |
| `confidence` | Retrieval or grounding confidence when available. |

## Proposed evaluation checks

- Retrieval returns at least one authorized citation for answerable invoice
  questions.
- Answers decline when no authorized evidence is found.
- Aggregate answers match structured invoice totals for the selected scope.
- Citation excerpts support the exact claim made in the answer.
- Cross-tenant data never appears in retrieved evidence or citations.

## Non-goals for this documentation change

- No embedding model, vector database, retriever, ingestion job, or citation API
  is implemented here.
- No claim is made that current generic chat can answer invoice questions from
  persisted invoice data.
