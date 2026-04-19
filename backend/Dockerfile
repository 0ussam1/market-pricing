FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Create non-root user
RUN useradd -m appuser

# Set environment variables for uv to use a specific venv location
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies into /opt/venv
RUN uv sync --frozen --no-install-project

# Copy the rest of the code
COPY . .

# Ensure proper ownership
RUN chown -R appuser:appuser /app /opt/venv

# Switch to non-root user
USER appuser

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

# Expose port
EXPOSE 8000

# Start server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
