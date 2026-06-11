# Proposal: Invoice RAG Product and Technical Documentation

## Intent

Create a trustworthy documentation baseline for a multi-user SaaS-ready invoice assistant. The docs must explain current FastAPI invoice upload, persistence, and AI summarization behavior, while clearly marking invoice chat, tenancy, security boundaries, and RAG capabilities as **Proposed** when they are not implemented.

## Scope

### In Scope
- Create/update `docs/README.md`, `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/DOMAIN_MODEL.md`, `docs/RAG_STRATEGY.md`, `docs/API_DESIGN.md`, and `docs/IMPLEMENTATION_PLAN.md`.
- Inspect current code before documenting implementation details.
- Use clear Markdown, concrete examples, and Current vs Proposed labels for future AI coding agents.
- Resolve the existing lowercase `docs/prd.md` naming risk by replacing or renaming it to requested `docs/PRD.md` without keeping conflicting PRD files.

### Out of Scope
- Runtime upload, chat, authentication, tenancy, vector search, or RAG implementation changes.
- Database migrations, frontend work, object storage, embeddings, or new API behavior.

## Capabilities

### New Capabilities
- `invoice-rag-documentation`: Defines requirements for the documentation set covering current invoice ingestion, proposed SaaS tenancy/security model, proposed invoice chat/RAG evolution, API direction, and implementation planning.

### Modified Capabilities
- None. No existing `openspec/specs/` capabilities were found.

## Approach

Use the exploration recommendation: a Current-vs-Proposed documentation baseline. Each doc should lead with implemented facts from code, then separate proposed SaaS/RAG direction. Keep docs reviewable and agent-friendly with summaries, tables, examples, and explicit non-goals.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `docs/` | New/Modified | Add the requested documentation set and handle `prd.md` -> `PRD.md`. |
| `app/api/`, `app/services/`, `app/models/`, `app/infrastructure/` | Reference only | Source material for accurate Current-state documentation. |
| `README.md` | Possible Modified | Optional link to `docs/README.md`; no behavior change. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Docs imply proposed SaaS/RAG features already exist | Med | Require explicit Current/Proposed labels. |
| `docs/prd.md` vs `docs/PRD.md` causes case conflicts | Med | Produce one canonical `docs/PRD.md` and remove/replace the lowercase stub. |
| Seven docs exceed review budget | Med | Keep first pass concise and consider task slicing later. |

## Rollback Plan

Revert the documentation commit: remove newly added docs, restore `docs/prd.md` if renamed, and leave application code untouched.

## Dependencies

- Existing codebase inspection and `openspec/changes/invoice-rag-documentation/exploration.md`.
- User direction that the product is multi-user SaaS-ready and this change is documentation-only.

## Success Criteria

- [ ] Requested docs exist under `docs/` with canonical `docs/PRD.md` naming.
- [ ] Current implementation details are accurate and not invented.
- [ ] Proposed SaaS, tenancy, security, API, and RAG pieces are labeled as **Proposed**.
- [ ] No application behavior changes are introduced.
