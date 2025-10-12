# builder
FROM python:3.13.8-slim-trixie AS builder

ARG PROJECT_PATH=/app
ARG WHEELS_DIR_PATH=$PROJECT_PATH/wheels

WORKDIR ${PROJECT_PATH}

COPY pyproject.toml poetry.lock ./

RUN DEBIAN_FRONTEND=noninteractive apt-get update -y -q && \
    apt-get install --no-install-recommends -y -q \
            gcc \
            g++ \
            libpq-dev && \
    python -m pip install --no-cache-dir -U pip setuptools wheel poetry poetry-plugin-export && \
    # build wheel archives using the pyproject.toml/poetry.lock files
    poetry export --format requirements.txt --output requirements.txt && \
    python -m pip wheel --no-cache-dir --wheel-dir $WHEELS_DIR_PATH -r requirements.txt --require-hashes

# final
FROM python:3.13.8-slim-trixie AS final

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG USER=admin
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG BUILDER_WHEELS_DIR_PATH=/app/wheels
ARG PROJECT_PATH=/app
ARG WHEELS_DIR_PATH=$PROJECT_PATH/wheels

WORKDIR ${PROJECT_PATH}

RUN --mount=type=bind,from=builder,source=$BUILDER_WHEELS_DIR_PATH,target=$WHEELS_DIR_PATH \
    DEBIAN_FRONTEND=noninteractive apt-get update -y -q && \
    apt-get install --no-install-recommends -y -q \
            curl \
            netcat-traditional \
            libpq-dev && \
    # add new user
    groupadd -g $GROUP_ID $USER && \
    useradd -M -o -l -s /bin/bash -u $USER_ID -g $GROUP_ID $USER && \
    # install python packages
    python -m pip install --no-cache-dir -U pip setuptools wheel && \
    python -m pip install --no-cache-dir $WHEELS_DIR_PATH/* && \
    # cleanup
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --chown=$USER:$USER . ./

USER $USER
