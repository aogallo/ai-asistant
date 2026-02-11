run:
	uv run uvicorn app.main:app --reload

lint:
	ruff check --fix .

format:
	ruff format . 

type:
	mypy app

test:
	pytest

