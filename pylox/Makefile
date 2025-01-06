SCRIPTS_DIR := scripts
BASH_SCRIPT := generate_ast.sh

.PHONY: ast

ast:
	@echo "Running AST generation script..."
	bash $(SCRIPTS_DIR)/$(BASH_SCRIPT)

.PHONY: clean

clean:
	@echo "Cleaning generated files..."
	rm -f pylox/expr.py
