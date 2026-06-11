# Invoice RAG Documentation Specification

## Purpose

This capability defines a documentation-only baseline for the invoice assistant.
The documentation MUST describe implemented invoice ingestion and AI summary
behavior accurately, while marking SaaS, tenancy, invoice chat, and RAG
capabilities as Proposed when they are not implemented.

## Requirements

### Requirement: Documentation Set

The change MUST create the requested documentation set under `docs/` and MUST
avoid application runtime behavior changes.

| Document | Required focus |
|----------|----------------|
| `docs/README.md` | Navigation hub for the documentation set. |
| `docs/PRD.md` | Product direction and Current vs Proposed scope. |
| `docs/ARCHITECTURE.md` | Current FastAPI architecture and proposed SaaS/RAG evolution. |
| `docs/DOMAIN_MODEL.md` | Current invoice entities and proposed document/RAG concepts. |
| `docs/RAG_STRATEGY.md` | Proposed retrieval, chunking, embeddings, grounding, and citations. |
| `docs/API_DESIGN.md` | Current endpoints and proposed API direction. |
| `docs/IMPLEMENTATION_PLAN.md` | Phased, reviewable implementation path. |

#### Scenario: Documentation artifacts are present

- GIVEN the documentation change is applied
- WHEN a reviewer inspects `docs/`
- THEN each required document MUST exist with the required focus
- AND no app code change SHALL be required by this capability

#### Scenario: Lowercase PRD conflict is resolved

- GIVEN `docs/prd.md` exists before the change
- WHEN the documentation set is created
- THEN the canonical PRD MUST be `docs/PRD.md`
- AND conflicting lowercase PRD content MUST NOT remain as a separate source

### Requirement: Current vs Proposed Labeling

The documentation MUST distinguish Current implementation from Proposed product
direction and MUST NOT present missing SaaS/RAG capabilities as existing.

#### Scenario: Current behavior is documented from code

- GIVEN docs describe invoice upload, persistence, or batch AI analysis
- WHEN the behavior is labeled Current
- THEN the description MUST be supported by inspected code or tests
- AND unsupported assumptions MUST NOT be stated as facts

#### Scenario: Future behavior is explicitly marked

- GIVEN docs mention authentication, tenancy, invoice chat, vector search,
  embeddings, object storage, migrations, or RAG retrieval
- WHEN those capabilities are not present in the codebase
- THEN the docs MUST label them as Proposed
- AND readers MUST be able to tell they are not implemented today

### Requirement: SaaS-Ready Product Direction

The documentation SHOULD frame future product decisions for a multi-user SaaS
invoice assistant without requiring those features in this change.

#### Scenario: Product docs communicate SaaS direction

- GIVEN a future agent reads the PRD or implementation plan
- WHEN they look for product direction
- THEN the docs SHOULD identify multi-user SaaS readiness as the target
- AND SHOULD separate future tenant/security work from current behavior

#### Scenario: Security boundaries are not overclaimed

- GIVEN docs describe user ownership, authorization, or tenant isolation
- WHEN those mechanisms are not implemented
- THEN the docs MUST present them as Proposed boundaries
- AND MUST NOT imply current production-grade isolation

### Requirement: Reviewable Agent-Friendly Structure

The documentation MUST reduce cognitive load for human reviewers and future AI
coding agents through concise structure, summaries, tables, and explicit
non-goals.

#### Scenario: Reader can find the next document

- GIVEN a reader starts at `docs/README.md`
- WHEN they need product, architecture, domain, RAG, API, or plan details
- THEN the README MUST route them to the relevant document

#### Scenario: Out-of-scope behavior is clear

- GIVEN a reviewer checks the documentation change
- WHEN they look for implementation impact
- THEN the docs MUST state that runtime upload, chat, authentication, tenancy,
  vector search, and RAG behavior are out of scope for this change
