#!/usr/bin/env bash
# scripts/run_lighthouse.sh
# Executa Lighthouse contra as rotas principais em mobile + desktop e salva relatórios.
#
# Uso:
#   ./scripts/run_lighthouse.sh baseline       # primeira execução
#   ./scripts/run_lighthouse.sh checkpoint1    # após Bloco A
#   ./scripts/run_lighthouse.sh final          # após Bloco B

set -euo pipefail

LABEL="${1:-baseline}"
BASE_URL="${LIGHTHOUSE_BASE_URL:-https://www.celogos.com.br}"
OUT_DIR="reports/lighthouse/${LABEL}"

mkdir -p "$OUT_DIR"

ROUTES=(
    "home:/"
    "about:/about/"
    "contato:/contato/"
    "infantil:/servicos-educacionais/educacao-infantil"
    "fundamental1:/servicos-educacionais/ensino-fundamental-1"
    "medio:/servicos-educacionais/ensino-medio"
)

# Configurações: mobile (default LH) e desktop
declare -A FORM_FACTORS=(
    [mobile]="--form-factor=mobile --screenEmulation.mobile --throttling.cpuSlowdownMultiplier=4"
    [desktop]="--preset=desktop"
)

echo "Lighthouse run: label=$LABEL base=$BASE_URL"
echo "Saída em: $OUT_DIR"
echo ""

for entry in "${ROUTES[@]}"; do
    NAME="${entry%%:*}"
    PATH_URL="${entry##*:}"
    URL="${BASE_URL}${PATH_URL}"

    for ff in mobile desktop; do
        OUT="${OUT_DIR}/${NAME}-${ff}"
        echo "→ $NAME ($ff): $URL"
        # shellcheck disable=SC2086
        lighthouse "$URL" \
            ${FORM_FACTORS[$ff]} \
            --output=html,json \
            --output-path="$OUT" \
            --quiet \
            --chrome-flags="--headless=new --no-sandbox" \
            --only-categories=performance,accessibility,best-practices,seo \
            || echo "  (falhou, continuando)"
    done
done

echo ""
echo "Relatórios gerados em: $OUT_DIR"
