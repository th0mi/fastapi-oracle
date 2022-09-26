#!/bin/bash
set -e

$HOME/.local/bin/poetry run dotenv run pytest -m database tests

set +e
