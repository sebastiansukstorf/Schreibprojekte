#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Verwendung: $0 ZUSTANDSDATEI" >&2
  exit 64
fi

STATE_FILE="$1"
if [[ ! -f "$STATE_FILE" ]]; then
  echo "Kein aktiver Lektoratsstand: $STATE_FILE"
  exit 0
fi

set -a
source "$STATE_FILE"
set +a

: "${PROJECT:?PROJECT fehlt in der Zustandsdatei}"
: "${CONFIG:?CONFIG fehlt in der Zustandsdatei}"
: "${REVISION:?REVISION fehlt in der Zustandsdatei}"
NEXT_REVISION="${NEXT_REVISION:-$REVISION}"
ACTION="${ACTION:-auto}"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
MANUSKRIPT="$SCRIPT_DIR/../.venv/bin/manuskript"
REVISION_DIR="$PROJECT/lektorat/ueberarbeitungen/$REVISION"
LATEST_MANIFEST="$(find "$REVISION_DIR" -mindepth 2 -maxdepth 2 -type f -name manifest.json -print 2>/dev/null | sort | tail -n 1 || true)"

if [[ "$ACTION" != "start" && -n "$LATEST_MANIFEST" ]] && grep -q '"status": "complete"' "$LATEST_MANIFEST"; then
  echo "Lektoratsstand $REVISION ist bereits vollständig."
  rm -f -- "$STATE_FILE"
  exit 0
fi

if [[ "$ACTION" == "start" ]]; then
  MODE="start"
  ARGS=(--revision "$REVISION" --next-revision "$NEXT_REVISION")
elif [[ -n "$LATEST_MANIFEST" ]]; then
  MODE="resume"
  ARGS=(--resume "$REVISION")
else
  MODE="start"
  ARGS=(--revision "$REVISION" --next-revision "$NEXT_REVISION")
fi

echo "Automatischer Lektoratslauf: $MODE · Stand $REVISION · Projekt $PROJECT"
set +e
"$MANUSKRIPT" lektorat-nacht "$PROJECT" --config "$CONFIG" "${ARGS[@]}"
RESULT=$?
set -e

if [[ $RESULT -eq 0 ]]; then
  rm -f -- "$STATE_FILE"
  echo "Lektoratsstand $REVISION vollständig; aktiver Zustand entfernt."
fi
exit "$RESULT"
