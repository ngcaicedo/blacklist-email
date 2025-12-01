#!/bin/bash

# ============================================
# Script de Pruebas de Estrés con Newman
# ============================================
# Este script ejecuta pruebas de carga contra la API de Blacklist
# para generar tráfico y validar el monitoreo en New Relic

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# URLs disponibles
LOCAL_URL="http://localhost:9000"
AWS_URL="http://LB-Blacklist-app-961785232.us-east-1.elb.amazonaws.com"

# Configuración por defecto
BASE_URL="${BASE_URL:-$LOCAL_URL}"
ITERATIONS="${ITERATIONS:-100}"
DELAY="${DELAY:-50}"
COLLECTION="blacklist-api.postman_collection.json"

# Detectar ambiente
if [[ "$1" == "aws" || "$1" == "cloud" ]]; then
    BASE_URL="$AWS_URL"
    echo -e "${BLUE}🌐 Ejecutando contra AWS Cloud${NC}"
elif [[ "$1" == "local" ]]; then
    BASE_URL="$LOCAL_URL"
    echo -e "${BLUE}🏠 Ejecutando contra Local${NC}"
fi

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   Pruebas de Estrés - Blacklist API${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "${YELLOW}Configuración:${NC}"
echo -e "  URL Base: ${GREEN}$BASE_URL${NC}"
echo -e "  Iteraciones: ${GREEN}$ITERATIONS${NC}"
echo -e "  Delay entre requests: ${GREEN}${DELAY}ms${NC}"
echo ""

# Verificar que Newman esté instalado
if ! command -v newman &> /dev/null; then
    echo -e "${RED}Error: Newman no está instalado${NC}"
    echo -e "${YELLOW}Instalando Newman...${NC}"
    npm install -g newman newman-reporter-htmlextra
fi

# Verificar que el servicio esté disponible
echo -e "${YELLOW}Verificando disponibilidad del servicio...${NC}"
if curl -s "$BASE_URL/health" > /dev/null; then
    echo -e "${GREEN}✓ Servicio disponible${NC}"
else
    echo -e "${RED}✗ El servicio no está disponible en $BASE_URL${NC}"
    echo -e "${YELLOW}Asegúrate de que docker-compose esté corriendo:${NC}"
    echo -e "  docker-compose up -d"
    exit 1
fi

echo ""
echo -e "${YELLOW}Iniciando pruebas de estrés...${NC}"
echo ""

# Crear directorio de reportes si no existe
mkdir -p reports

# Ejecutar Newman con las pruebas de estrés
newman run "$COLLECTION" \
    --env-var "base_url=$BASE_URL" \
    --iteration-count "$ITERATIONS" \
    --delay-request "$DELAY" \
    --reporters cli,htmlextra \
    --reporter-htmlextra-export "reports/stress-test-report-$(date +%Y%m%d-%H%M%S).html" \
    --reporter-htmlextra-title "Blacklist API - Stress Test Report" \
    --reporter-htmlextra-browserTitle "Stress Test Results"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   Pruebas completadas exitosamente${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${YELLOW}Revisa los resultados en:${NC}"
echo -e "  - New Relic Dashboard"
echo -e "  - Reportes HTML en: ./reports/"
echo ""

