#!/usr/bin/env bash
# scripts/check.sh
# Espelha exatamente o pipeline de CI: ruff -> ruff format --check -> mypy --strict -> pytest
# Uso: ./scripts/check.sh
# Falha rápido (set -e) e mostra qual etapa falhou.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

step() {
    echo ""
    echo -e "${YELLOW}==> $1${NC}"
}

ok() {
    echo -e "${GREEN}✓ $1${NC}"
}

fail() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# 1) Lint
step "1/4 ruff check ."
ruff check . || fail "ruff check falhou"
ok "ruff check"

# 2) Format
step "2/4 ruff format --check ."
ruff format --check . || fail "ruff format --check falhou (rode: ruff format .)"
ok "ruff format --check"

# 3) Type check
step "3/4 mypy --strict src"
mypy --strict src || fail "mypy --strict falhou"
ok "mypy --strict src"

# 4) Tests (coverage ativa quando ha codigo em src/)
step "4/4 pytest"
SRC_HAS_CODE=$(find src -type f -name "*.py" ! -name "__init__.py" 2>/dev/null | head -1 || true)
if [ -n "$SRC_HAS_CODE" ]; then
    pytest --cov=src --cov-report=term-missing --cov-report=html:reports/coverage --cov-fail-under=80 \
        || fail "pytest falhou"
else
    pytest || fail "pytest falhou"
fi
ok "pytest"

echo ""
echo -e "${GREEN}=================================="
echo -e " Todos os checks passaram com sucesso"
echo -e "==================================${NC}"
