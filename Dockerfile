# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml poetry.lock ./
COPY smt_planning ./smt_planning
COPY README.md ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Install gunicorn for production REST server
RUN pip install gunicorn

# Copy and setup entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create user for security
RUN groupadd --gid 1001 --system appgroup && \
    useradd --no-create-home --shell /bin/false --uid 1001 --system --gid appgroup appuser

# Create data directory
RUN mkdir -p /data && \
    chown -R appuser:appgroup /app /data

USER appuser

# Expose port 5000 for REST API
EXPOSE 5000

# Health check for REST API
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:5000/ping || exit 1

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["rest"]
