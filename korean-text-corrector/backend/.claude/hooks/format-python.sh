#!/bin/bash

echo "🔧 Running Python formatter..."

cd "$(dirname "$0")/../.."

# Check if ruff is available
if ! command -v ruff &> /dev/null; then
    echo "⚠️  ruff not found, skipping formatting"
    exit 0
fi

# Format Python files
if ruff format . --quiet; then
    echo "✅ Python formatting completed"
else
    echo "⚠️  Formatting had some issues, but continuing"
fi

# Run basic checks
if ruff check . --fix --quiet 2>/dev/null; then
    echo "✅ Linting checks passed"
else
    echo "⚠️  Some linting issues remain"
fi

exit 0
