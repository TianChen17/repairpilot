.PHONY: bootstrap data ingest test lint frontend-build warehouse-build quality live-e2e demo-reset video-lint video-render

bootstrap:
	./scripts/bootstrap.sh

data:
	./scripts/generate_seed.py

ingest:
	./scripts/ingest_datahub.sh

test:
	./.venv/bin/pytest -q backend/tests

lint:
	./.venv/bin/ruff check backend scripts video/scripts

frontend-build:
	npm --prefix frontend run build

warehouse-build:
	./.venv/bin/dbt build --project-dir warehouse --profiles-dir warehouse

quality:
	./scripts/quality-gates.sh

live-e2e:
	./scripts/live-e2e.sh

demo-reset:
	curl -fsS -X POST http://127.0.0.1:8766/api/v1/demo/reset | jq .

video-lint:
	npm --prefix video run lint

video-render:
	cd video && npm run render -- --browser-executable=/snap/bin/chromium
	./video/scripts/normalize_audio.sh
	./video/scripts/validate_video.sh
