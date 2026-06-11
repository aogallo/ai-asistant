## Exploration: Invoice RAG Documentation

### Current State
- The application is a Python 3.12 FastAPI service with a layered structure: API routers in `app/api/`, business services in `app/services/`, infrastructure in `app/infrastructure/`, Pydantic/SQLModel models in `app/models/`, and shared config/logging in `app/core/`.
- Current invoice upload functionality exists at `POST /invoice/upload` in `app/api/invoices.py`. It accepts an uploaded Excel file plus `invoiceType`, reads the file in `InvoiceService`, validates SAT-style invoice rows with `InvoiceRowSchema`, persists batches, companies, invoices, and tax details, then optionally adds an AI-generated batch summary.
- Current invoice persistence exists through SQLModel tables in `app/models/db_models.py`: `UploadBatch`, `Company`, `Invoice`, and `InvoiceTaxDetail`. Repository methods in `app/infrastructure/repositories.py` support basic create/update flows, but not invoice search, filtering, user ownership, document chunks, embeddings, or chat retrieval.
- Current AI functionality exists in three separate forms: `/summarize` via `LLMService`, `/chat/stream` via `LLMStreamService`, and `/agent/stream` via `ClaudeAgentLoop`. These chat/agent endpoints currently use only the raw prompt and do not retrieve invoice data from the database.
- Current invoice AI analysis exists in `InvoiceAIService.analyze_batch`, which sends up to the first 100 validated invoice rows to Anthropic through Instructor and returns a structured `InvoiceSummary`. This is batch summarization, not RAG.
- Current database setup uses async SQLAlchemy/SQLModel in `app/infrastructure/database.py`, initializes schema with `SQLModel.metadata.create_all`, and depends on `DATABASE_URL`. There is no migration layer visible in the inspected code.
- Current tests cover health, invoice upload, invoice row validation, invoice service processing, and repositories. Tests use an in-memory SQLite async engine and dependency overrides.
- Existing documentation is minimal: root `README.md` is a setup stub and `docs/prd.md` contains only headings. The requested documentation set is therefore mostly new or replacement documentation.
- No React frontend, vector database, embeddings, RAG retrieval pipeline, file object storage, user/account model, authentication, invoice query API, or chat-over-invoices endpoint was found in the inspected code. These must be documented as **Proposed**, not current implementation.

### Affected Areas
- `docs/README.md` — Proposed top-level documentation entry point for future AI coding agents and contributors.
- `docs/PRD.md` — Proposed product requirements document; current `docs/prd.md` exists but is lowercase and only a stub, so naming/cleanup should be decided in the proposal.
- `docs/ARCHITECTURE.md` — Proposed architecture documentation covering current FastAPI layers and proposed invoice-chat/RAG evolution.
- `docs/DOMAIN_MODEL.md` — Proposed domain model documentation for current persisted entities and proposed RAG/document concepts.
- `docs/RAG_STRATEGY.md` — Proposed strategy for invoice metadata retrieval, document chunking, embeddings, vector search, and grounded answers.
- `docs/API_DESIGN.md` — Proposed API contract documentation for existing endpoints plus proposed invoice listing/query/chat/RAG endpoints.
- `docs/IMPLEMENTATION_PLAN.md` — Proposed phased implementation plan designed for future AI coding agents and reviewable work units.
- `README.md` — Existing project README may need to point to `docs/README.md` later, but should not be changed during exploration.
- `app/api/invoices.py` — Current invoice upload endpoint that docs must describe accurately.
- `app/services/invoice_service.py` — Current Excel parsing, row validation, chunk processing, persistence, and upload result assembly.
- `app/services/invoice_ai_service.py` — Current batch analysis behavior that should be distinguished from future RAG.
- `app/models/invoice.py` — Current invoice row and AI summary DTOs.
- `app/models/db_models.py` — Current persisted invoice schema and relationship source of truth.
- `app/infrastructure/repositories.py` — Current persistence capabilities and missing query/retrieval methods.
- `app/api/chat.py`, `app/api/agent.py`, `app/agents/` — Current generic chat/agent streaming functionality; not invoice-aware today.
- `tests/` — Current behavior evidence for docs; no docs implementation tests are required unless future phases choose markdown/content checks.

### Approaches
1. **Current-vs-Proposed documentation baseline** — Create practical docs that separate implemented behavior from proposed architecture using explicit labels.
   - Pros: Prevents invented implementation details; gives future agents a trustworthy baseline; directly supports clean RAG planning.
   - Cons: Requires careful wording to avoid overpromising future React/vector database/database migration pieces.
   - Effort: Medium

2. **Aspirational product-first documentation** — Write the full future product story first, with current implementation details only as background.
   - Pros: Strong product narrative; useful for stakeholder alignment.
   - Cons: Higher risk of confusing proposed capabilities with existing code; less useful for AI coding agents that need exact implementation boundaries.
   - Effort: Medium

3. **Architecture-only documentation slice** — Start with `ARCHITECTURE.md`, `DOMAIN_MODEL.md`, and `RAG_STRATEGY.md`, leaving PRD/API/implementation docs for later.
   - Pros: Smaller review surface; focuses on technical foundation.
   - Cons: Does not satisfy the full requested documentation set; weaker product/API alignment.
   - Effort: Low

### Recommendation
Use the **Current-vs-Proposed documentation baseline** approach for the later docs-only implementation. Each document should lead with what exists today, mark missing/future capabilities as **Proposed**, and avoid presenting PostgreSQL, React, vector database, embeddings, RAG, authentication, or invoice chat retrieval as implemented unless future code adds them first.

For cognitive load, structure the eventual docs as a connected set: `docs/README.md` as the navigation hub, `PRD.md` for product intent, `ARCHITECTURE.md` for system shape, `DOMAIN_MODEL.md` for entities, `RAG_STRATEGY.md` for retrieval design, `API_DESIGN.md` for current/proposed API contracts, and `IMPLEMENTATION_PLAN.md` for phased execution.

### Risks
- Existing `docs/prd.md` uses lowercase while the requested artifact is `docs/PRD.md`; case-sensitive and case-insensitive filesystems may behave differently, so the proposal should explicitly handle rename/update strategy.
- Current database schema is created directly through SQLModel metadata with no visible migration system; docs should not imply migration maturity.
- Current chat and agent endpoints are generic and not invoice-aware; calling them invoice chat or RAG without a **Proposed** label would misrepresent the implementation.
- `InvoiceAIService` analyzes only up to the first 100 validated rows in prompt context; this is not reliable retrieval and should be documented as current batch summarization only.
- Future RAG design needs decisions that are not in code yet: user/account boundaries, file storage retention, embedding model, vector store, retrieval filters, authorization, citation format, and metadata indexing.
- Documentation-only implementation may exceed the 400-line review budget if all seven requested docs are detailed; future task planning should consider review slices or concise first-pass docs.

### Ready for Proposal
Yes. The proposal should define a docs-only change that creates or updates the requested documentation artifacts, explicitly distinguishes **Current** from **Proposed**, addresses the `docs/prd.md` vs `docs/PRD.md` naming issue, and keeps the first documentation pass concise enough for review.
