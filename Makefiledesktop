.PHONY: setup dev-setup start stop clean test migrate init-db check-deps

# System dependencies versions
PG_VERSION := 14
VENV_NAME := .venv

# Detect environment (container vs normal)
CONTAINER_ENV := $(shell test -f /.dockerenv && echo 1 || echo 0)
ifeq ($(CONTAINER_ENV),1)
	SERVICE_CMD := service
else
	SERVICE_CMD := systemctl
endif

# Check system dependencies
check-deps:
	@which python3 > /dev/null || (echo "Installing Python..." && sudo apt-get update && sudo apt-get install -y python3-minimal python3-venv)
	@which rustc > /dev/null || (echo "Installing Rust..." && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh)
	@source "$$HOME/.cargo/env" || true
	@echo "Setting up PostgreSQL repository..."
	@sudo apt-get install -y curl ca-certificates gnupg
	@curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /usr/share/keyrings/postgresql-keyring.gpg
	@echo "deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] http://apt.postgresql.org/pub/repos/apt $$(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/postgresql.list > /dev/null
	@sudo apt-get update

# Python packages with specific versions
BASE_REQUIREMENTS := \
	python-dotenv==1.0.0 \
	fastapi==0.104.1 \
	uvicorn==0.24.0 \
	sqlalchemy==2.0.23 \
	alembic==1.12.1 \
	psycopg2-binary==2.9.9 \
	pydantic[email]==2.4.2 \
	email-validator==2.1.0 \
	python-multipart==0.0.6

DEV_REQUIREMENTS := \
	pytest==7.4.3 \
	pytest-cov==4.1.0 \
	black==23.10.1 \
	flake8==6.1.0

# System packages setup
setup: check-deps clean
	sudo apt-get update
	sudo DEBIAN_FRONTEND=noninteractive apt-get install -y postgresql-$(PG_VERSION) postgresql-contrib-$(PG_VERSION)
	sudo apt-get install -y python3-venv python3-pip
	python3 -m venv $(VENV_NAME)
	. $(VENV_NAME)/bin/activate && python3 -m pip install --upgrade pip wheel setuptools
	. $(VENV_NAME)/bin/activate && PYTHONPATH=$(PWD) pip install $(BASE_REQUIREMENTS)
	sudo $(SERVICE_CMD) postgresql start

# Development environment setup
dev-setup: setup
	. $(VENV_NAME)/bin/activate && pip install $(DEV_REQUIREMENTS)

# Database initialization
init-db:
	sudo $(SERVICE_CMD) postgresql start
	sudo -u postgres createdb supplychain_db || true
	test -f alembic.ini || (. $(VENV_NAME)/bin/activate && alembic init migrations)
	. $(VENV_NAME)/bin/activate && alembic upgrade head

# Start application
start:
	. $(VENV_NAME)/bin/activate && python src/main.py

# Stop services
stop:
	sudo $(SERVICE_CMD) postgresql stop

# Clean environment
clean:
	sudo $(SERVICE_CMD) postgresql stop || true
	-deactivate || true
	rm -rf $(VENV_NAME)
	find . -type d -name __pycache__ -exec rm -r {} +

# Run tests
test:
	. $(VENV_NAME)/bin/activate && pytest

# Database migrations
migrate:
	. $(VENV_NAME)/bin/activate && alembic upgrade head
