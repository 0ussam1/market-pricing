.PHONY: run test migrate lint

run:
	cd backend && uv run python manage.py runserver 0.0.0.0:8000

test:
	cd backend && uv run pytest tests/ -v --cov=backend --cov-report=term-missing

migrate:
	cd backend && uv run python manage.py migrate

lint:
	cd backend && uv run flake8 .
	cd backend && uv run black --check .
	cd backend && uv run isort --check-only .
