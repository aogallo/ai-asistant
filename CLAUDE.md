# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Assistant built with FastAPI and Claude API (Anthropic SDK). Async-first Python application featuring streaming chat, an agentic tool-use loop, and invoice processing.

## Commands

```bash
make run       # Start dev server (uvicorn with --reload)
make lint      # Ruff check with auto-fix
make format    # Ruff format
make type      # MyPy strict type checking
make test      # Run pytest suite
```

**Setup:** `pip install uv && uv sync`

**Single test:** `uv run pytest tests/test_health.py -v`

## Architecture

Layered architecture with dependency injection via FastAPI `Depends()`:

```
API (app/api/) → Services (app/services/) → Infrastructure (app/infrastructure/)
                    ↕                              ↕
            Models (app/models/)          Anthropic Client
            Schemas (app/schemas/)
```

- **API Layer** (`app/api/`): Route handlers. Each file is a router mounted in `main.py`.
- **Services** (`app/services/`): Business logic — `LLMService` (summarization), `LLMStreamService` (streaming chat), `ClaudeAgentLoop` (agentic tool loop), `InvoiceService` (Excel/PDF invoice processing).
- **Infrastructure** (`app/infrastructure/`): External client factories (Anthropic SDK wrapper).
- **Schemas** (`app/schemas/`): Pydantic DTOs for request/response validation.
- **Models** (`app/models/`): Domain entities (invoice types, row schemas).
- **Core** (`app/core/`): Settings via `pydantic-settings` (loads from `.env`), structured logging with `structlog`.
- **Utils** (`app/utils/`): `ClaudeStreamParser` for parsing Anthropic streaming events.

## Key Patterns

- **Streaming**: Async generators + `StreamingResponse` for `/chat/stream` and `/agent/stream` endpoints.
- **Agent Loop**: `ClaudeAgentLoop` detects tool calls in stream → executes via `ToolRegistry` → feeds results back → loops until no more tool calls.
- **Tool Registry**: Tools registered in `app/agents/tools.py`, dispatched by name through registry pattern.
- **Config**: All secrets/settings via environment variables loaded through `app/core/config.py` (`Settings` class).

## Code Style

- **Line length**: 80 characters (ruff.toml)
- **Lint rules**: pycodestyle, pyflakes, isort, bugbear, pyupgrade; B008 ignored (function calls in defaults, needed for `Depends()`)
- **Type checking**: MyPy strict mode with Pydantic plugin
- **Python**: ≥3.12 required (pyproject.toml)

## Git Workflow

- **Main branch**: `develop`
- **Commit style**: Conventional commits (`fix:`, `feat:`, `chore:`, etc.)
