#!/bin/bash

# Set the working directory to `pylox/`
cd "$(dirname "$0")/.." || exit 1

# Set PYTHONPATH to the current directory (pylox)
export PYTHONPATH=$(pwd)

# Run the Python script from the `tools` folder
python3 tools/generate_ast.py
