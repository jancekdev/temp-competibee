
default:
    @just --list

# Bootstrap the local development environment
setup:
    docker compose -f docker-compose.local.yml --profile setup run --rm setup
    if [ -f .setup-complete ] && [ -d config/setup ]; then rm -rf config/setup; fi

# Internal helper that runs setup only when needed
ensure-setup:
    if [ ! -d .envs ] && [ -d .envs.example ]; then cp -r .envs.example .envs; fi
    if [ ! -f .setup-complete ]; then docker compose -f docker-compose.local.yml --profile setup run --rm setup; fi
    if [ -f .setup-complete ] && [ -d config/setup ]; then rm -rf config/setup; fi

# Start development environment with Docker
up: ensure-setup
    docker compose -f docker-compose.local.yml up --build

# Stop development environment
down:
    docker compose -f docker-compose.local.yml down

# View Docker logs
logs: ensure-setup
    docker compose -f docker-compose.local.yml logs -f

# Execute commands inside Django container
exec *args: ensure-setup
    docker compose -f docker-compose.local.yml exec -u $(id -u):$(id -g) django {{ args }}

# Django shell in Docker
shell: ensure-setup
    docker compose -f docker-compose.local.yml exec -u $(id -u):$(id -g) django python manage.py shell_plus

# Run migrations in Docker
migrate: ensure-setup
    docker compose -f docker-compose.local.yml exec -u $(id -u):$(id -g) django python manage.py migrate

# Create migrations in Docker
makemigrations: ensure-setup
    docker compose -f docker-compose.local.yml exec -u $(id -u):$(id -g) django python manage.py makemigrations

# Run tests in Docker
test: ensure-setup
    docker compose -f docker-compose.local.yml exec -u $(id -u):$(id -g) django pytest

# Install new package via uv in Docker
add package: ensure-setup
    docker compose -f docker-compose.local.yml exec django uv add {{ package }}

# Install new dev package via uv in Docker
add-dev package: ensure-setup
    docker compose -f docker-compose.local.yml exec -u $(id -u):$(id -g) django uv add --dev {{ package }}

# Rebuild containers when dependencies change
rebuild: ensure-setup
    docker compose -f docker-compose.local.yml build --no-cache

# Django management command runner
manage *args: ensure-setup
    docker compose -f docker-compose.local.yml exec -u $(id -u):$(id -g) django python manage.py {{ args }}

# Add a new Django app
startapp name: ensure-setup
    docker compose -f docker-compose.local.yml exec -u $(id -u):$(id -g) django python manage.py startapp {{ name }}


tailwind-watch: ensure-setup
    docker compose -f docker-compose.local.yml exec react sh -c "cd /app/frontend/django/static/jsutils && npx @tailwindcss/cli -i ./tailwind.css -o ../css/output.css --watch"

ruff-check: ensure-setup
    docker compose -f docker-compose.local.yml exec -u $(id -u):$(id -g) django ruff check --no-cache .

ruff-format: ensure-setup
    docker compose -f docker-compose.local.yml exec -u $(id -u):$(id -g) django ruff format --no-cache .

ruff-fix: ensure-setup
    docker compose -f docker-compose.local.yml exec -u $(id -u):$(id -g) django ruff check --fix --no-cache .

mypy: ensure-setup
    docker compose -f docker-compose.local.yml exec -u $(id -u):$(id -g) django mypy .