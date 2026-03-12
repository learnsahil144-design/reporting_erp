# ========== STAGE 1: Build Stage ==========
FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# ========== STAGE 2: Final Stage ==========
FROM python:3.11-slim

WORKDIR /app

# Install only the runtime dependencies (libpq is needed for psycopg2-binary)
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

# Copy Project
COPY . .

# Security: Non-root user
RUN addgroup --system django \
    && adduser --system --ingroup django django \
    && chown -R django:django /app

# Create static and media folders with correct permissions
RUN mkdir -p /app/staticfiles /app/media \
    && chown -R django:django /app/staticfiles /app/media

# Switch to the non-root user
USER django

EXPOSE 8900

# Metadata
LABEL maintainer="ReportSystem Team"
LABEL version="1.0"

COPY entrypoint.sh /entrypoint.sh
# Note: entrypoint.sh permissions should be handled by git/filesystem, 
# but we can ensure it here if we were root. Since we are django user now, 
# we rely on the host permission or a previous step as root.

USER root
RUN chmod +x /entrypoint.sh
USER django

CMD ["/entrypoint.sh"]