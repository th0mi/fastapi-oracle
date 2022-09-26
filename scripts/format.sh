#!/bin/bash
$HOME/.local/bin/poetry run autoflake \
    --remove-all-unused-imports \
    --recursive \
    --remove-unused-variables \
    --in-place \
    fastapi_oracle tests
$HOME/.local/bin/poetry run black fastapi_oracle tests
$HOME/.local/bin/poetry run isort fastapi_oracle tests
