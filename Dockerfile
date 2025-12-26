FROM python:3.11-slim

# OS-level hardening
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && apt-get update && apt-get install -y --no-install-recommends \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy code and run as non-root
COPY . /app
RUN chown -R appuser:appuser /app && chmod -R go-w /app
USER appuser

ENTRYPOINT ["python", "input.py"]
