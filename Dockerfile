# Dockerfile for Smart Contract LLM Builder

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Install Flow CLI
RUN curl -sSL https://storage.googleapis.com/flow-cli/install.sh | bash

# Create necessary directories
RUN mkdir -p /app/flow_projects /app/vector_db /app/logs /app/uploads

# Copy static files (if any)
COPY static/ ./static/

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH=$PATH:/root/.local/bin

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]