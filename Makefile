.PHONY: setup dev-setup start stop clean test migrate init-db check-deps

# System dependencies versions
PYTHON_VERSION := 3.11
PG_VERSION := 14
VENV_NAME := .venv

# Check system dependencies
check-deps:
	@which python3 > /dev/null || (echo "Installing Python..." && sudo apt-get update && sudo apt-get install -y python$(PYTHON_VERSION))
	@which rustc > /dev/null || (echo "Installing Rust..." && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh)
	@source "$$HOME/.cargo/env" || true

# Python packages with specific versions
BASE_REQUIREMENTS := \
	python-dotenv==1.0.0 \
	fastapi==0.104.1 \
	uvicorn==0.24.0 \
	sqlalchemy==2.0.23 \
	alembic==1.12.1 \
	psycopg2-binary==2.9.9 \
	pydantic[email]==2.4.2 \
	email-validator==2.1.0

DEV_REQUIREMENTS := \
	pytest==7.4.3 \
	pytest-cov==4.1.0 \
	black==23.10.1 \
	flake8==6.1.0

# System packages setup
	setup: check-deps clean
	sudo apt-get update
	sudo apt-get install -y python$(PYTHON_VERSION) python3-pip postgresql-$(PG_VERSION)
	python3 -m venv $(VENV_NAME)
	. $(VENV_NAME)/bin/activate && python3 -m pip install --upgrade pip wheel setuptools
	. $(VENV_NAME)/bin/activate && PYTHONPATH=$(PWD) pip install $(BASE_REQUIREMENTS)
	sudo systemctl start postgresql

# Development environment setup
dev-setup: setup
	. $(VENV_NAME)/bin/activate && pip install $(DEV_REQUIREMENTS)

# Database initialization
init-db:
	sudo systemctl start postgresql
	sudo -u postgres createdb supplychain_db || true
	test -f alembic.ini || (. $(VENV_NAME)/bin/activate && alembic init migrations)		
	. $(VENV_NAME)/bin/activate && alembic upgrade head

# Start application
start:
	. $(VENV_NAME)/bin/activate && python src/main.py

# Stop services
stop:
	sudo systemctl stop postgresql

# Clean environment
clean:
	sudo systemctl stop postgresql || true
	deactivate || true
	rm -rf $(VENV_NAME)
	find . -type d -name __pycache__ -exec rm -r {} +

# Run tests
test:
	. $(VENV_NAME)/bin/activate && pytest

# Database migrations
migrate:
	. $(VENV_NAME)/bin/activate && alembic upgrade head
