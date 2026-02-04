# Use a minimal base image
FROM python:3.11-slim

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /home/app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY input.py .

# Change ownership to non-root user
RUN chown -R app:app /home/app

# Switch to non-root user
USER app

# Expose port if needed (not in this case)
# EXPOSE 8000

# Run the application
CMD ["python", "input.py"]