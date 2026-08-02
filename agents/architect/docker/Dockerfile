# ==============================================================================
# Architect Agent Dockerfile (Tier 4 - Enterprise Systems Architect)
# ==============================================================================

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    graphviz \
    plantuml \
    && rm -rf /var/lib/apt/lists/*

COPY agents/architect/docker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY agents/architect/src/ /app/src/
COPY policies/ /app/policies/

# Permissions for non-root user (UID 65534)
RUN mkdir -p /var/design-artifacts /var/design-artifacts/diagrams /var/design-artifacts/adr /tmp && \
    chown -R 65534:65534 /app /var/design-artifacts /tmp

USER 65534

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

EXPOSE 8080 9090

CMD ["python", "-m", "src.handlers.api_server"]
