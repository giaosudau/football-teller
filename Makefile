.PHONY: install test



POETRY ?= poetry
PYTHON ?= python

install:
	pip install --user $(POETRY)

include conf/.env.test
export
test:
	$(POETRY) install --no-root
	$(POETRY) run $(PYTHON) -m unittest discover -v tests