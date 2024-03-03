POETRY = poetry

lint: ruff mypy
	@echo '[OK] Linters checks passed successfully'

mypy:
	$(POETRY) run mypy --config-file pyproject.toml --cache-dir=/dev/null .

ruff:
	$(POETRY) run ruff check . --no-cache

fmt:
	$(POETRY) run ruff check --select I --fix .
	$(POETRY) run ruff format . --no-cache
	@echo '[OK] Formatters went through successfully'
