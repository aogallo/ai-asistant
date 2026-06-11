# Tasks: Invoice RAG Product and Technical Documentation

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 500-900 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 product/navigation -> PR 2 technical current-state docs -> PR 3 proposed RAG/API/plan docs |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-develop |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-develop
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Canonical PRD and docs hub | PR 1 | Rename/delete `docs/prd.md`; create `docs/PRD.md` and `docs/README.md`. |
| 2 | Current technical baseline | PR 2 | Create `docs/ARCHITECTURE.md` and `docs/DOMAIN_MODEL.md`; verify claims against code/tests. |
| 3 | Proposed RAG/API roadmap | PR 3 | Create `docs/RAG_STRATEGY.md`, `docs/API_DESIGN.md`, `docs/IMPLEMENTATION_PLAN.md`; label proposed behavior. |

## Phase 1: Source Review and Naming Baseline

- [x] 1.1 Inspect `app/api/`, `app/services/`, `app/models/`, `app/infrastructure/`, and `tests/` for Current invoice, AI, streaming, and persistence behavior to document.
- [x] 1.2 Inspect `docs/prd.md`; plan a git-aware rename or replacement so only canonical `docs/PRD.md` remains.

## Phase 2: Product and Navigation Docs

- [x] 2.1 Create `docs/README.md` as a navigation hub routing readers to product, architecture, domain, RAG, API, and plan docs.
- [x] 2.2 Create canonical `docs/PRD.md` from `docs/prd.md` as needed, covering SaaS-ready product direction, Current scope, Proposed scope, and non-goals.
- [x] 2.3 Verify `docs/prd.md` no longer remains as a conflicting separate PRD source.

## Phase 3: Current Technical Baseline Docs

- [x] 3.1 Create `docs/ARCHITECTURE.md` with Current FastAPI layers, invoice upload flow, generic AI flows, and Proposed SaaS/RAG evolution.
- [x] 3.2 Create `docs/DOMAIN_MODEL.md` with Current invoice database/domain entities and Proposed user, document, chunk, embedding, and citation concepts.
- [x] 3.3 Cross-check every Current claim in these docs against inspected code or tests.

## Phase 4: Proposed RAG, API, and Plan Docs

- [x] 4.1 Create `docs/RAG_STRATEGY.md` covering Proposed chunking, embeddings, retrieval, grounding, citations, authorization constraints, and evaluation.
- [x] 4.2 Create `docs/API_DESIGN.md` with Current endpoints and Proposed invoice query/chat API direction without adding runtime behavior.
- [x] 4.3 Create `docs/IMPLEMENTATION_PLAN.md` with phased, reviewable future work and explicit separation from this documentation-only change.

## Phase 5: Verification

- [x] 5.1 Verify all seven required docs exist under `docs/` and no app code was modified.
- [x] 5.2 Verify all auth, tenancy, object storage, vector search, embeddings, invoice chat, and RAG references are labeled **Proposed** unless code proves otherwise.
- [x] 5.3 Optionally run `PYTHONPATH=. uv run pytest` only if env vars and dependencies are available; record if skipped because this is documentation-only.
