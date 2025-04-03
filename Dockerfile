# Base stage: shared setup
FROM python:3.11-slim AS base

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# App stage
FROM base AS app
EXPOSE 8080
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# Test stage
FROM base AS test
CMD ["pytest", "tests/"]