# Image for dependencies
FROM python:3.13.3 AS dependencies
WORKDIR /code
RUN --mount=target=/code \
    pip install --no-cache-dir -r whoshome/requirements.txt

# Image for linting
FROM dependencies AS lint
RUN --mount=target=/code,rw \
    python3 -m pip install mypy black isort pylint && \
    mkdir .mypy_cache && \
    pylint whoshome --disable=R,C,W0511,W3101,W0719,duplicate-code && \
    mypy --ignore-missing-imports --show-column-numbers --install-types --non-interactive whoshome && \
    black --check --diff whoshome && \
    isort --check --diff whoshome

# Image for code itself
FROM dependencies
WORKDIR /code
COPY whoshome /code/whoshome
