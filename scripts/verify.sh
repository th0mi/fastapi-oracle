#!/bin/bash
set -e

$HOME/.local/bin/poetry run black fastapi_oracle tests --check
$HOME/.local/bin/poetry run isort --check-only fastapi_oracle tests
$HOME/.local/bin/poetry run flake8 fastapi_oracle tests
$HOME/.local/bin/poetry run mypy fastapi_oracle tests

set +e
