# Base stage: Install dependencies
FROM python:3.11-slim AS base

# Set the working directory inside the container
WORKDIR /app

# Set PYTHONPATH to include the /app directory
ENV PYTHONPATH=/app

# Copy the requirements file to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the source code into the container
COPY . .

# Application stage: Run the application
FROM base AS app

# Expose the port your application runs on (e.g., 8080 for FastAPI)
EXPOSE 8080

# Set the default command to run your application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# Testing stage: Run tests
FROM base AS test

# Set the default command to run tests
CMD ["pytest", "tests/"]