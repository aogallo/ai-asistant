# Design: Invoice RAG Product and Technical Documentation

## Technical Approach

Create a documentation-only baseline under `docs/` that is grounded in the
inspected FastAPI code and optimized for future reviewers and AI coding agents.
The docs will describe Current behavior first, then mark SaaS tenancy,
authentication, invoice chat, embeddings, vector search, object storage, and RAG
retrieval as **Proposed**. No application files, database schema, endpoints, or
runtime behavior will be changed by this change.

## Architecture Decisions

| Decision | Choice | Alternatives considered | Rationale |
|----------|--------|--------------------------|-----------|
| Current vs Proposed labeling | Each substantive section uses explicit **Current** and **Proposed** labels. | Product-only narrative; architecture-only slice. | Prevents overclaiming missing SaaS/RAG behavior while still preserving product direction. |
| Canonical PRD path | Replace/rename lowercase `docs/prd.md` with canonical `docs/PRD.md`; do not keep both. | Keep both files; leave lowercase stub. | Avoids ambiguity and case-sensitivity problems across filesystems. |
| Documentation structure | Use `docs/README.md` as a navigation hub and keep each doc focused on one reader job. | One large design document. | Reduces cognitive load and satisfies the requested documentation set. |
| Runtime boundary | Application code remains reference-only. | Add placeholder APIs/models for proposed RAG. | The spec requires documentation only; placeholders would create misleading implementation claims. |

## Data Flow

Current invoice upload flow to document:

```text
POST /invoice/upload
  -> app/api/invoices.py reads UploadFile + invoiceType
  -> InvoiceService parses Excel with pandas, renames SAT columns, validates rows
  -> repositories persist UploadBatch, Company, Invoice, InvoiceTaxDetail
  -> InvoiceAIService optionally summarizes validated rows through Anthropic
  -> UploadResult returns batch totals and optional ai_summary
```

Current generic AI flows to document separately:

```text
/summarize -> LLMService -> Anthropic messages API
/chat/stream -> LLMStreamService -> streaming Anthropic response
/agent/stream -> ClaudeAgentLoop -> tool registry loop
```

These flows do not retrieve invoice data today, so invoice chat/RAG data flow is
Proposed only.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `docs/README.md` | Create | Navigation hub for product, architecture, domain, RAG, API, and plan docs. |
| `docs/PRD.md` | Create/Rename | Canonical product document replacing `docs/prd.md`; covers SaaS-ready direction and Current vs Proposed scope. |
| `docs/prd.md` | Delete/Rename | Remove lowercase stub to avoid conflicting PRD sources. |
| `docs/ARCHITECTURE.md` | Create | Current layered FastAPI architecture plus Proposed SaaS/RAG evolution. |
| `docs/DOMAIN_MODEL.md` | Create | Current SQLModel/Pydantic invoice entities plus Proposed user/document/chunk concepts. |
| `docs/RAG_STRATEGY.md` | Create | Proposed retrieval, chunking, embedding, grounding, citations, and authorization constraints. |
| `docs/API_DESIGN.md` | Create | Current endpoints and Proposed invoice query/chat API direction. |
| `docs/IMPLEMENTATION_PLAN.md` | Create | Phased, reviewable implementation path for future work. |
| `README.md` | Optional Modify | Add a short pointer to `docs/README.md` only if task budget allows. |

## Interfaces / Contracts

No runtime interfaces are added or changed. Documentation contracts:

- Any Current claim about upload, persistence, AI summaries, streaming, or tests
  MUST cite or clearly map to inspected files such as `app/api/invoices.py`,
  `app/services/invoice_service.py`, `app/services/invoice_ai_service.py`,
  `app/models/db_models.py`, and `tests/`.
- Any mention of auth, users, tenant isolation, vector search, embeddings,
  object storage, migrations, invoice chat, or RAG retrieval MUST be labeled
  **Proposed** unless implemented before these docs are written.
- `docs/PRD.md` is the only PRD source after this change.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Static review | Required docs exist and `docs/prd.md` conflict is gone. | Inspect `docs/` and git diff. |
| Content review | Current claims match code; Proposed claims are labeled. | Cross-check docs against inspected app/test files. |
| Runtime regression | App behavior remains unchanged. | No app-code tests required; optionally run `PYTHONPATH=. uv run pytest` if environment variables and dependencies are available. |

## Migration / Rollout

No runtime migration required. Rollout is a documentation-only commit. The only
file migration is `docs/prd.md` to `docs/PRD.md`; use a git-aware rename when
possible and verify only one PRD remains.

## Open Questions

- [ ] Should `README.md` link to `docs/README.md` in this change, or should the
  seven requested docs remain the only documentation surface?
- [ ] Should task planning split the seven-doc set to protect the 400-line
  review budget, or keep a concise single documentation PR?
