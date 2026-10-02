VENV := .venv
PYTHON := $(VENV)/bin/python

.PHONY: validate

validate: $(VENV)/.installed
	$(PYTHON) scripts/validate.py

$(VENV)/.installed:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --quiet "jsonschema[format]" rfc8785
	touch $@
