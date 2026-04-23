#!/usr/bin/env bash
set -euo pipefail
DATE="${1:?Usage: run_datapipe_daily.sh YYYY-MM-DD}"
python -m datapipe.cli daily --date "$DATE"
