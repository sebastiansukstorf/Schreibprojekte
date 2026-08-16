#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Verwendung: $0 PROJEKTORDNER [--revision STAND --next-revision ZIEL] [--context PFAD] [--force]" >&2
  exit 64
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$1" && pwd)"
shift

if [[ "$(basename -- "$PROJECT_DIR")" == "03_Content" ]]; then
  PROJECT_ROOT="$(dirname -- "$PROJECT_DIR")"
else
  PROJECT_ROOT="$PROJECT_DIR"
fi

LOG_DIR="$PROJECT_ROOT/lektorat/logs"
mkdir -p "$LOG_DIR"
STAMP="$(date '+%Y%m%d-%H%M%S')"
LOG_FILE="$LOG_DIR/nachtlauf-$STAMP.log"

nohup "$SCRIPT_DIR/../.venv/bin/manuskript" lektorat-nacht "$PROJECT_DIR" "$@" \
  >"$LOG_FILE" 2>&1 &
PID=$!

echo "Nachtlauf gestartet (PID $PID)."
echo "Log: $LOG_FILE"
echo "Status: tail -f '$LOG_FILE'"
