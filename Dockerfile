FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
LABEL maintainer="Samuel Stegmeyer<samuel_stegmeyer@posteo.com>"

# Env vars
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

# Install pip and pipenv
RUN python -m pip install --upgrade pip \
    && pip install 'poetry==1.0.5'

# Install dependencies
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi \
    && pip uninstall --yes poetry

EXPOSE 5000

# Copy the data to image
COPY ./app /app
COPY ./.env_prod .env
WORKDIR /app
ENV PYTHONPATH=/app

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "5000", "--lifespan", "on", "shit_head:app"]