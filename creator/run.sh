#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -x .venv-creator/bin/python ]]; then
  echo 'First run: follow creator/README.md to install the creator with Python 3.11 or newer.'
  exit 1
fi
exec .venv-creator/bin/python -m streamlit run creator/app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
