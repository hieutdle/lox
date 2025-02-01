SCRIPTS_DIR := scripts
BASH_SCRIPT := generate_ast.sh

.PHONY: activate

activate:
	@echo "Activating virtual environment..."
	@bash -c "source .venv/bin/activate && exec zsh"

.PHONY: ast

ast:
	@echo "Running AST generation script..."
	bash $(SCRIPTS_DIR)/$(BASH_SCRIPT)

.PHONY: clean

clean:
	@echo "Cleaning generated files..."
	rm -f pylox/expr.py

.PHONY: test

test:
	@pytest

.PHONY: run

run:
	python3 plox/__main__.py

.PHONY: requirements

requirements:
	@magic add $(shell tr '\n' ' ' < requirements.txt)
