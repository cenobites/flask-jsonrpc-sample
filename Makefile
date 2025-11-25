.PHONY: all clean style typing test release env

VIRTUALENV_EXISTS := $(shell [ -d apps/lms-api/.venv ] && echo 1 || echo 0)

all: clean test
	@python -c "print('OK')"

clean:
	find {apps/lms-api/src,apps/lms-api/tests} -regex ".*\.\(so\|pyc\)" | xargs rm -rf
	find {apps/lms-api/src,apps/lms-api/tests} -name "__pycache__" -o -name ".coverage" -o -name "junit" -o -name "coverage.lcov" -o -name "htmlcov" -o -name ".tox"  -o -name ".pytest_cache" -o -name ".ruff_cache"  -o -name ".pkg" -o -name ".tmp" -o -name "*.so" | xargs rm -rf
# 	rm -rf .coverage coverage.* .eggs/ .mypy_cache/ .pytype/ .ruff_cache/ .pytest_cache/ .tox/ src/*.egg-info/ htmlcov/ junit/ htmldoc/ build/ dist/ wheelhouse/ __pycache__/

style:
	(cd apps/lms-api && uv run ruff check .) &
	(cd apps/lms-api && uv run ruff format .)

typing:
	(cd apps/lms-api && uv run mypy --install-types --non-interactive src/) &
	(cd apps/lms-api && uv run pyright)

dev:
	(cd apps/lms-api && uv run flask --app lms run --reload) &
	(cd apps/lms-ui && yarn dev)

test: clean
	(cd apps/lms-api && uv run pytest --numprocesses=0 --count=1 --reruns=0)

release: test
	(cd apps/lms-api && uv build)
	(cd apps/lms-api && uv tool run twine check --strict dist/*)

env:
ifeq ($(VIRTUALENV_EXISTS), 0)
	(cd apps/lms-api && uv venv --clear)
endif
	(cd apps/lms-api && uv sync --locked)
	@echo "To activate the virtualenv, run: source apps/lms-api/.venv/bin/activate"
