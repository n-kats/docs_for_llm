.PHONY: lint format test
TARGET ?= .
lint:
	ruff check $(TARGET)
	mypy $(TARGET)
format:
	ruff format $(TARGET)
	ruff check --fix $(TARGET)
test:
	pytest
