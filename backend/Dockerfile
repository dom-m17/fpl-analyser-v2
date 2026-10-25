# syntax=docker/dockerfile:1

# ---------- Stage 1: build the dependency virtualenv ----------
FROM python:3.13-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN python -m venv /opt/venv

# Install dependencies against a stub package first. This layer is keyed on
# pyproject.toml alone, so editing src/ no longer re-resolves and re-downloads
# fastapi/httpx/uvicorn on every build.
COPY pyproject.toml ./
RUN mkdir -p src/fpl \
    && touch src/fpl/__init__.py \
    && pip install .

# Now the real source, installed without touching the dependency layer above.
COPY src ./src
RUN pip install --no-deps --force-reinstall .

# ---------- Stage 2: runtime ----------
FROM python:3.13-slim AS runtime

# PYTHONUNBUFFERED keeps logs flowing to `docker logs` instead of sitting in a
# buffer; PYTHONDONTWRITEBYTECODE avoids .pyc churn in a read-only-ish layer.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Unprivileged user: a container escape shouldn't start as root.
RUN useradd --create-home --uid 10001 app

# The venv carries both the dependencies and the installed fpl package, so the
# source tree itself never has to ship. No compilers or pip caches come with it.
COPY --from=builder /opt/venv /opt/venv

USER app
WORKDIR /home/app

EXPOSE 8000

# One worker on purpose: fpl.cache holds the FPL payloads in module-level
# globals, so every extra worker would keep its own copy and independently poll
# the upstream API. Scale with replicas, not workers.
CMD ["uvicorn", "fpl.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
