# Multi-stage Dockerfile for Flowzmith API

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies system-wide
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Flow CLI
RUN curl -sSL https://storage.googleapis.com/flow-cli/install.sh | bash && \
    mv /root/.local/bin/flow /usr/local/bin/flow

# Stage 2: Runtime
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages and binaries from builder
COPY --from=builder /usr/local /usr/local
COPY --from=builder /usr/local/bin/flow /usr/local/bin/flow

# Set working directory
WORKDIR /app

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY static/ ./static/
COPY context/ ./context/
COPY templates/ ./templates/
COPY knowledge_base/ ./knowledge_base/
COPY docs/ ./docs/
COPY contracts/ ./contracts/

# Create necessary directories with proper permissions
RUN mkdir -p /app/flow_projects /app/vector_db /app/logs /app/uploads /app/knowledge_base /app/data && \
    chmod -R 755 /app

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///./smart_contract_llm.db
ENV VECTOR_DB_PATH=/app/vector_db
ENV FLOW_PROJECTS_PATH=/app/flow_projects
ENV LOG_PATH=/app/logs

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application via Python module to avoid permission issues with local bin scripts
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]