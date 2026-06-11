# Invoice RAG Implementation Plan

This plan turns the proposed SaaS/RAG direction into reviewable future work. The
current change is documentation-only. It does not implement authentication,
tenancy, object storage, vector search, invoice chat, or new API behavior.

## Quick path

1. Protect the current upload workflow before adding SaaS boundaries.
2. Add ownership and authorization before retrieval or chat.
3. Build RAG in small slices: source documents, chunks, embeddings, retrieval,
   grounded answers, then evaluation.

## Current starting point

| Capability | Current state |
|------------|---------------|
| Invoice upload | Implemented at `POST /invoice/upload`. |
| Structured persistence | Implemented for upload batches, companies, invoices, and invoice tax details. |
| AI batch summary | Implemented as optional Anthropic analysis after upload. |
| Generic chat/agent | Implemented, but not connected to invoice data. |
| SaaS auth/tenancy | **Proposed** — not implemented. |
| RAG retrieval/citations | **Proposed** — not implemented. |

## Proposed phased roadmap

### Phase 1: Stabilize current invoice boundaries

Outcome: current upload behavior remains safe to extend.

- Add regression coverage around successful upload, invalid file handling, AI
  summary failure, and batch persistence if gaps are found.
- Document and preserve the current `UploadResult` response fields.
- Avoid changing invoice table semantics before tenant ownership is designed.

### Phase 2: Add SaaS identity and ownership

Outcome: invoice data can be scoped to authenticated users or tenants.

- Choose an authentication mechanism and token/session contract.
- Add user, tenant/organization, and membership concepts.
- Add tenant ownership to upload batches and invoice records through migrations.
- Enforce authorization at API and repository/service boundaries.

### Phase 3: Expose tenant-scoped invoice reads

Outcome: users can safely inspect their invoice corpus without chat.

- Add invoice list/detail endpoints scoped by tenant membership.
- Support basic filters such as date, vendor NIT/name, invoice type, status, and
  amount range.
- Keep aggregate calculations backed by structured invoice facts.

### Phase 4: Add source document storage

Outcome: uploaded files can be cited and reprocessed.

- Define source document metadata linked to upload batches and tenant ownership.
- Store original files in the selected object storage provider.
- Track ingestion status and failure reasons separately from upload success.

### Phase 5: Build ingestion for chunks and embeddings

Outcome: invoice documents become retrievable evidence.

- Extract text from source documents where available.
- Chunk text with invoice-aware metadata.
- Generate embeddings for chunks and selected structured facts.
- Store vectors with tenant and authorization metadata.

### Phase 6: Add grounded invoice chat

Outcome: users can ask questions over authorized invoice evidence.

- Add an invoice chat endpoint with tenant-scoped retrieval.
- Combine structured filters and vector retrieval.
- Generate answers only from authorized evidence.
- Return citations and retrieval metadata with each answer.

### Phase 7: Evaluate and operate RAG quality

Outcome: retrieval behavior can be reviewed and improved safely.

- Add test fixtures for answerable, unanswerable, and cross-tenant questions.
- Track citation coverage, retrieval hit rate, and unsupported-answer declines.
- Add operational visibility for ingestion and retrieval failures.

## Reviewable work units

| Work unit | Review boundary | Suggested verification |
|-----------|-----------------|------------------------|
| Auth foundation | Auth dependency and user identity model only. | Unit/integration tests for authenticated and unauthenticated requests. |
| Tenant ownership | Migrations and tenant-scoped repositories. | Repository tests proving cross-tenant exclusion. |
| Invoice reads | Read-only invoice APIs. | API tests for filters and authorization. |
| Source documents | Metadata and object storage adapter. | Service tests with storage mocked at the boundary. |
| Chunking | Deterministic chunk creation. | Pure unit tests for chunk boundaries and metadata. |
| Embeddings/index | Embedding service and vector persistence. | Adapter tests and integration tests against chosen vector store. |
| Invoice chat | Retrieval, answer generation, and citations. | Integration tests for grounded answers and no-evidence cases. |

## Proposed sequencing rules

- Do not implement invoice chat before authorization and tenant ownership exist.
- Do not run vector retrieval across unfiltered global data.
- Keep tests with each behavior slice under Strict TDD.
- Keep each PR reviewable; split large migrations, API changes, and RAG
  orchestration into separate stacked work units.
- Preserve existing upload response compatibility unless a future PR explicitly
  changes the API contract.

## Open decisions for future implementation

| Decision | Why it matters |
|----------|----------------|
| Authentication provider | Determines dependencies, local testing, and token validation. |
| Tenant model | Controls ownership, collaboration, and authorization semantics. |
| Object storage provider | Determines source document durability and citation links. |
| Vector store | Determines retrieval filters, migrations, and local test strategy. |
| Embedding model | Affects cost, latency, language quality, and reindexing strategy. |
| Citation UX/API | Determines how users verify answers and report issues. |

## Documentation-only completion criteria

- The seven requested docs exist under `docs/`.
- Current behavior is supported by inspected source or tests.
- Proposed SaaS/RAG behavior is labeled **Proposed**.
- No application code or runtime behavior changes are introduced.
