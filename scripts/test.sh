#!/bin/bash
set -e

$HOME/.local/bin/poetry run pytest \
  -m pureunit \
  --cov=. \
  --cov-fail-under=100 \
  --cov-report=xml \
  --junitxml=report.xml \
  tests
$HOME/.local/bin/poetry run coverage xml
xmllint -o report.xml --format report.xml

set +e
