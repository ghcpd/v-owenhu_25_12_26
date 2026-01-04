FROM python:3.11-slim

# Set security-related environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY input.py .
COPY input_backup.py .

# Create logs directory with proper permissions
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

# Use non-root user
USER appuser

# Expose port if API server is added later
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sqlite3; sqlite3.connect('users.db').execute('SELECT 1')" || exit 1

# Default command
CMD ["python", "input.py"]
