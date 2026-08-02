# ==============================================================================
# GPIS PDP (Governance Policy Inquiry Service) Dockerfile
# Base Image: Python 3.12-slim (Non-root UID 65534 compliance)
# ==============================================================================

FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy GPIS source code and policy definitions
COPY app/ /app/app/
COPY policies/ /app/policies/

# Create app directory permissions for non-root nobody user (UID 65534)
RUN chown -R 65534:65534 /app

USER 65534

# Expose PDP port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Launch FastAPI PDP server via uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
