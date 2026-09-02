#!/usr/bin/env bash

# Exit on error
set -e

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Root directory of the project
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Default configuration values
IS_DEV=0
COMMAND=""
SERVICE=""

# Parse flags & commands
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dev|-d)
                IS_DEV=1
                shift
                ;;
            start|stop|restart|logs|status|migrate|consolidate-migrations|sync-prod-migrations|help)
                COMMAND="$1"
                shift
                ;;
            api|worker|db|redis|frontend)
                SERVICE="$1"
                shift
                ;;
            *)
                echo -e "${RED}Opción o comando desconocido: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
}

show_help() {
    echo -e "${BLUE}GestorFinanzas Smart Agent - Management CLI${NC}"
    echo ""
    echo "Uso: ./manage.sh <comando> [opciones]"
    echo ""
    echo "Comandos disponibles:"
    echo "  start                   Levanta todos los servicios en segundo plano"
    echo "  stop                    Detiene todos los servicios"
    echo "  restart                 Reinicia los servicios"
    echo "  status                  Muestra el estado de los contenedores"
    echo "  logs [servicio]         Muestra los logs en tiempo real (ej. ./manage.sh logs api)"
    echo "  migrate                 Aplica las migraciones pendientes de Alembic"
    echo "  consolidate-migrations  Elimina migraciones antiguas y genera una única versión inicial"
    echo "  sync-prod-migrations    Sello (stamp) 'head' en la BD de producción sin aplicar cambios"
    echo "  help                    Muestra esta ayuda"
    echo ""
    echo "Opciones:"
    echo "  --dev, -d               Ejecuta la acción en el entorno de desarrollo aislado (puertos distintos, BD dev)"
    echo ""
    echo "Ejemplos:"
    echo "  ./manage.sh start --dev"
    echo "  ./manage.sh logs api -d"
    echo "  ./manage.sh stop"
}

export_env_vars() {
    if [[ $IS_DEV -eq 1 ]] && [[ -f "$PROJECT_ROOT/backend/.env.dev" ]]; then
        set -a
        source "$PROJECT_ROOT/backend/.env.dev"
        set +a
    elif [[ $IS_DEV -eq 1 ]] && [[ -f "$PROJECT_ROOT/.env.dev" ]]; then
        set -a
        source "$PROJECT_ROOT/.env.dev"
        set +a
    elif [[ -f "$PROJECT_ROOT/backend/.env" ]]; then
        set -a
        source "$PROJECT_ROOT/backend/.env"
        set +a
    elif [[ -f "$PROJECT_ROOT/.env" ]]; then
        set -a
        source "$PROJECT_ROOT/.env"
        set +a
    fi

    if [[ $IS_DEV -eq 1 ]]; then
        echo -e "${YELLOW}>>> Modo DESARROLLO activado (--dev)${NC}"
        export COMPOSE_PROJECT_NAME="smartfinance-dev"
        export POSTGRES_DB="${POSTGRES_DB:-smart_finance_dev}"
        export POSTGRES_PORT="${POSTGRES_DEV_PORT:-5433}"
        export REDIS_PORT="${REDIS_DEV_PORT:-6380}"
        export API_PORT="${API_DEV_PORT:-8001}"
        export FRONTEND_PORT="${FRONTEND_DEV_PORT:-3001}"
    else
        echo -e "${GREEN}>>> Modo PRODUCCIÓN activado${NC}"
        export COMPOSE_PROJECT_NAME="smartfinance"
        export POSTGRES_DB="${POSTGRES_DB:-smart_finance}"
        export POSTGRES_PORT="${POSTGRES_PORT:-5432}"
        export REDIS_PORT="${REDIS_PORT:-6379}"
        export API_PORT="${API_PORT:-8000}"
        export FRONTEND_PORT="${FRONTEND_PORT:-80}"
    fi
}

ensure_db_exists() {
    echo -e "${BLUE}Verificando existencia de la base de datos '${POSTGRES_DB}'...${NC}"
    docker compose exec -T db psql -U "${POSTGRES_USER:-postgres}" -c "CREATE DATABASE ${POSTGRES_DB};" 2>/dev/null || true
}

start_services() {
    export_env_vars
    echo -e "${BLUE}Levantando contenedores de Docker...${NC}"
    docker compose up -d --build
    ensure_db_exists
    echo -e "${GREEN}Servicios levantados correctamente.${NC}"
    echo -e "Frontend: ${YELLOW}http://localhost:${FRONTEND_PORT}${NC}"
    echo -e "Backend API: ${YELLOW}http://localhost:${API_PORT}/api/v1/health${NC}"
    echo -e "PostgreSQL: ${YELLOW}localhost:${POSTGRES_PORT} (BD: ${POSTGRES_DB})${NC}"
}

stop_services() {
    export_env_vars
    echo -e "${BLUE}Deteniendo servicios de Docker...${NC}"
    docker compose down
    echo -e "${GREEN}Servicios detenidos.${NC}"
}

restart_services() {
    stop_services
    start_services
}

show_status() {
    export_env_vars
    docker compose ps
}

show_logs() {
    export_env_vars
    docker compose logs -f $SERVICE
}

run_migrations() {
    export_env_vars
    ensure_db_exists
    echo -e "${BLUE}Ejecutando migraciones de Alembic...${NC}"
    docker compose exec api alembic upgrade head
    echo -e "${GREEN}Migraciones aplicadas con éxito.${NC}"
}

consolidate_migrations() {
    export_env_vars
    ensure_db_exists
    echo -e "${YELLOW}Eliminando migraciones antiguas en backend/alembic/versions/...${NC}"
    rm -f backend/alembic/versions/*.py
    rm -rf backend/alembic/versions/__pycache__
    
    echo -e "${YELLOW}Limpiando tabla alembic_version en la base de datos...${NC}"
    docker compose exec -T db psql -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB}" -c "DROP TABLE IF EXISTS alembic_version CASCADE;" || true

    echo -e "${BLUE}Generando migración inicial única...${NC}"
    docker compose exec api alembic revision --autogenerate -m "consolidated_initial_schema"
    
    # Fix missing imports or extensions if generated
    for f in backend/alembic/versions/*.py; do
        if [[ -f "$f" ]]; then
            docker compose exec api chmod 666 "/app/alembic/versions/$(basename "$f")" 2>/dev/null || true
            if ! grep -q "import pgvector" "$f"; then
                sed -i 's/import sqlalchemy as sa/import sqlalchemy as sa\nimport pgvector/' "$f"
            fi
            if ! grep -q "CREATE EXTENSION IF NOT EXISTS vector;" "$f"; then
                sed -i 's/def upgrade() -> None:/def upgrade() -> None:\n    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")/' "$f"
            fi
        fi
    done

    echo -e "${GREEN}Nueva migración consolidada creada en backend/alembic/versions/${NC}"
    
    echo -e "${BLUE}Aplicando migración consolidada a la base de datos...${NC}"
    docker compose exec api alembic upgrade head
    echo -e "${GREEN}Base de datos sincronizada con la nueva migración.${NC}"
}

sync_prod_migrations() {
    export_env_vars
    ensure_db_exists
    echo -e "${YELLOW}Marcando (stamping) la base de datos como 'head' sin ejecutar SQL...${NC}"
    docker compose exec api alembic stamp head
    echo -e "${GREEN}Base de datos de producción marcada como actualizada.${NC}"
}

# Execution Entry Point
parse_args "$@"

case "$COMMAND" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    migrate)
        run_migrations
        ;;
    consolidate-migrations)
        consolidate_migrations
        ;;
    sync-prod-migrations)
        sync_prod_migrations
        ;;
    help|"")
        show_help
        ;;
esac
