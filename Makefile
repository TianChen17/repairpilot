.PHONY: bootstrap data test lint frontend-build warehouse-build quality demo-reset

bootstrap:
	./scripts/bootstrap.sh

data:
	./scripts/generate_seed.py

test:
	./.venv/bin/pytest -q backend/tests

lint:
	./.venv/bin/ruff check backend scripts

frontend-build:
	npm --prefix frontend run build

warehouse-build:
	./.venv/bin/dbt build --project-dir warehouse --profiles-dir warehouse

quality:
	./scripts/quality-gates.sh

demo-reset:
	curl -fsS -X POST http://127.0.0.1:8766/api/v1/demo/reset | jq .
