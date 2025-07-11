# Multi-stage Docker build for SDLC Orchestrator
FROM node:18-alpine AS frontend-builder

# Set working directory for frontend
WORKDIR /app/frontend

# Copy frontend package files
COPY package*.json ./
COPY *.json ./
COPY *.tsx ./
COPY *.ts ./
COPY components/ ./components/
COPY hooks/ ./hooks/
COPY services/ ./services/
COPY utils/ ./utils/

# Install frontend dependencies
RUN npm ci --only=production

# Build frontend
RUN npm run build

# Python backend stage
FROM python:3.12-slim AS backend-builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python source code
COPY src/ ./src/
COPY main.py .
COPY *.py ./

# Copy frontend build output
COPY --from=frontend-builder /app/frontend/dist ./static/

# Production stage
FROM python:3.12-slim AS production

# Create non-root user
RUN useradd --create-home --shell /bin/bash sdlc

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application from builder
COPY --from=backend-builder /app .
COPY --from=backend-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Create necessary directories
RUN mkdir -p /app/database /app/logs && \
    chown -R sdlc:sdlc /app

# Copy health check script
COPY docker/healthcheck.py /app/healthcheck.py

# Switch to non-root user
USER sdlc

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python healthcheck.py || exit 1

# Default command
CMD ["python", "main.py"]
