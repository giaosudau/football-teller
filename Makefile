.PHONY: install test



POETRY ?= poetry
PYTHON ?= python

install:
	pip install --user $(POETRY)

include tests/test.env
export
test:
	$(POETRY) install --no-root
	$(POETRY) run $(PYTHON) -m unittest discover -v tests