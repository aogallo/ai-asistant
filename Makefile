run:
	uv run uvicorn app.main:app --reload

lint:
	ruff check .

format:
	ruff format . --fix

type:
	mypy app

test:
	pytest

