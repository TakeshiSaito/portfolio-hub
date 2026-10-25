#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p reports

uv run pytest \
    --junitxml=reports/junit.xml \
    --cov=portfolio_hub \
    --cov-report=term-missing \
    --cov-report=xml:reports/coverage.xml \
    --cov-report=html:reports/htmlcov \
    --cov-fail-under=70 \
    "$@"
