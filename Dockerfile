# Base stage: shared setup
FROM python:3.11-slim AS base

# Set the working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# App stage: for running the application
FROM base AS app
ENV ENV=development
EXPOSE 8080
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]

# Test stage: for running tests
FROM base AS test
CMD ["pytest", "tests/"]
