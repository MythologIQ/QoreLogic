# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r qorelogic && useradd -r -g qorelogic qorelogic

# Install runtime dependencies (e.g. sqlite3 library is usually standard in python images, 
# but Z3 might need libs if not statically linked. z3-solver pip package includes binaries)
# Installing minimal runtime deps if needed.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . /app

# Set permissions
RUN chown -R qorelogic:qorelogic /app

# Switch to non-root user
USER qorelogic

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Entrypoint
# Assuming the server is run via python module or script
# Based on existing patterns: python local_fortress/mcp_server/server.py
ENTRYPOINT ["python", "local_fortress/mcp_server/server.py"]
