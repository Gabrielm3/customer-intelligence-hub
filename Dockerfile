FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml ./

RUN uv sync --no-dev

COPY src/ ./src/
COPY cli/ ./cli/
COPY database/ ./database/
COPY .env.example ./
COPY .env ./

ENV PYTHONPATH=/app/src

RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uv", "run", "python", "cli/interactive_cli.py"]