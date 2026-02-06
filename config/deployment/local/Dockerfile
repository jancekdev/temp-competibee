# define an alias for the specific python version used in this file.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS python

# Python build stage
FROM python AS python-build-stage

ARG APP_HOME=/app

WORKDIR ${APP_HOME}

# we need to move the virtualenv outside of the $APP_HOME directory because it will be overriden by the docker compose mount
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0 UV_HTTP_TIMEOUT=300

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg dependencies
  libpq-dev \
  gettext \
  curl \
  wait-for-it \
  && rm -rf /var/lib/apt/lists/*





# Requirements are installed here to ensure they will be cached.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock:rw \
    uv sync --no-install-project

COPY . ${APP_HOME}

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock:rw \
    uv sync

RUN rm -rf /root/.cache/uv


# Runtime stage
FROM python AS python-run-stage

ARG APP_HOME=/app

WORKDIR ${APP_HOME}

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0 UV_HTTP_TIMEOUT=300

# Install only runtime dependencies
RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev gettext wait-for-it sudo git bash-completion nano ssh && rm -rf /var/lib/apt/lists/*



COPY --from=python-build-stage ${APP_HOME}/.venv ${APP_HOME}/.venv

# devcontainer dependencies and utils
RUN groupadd --gid 1000 dev-user \
  && useradd --uid 1000 --gid dev-user --shell /bin/bash --create-home dev-user \
  && echo dev-user ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/dev-user \
  && chmod 0440 /etc/sudoers.d/dev-user

# Give dev-user ownership of the frontend directory
RUN chown -R dev-user:dev-user ${APP_HOME}/frontend/react || true
RUN chown -R dev-user:dev-user ${APP_HOME}/.venv || true
RUN chown -R dev-user:dev-user ${APP_HOME}/.cache || true



ENV PATH="/${APP_HOME}/.venv/bin:$PATH"
ENV PYTHONPATH="${APP_HOME}/.venv/lib/python3.12/site-packages:$PYTHONPATH"
ENV PYTHONDONTWRITEBYTECODE=1

COPY ./config/deployment/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./config/deployment/local/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start


COPY ./config/deployment/local/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./config/deployment/local/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./config/deployment/local/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower


ENTRYPOINT ["/entrypoint"]
