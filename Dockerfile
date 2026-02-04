FROM python:3.11-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && mkdir /app && chown appuser:appuser /app
WORKDIR /app

# Copy app files
COPY . /app

# Install dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Use non-root user
USER appuser

ENV PYTHONUNBUFFERED=1

# Create directories for runtime files
RUN mkdir -p /app/logs /app/backups

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD python -c "import sys; import importlib; importlib.import_module('input') or sys.exit(0)"

CMD ["python", "input.py"]
