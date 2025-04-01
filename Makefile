.PHONY: setup dev-setup start stop clean test migrate init-db check-deps check-venv check-db setup-python create-venv

# System dependencies versions
PYTHON_VERSION := 3.11
VENV_NAME := .venv

# Check system dependencies
check-deps:
	@which python$(PYTHON_VERSION) > /dev/null || (echo "Python $(PYTHON_VERSION) is not installed. Please install it first."; exit 1)

# Ensure Python 3.11 is installed and linked
setup-python:
	@echo "Setting up Python $(PYTHON_VERSION)..."
	python$(PYTHON_VERSION) --version || (echo "Python $(PYTHON_VERSION) is not installed. Please install it first."; exit 1)

# Create a new target to set up the virtual environment only
create-venv: check-deps setup-python
	@echo "Creating Python virtual environment..."
	rm -rf $(VENV_NAME)
	/opt/homebrew/bin/python$(PYTHON_VERSION) -m venv $(VENV_NAME) --clear
	@if [ ! -f "$(VENV_NAME)/bin/activate" ]; then \
		echo "Virtual environment creation failed!"; \
		exit 1; \
	fi
	bash -c "source $(VENV_NAME)/bin/activate && python -m pip install --upgrade pip wheel setuptools"
	@echo "Virtual environment created successfully."

# Check if virtual environment exists
check-venv:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Check if database exists
check-db:
	@echo "Checking if database 'supplychain_db' exists..."
	@if ! psql -lqt | cut -d \| -f 1 | grep -qw supplychain_db; then \
		echo "Database 'supplychain_db' does not exist. Run 'make init-db' to create it."; \
		exit 1; \
	else \
		echo "Database 'supplychain_db' exists."; \
	fi

# Python packages with specific versions
BASE_REQUIREMENTS := \
	python-dotenv==1.0.0 \
	fastapi==0.104.1 \
	starlette==0.27.0 \
	uvicorn==0.24.0 \
	sqlalchemy==2.0.23 \
	alembic==1.12.1 \
	psycopg2-binary==2.9.9 \
	pydantic==1.10.12 \
	pydantic[email]==1.10.12 \
	python-multipart==0.0.6 \
	requests==2.31.0 \
	httpx==0.28.1

DEV_REQUIREMENTS := \
	coverage==6.5.0 \
	pytest==7.4.3 \
	pytest-cov==4.1.0 \
	black==23.10.1 \
	flake8==6.1.0 \
	httpx==0.28.1

# System packages setup
setup: create-venv
	@echo "Installing base requirements..."
	bash -c "source $(VENV_NAME)/bin/activate && PYTHONPATH=$(PWD) pip install $(BASE_REQUIREMENTS)"
	@echo "Base requirements installed."
	$(MAKE) init-db
	$(MAKE) migrate
	@echo "Environment setup complete."
	@echo "To activate the virtual environment, run: source $(VENV_NAME)/bin/activate"
	@echo "To start the application, run: make start"

# Development environment setup
dev-setup: setup
	@echo "Setting up the development environment..."
	bash -c "source $(VENV_NAME)/bin/activate && pip install $(DEV_REQUIREMENTS)"

# Database initialization
init-db: check-venv
	@echo "Initializing the database..."
	createdb supplychain_db || true
	bash -c "source $(VENV_NAME)/bin/activate && test -f alembic.ini || alembic init migrations"
	bash -c "source $(VENV_NAME)/bin/activate && alembic upgrade head"

# Start application
start: check-venv
	@echo "Starting the application..."
	bash -c "source $(VENV_NAME)/bin/activate && python src/main.py"

# Stop services
stop:
	@echo "Stopping services..."
	@echo "No services to stop. Ensure your database is managed externally."

# Clean environment
clean:
	@echo "Cleaning the environment..."
	rm -rf $(VENV_NAME)

# Run tests
test: dev-setup
	@echo "Running tests..."
	bash -c "source $(VENV_NAME)/bin/activate && PYTHONPATH=$(PWD) pytest"

# Database migrations
migrate: check-venv
	@echo "Running database migrations..."
	bash -c "source $(VENV_NAME)/bin/activate && PYTHONPATH=$(PWD) alembic upgrade head"

#Manual Steps to install the package
# Remove existing virtualenv
#rm -rf .venv
# brew reinstall python@3.11
#
# Create new virtualenv with explicit Python path
#/opt/homebrew/bin/python3.11 -m venv .venv
# Activate and install requirements
#bash -c "source .venv/bin/activate && pip install --upgrade pip wheel setuptools"
#bash -c "source .venv/bin/activate && pip install python-dotenv fastapi uvicorn sqlalchemy alembic psycopg2-binary pydantic python-multipart requests httpx"