FROM python:3.11-slim

# Create non-root user
RUN useradd -m appuser && mkdir /app && chown appuser:appuser /app
WORKDIR /app

# Copy application
COPY . /app

# Install dependencies as non-root
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Drop privileges
USER appuser

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off

CMD ["python", "input.py"]
