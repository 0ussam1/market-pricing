FROM mcr.microsoft.com/playwright/python:v1.56.0-noble

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Create non-root user
RUN useradd -m appuser

# uv venv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Copy deps first (layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --no-install-project

# Copy source
COPY . .

# Fix ownership (appuser needs access to pre-installed Playwright browsers)
RUN chown -R appuser:appuser /app /opt/venv /ms-playwright

USER appuser

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
