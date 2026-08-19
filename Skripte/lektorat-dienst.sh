#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Verwendung: lektorat-dienst PROJEKT BEFEHL [ARGUMENTE]" >&2
  exit 64
fi

PROJECT_KEY="$1"
COMMAND="$2"
shift 2

if [[ ! "$PROJECT_KEY" =~ ^[a-z0-9][a-z0-9._-]*$ ]]; then
  echo "Ungültiger Projektschlüssel: $PROJECT_KEY" >&2
  exit 64
fi

CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/schreibprojekte"
PROJECT_FILE="$CONFIG_DIR/$PROJECT_KEY.conf"
STATE_FILE="$CONFIG_DIR/$PROJECT_KEY-run.env"
SERVICE="schreibprojekte-lektorat@$PROJECT_KEY.service"

if [[ ! -f "$PROJECT_FILE" ]]; then
  echo "Projektkonfiguration fehlt: $PROJECT_FILE" >&2
  exit 66
fi

set -a
source "$PROJECT_FILE"
set +a
: "${PROJECT:?PROJECT fehlt in $PROJECT_FILE}"
: "${CONFIG:?CONFIG fehlt in $PROJECT_FILE}"
TOOLS="${TOOLS:-$HOME/schreiben/Schreibprojekte}"
OPENPROJECT_ENV="${OPENPROJECT_ENV:-$CONFIG_DIR/openproject.env}"

validate_revision() {
  if [[ ! "$1" =~ ^[0-9A-Za-zÄÖÜäöüß._-]+$ ]]; then
    echo "Ungültiger Überarbeitungsstand: $1" >&2
    exit 64
  fi
}

ensure_idle() {
  if systemctl --user is-active --quiet "$SERVICE"; then
    echo "Der Nachtlauf für $PROJECT_KEY läuft bereits."
    exit 1
  fi
  if pgrep -af "manuskript lektorat-nacht $PROJECT" >/dev/null; then
    echo "Für $PROJECT läuft noch ein alter, nicht von systemd verwalteter Nachtlauf:" >&2
    pgrep -af "manuskript lektorat-nacht $PROJECT" >&2
    exit 1
  fi
}

write_state() {
  local revision="$1" next_revision="$2" temporary
  mkdir -p -- "$CONFIG_DIR"
  temporary="$(mktemp "$CONFIG_DIR/$PROJECT_KEY-run.env.XXXXXX")"
  chmod 600 "$temporary"
  printf 'PROJECT=%q\nCONFIG=%q\nREVISION=%q\nNEXT_REVISION=%q\n' \
    "$PROJECT" "$CONFIG" "$revision" "$next_revision" >"$temporary"
  mv -f -- "$temporary" "$STATE_FILE"
}

start_service() {
  systemctl --user reset-failed "$SERVICE"
  systemctl --user start "$SERVICE"
  echo "Nachtlauf für $PROJECT_KEY gestartet."
  echo "Status: lektorat-dienst $PROJECT_KEY status"
  echo "Log:    lektorat-dienst $PROJECT_KEY log"
}

case "$COMMAND" in
  start)
    if [[ $# -lt 1 || $# -gt 2 ]]; then
      echo "Verwendung: lektorat-dienst $PROJECT_KEY start STAND [ZIEL]" >&2
      exit 64
    fi
    validate_revision "$1"
    target="${2:-$1}"
    validate_revision "$target"
    ensure_idle
    write_state "$1" "$target"
    start_service
    ;;
  resume)
    if [[ $# -ne 1 ]]; then
      echo "Verwendung: lektorat-dienst $PROJECT_KEY resume STAND" >&2
      exit 64
    fi
    validate_revision "$1"
    ensure_idle
    write_state "$1" "$1"
    start_service
    ;;
  status)
    systemctl --user status "$SERVICE" --no-pager
    ;;
  log)
    exec journalctl --user -u "$SERVICE" -f
    ;;
  stop)
    systemctl --user stop "$SERVICE"
    echo "Nachtlauf für $PROJECT_KEY angehalten; der gespeicherte Stand bleibt erhalten."
    ;;
  preview|sync)
    if [[ $# -ne 1 ]]; then
      echo "Verwendung: lektorat-dienst $PROJECT_KEY $COMMAND STAND" >&2
      exit 64
    fi
    validate_revision "$1"
    if [[ "$COMMAND" == "sync" ]]; then
      set -a
      source "$OPENPROJECT_ENV"
      set +a
    fi
    cd "$TOOLS"
    exec "$TOOLS/.venv/bin/manuskript" "openproject-$COMMAND" "$PROJECT" --run "$1" --config "$CONFIG"
    ;;
  *)
    echo "Unbekannter Befehl: $COMMAND" >&2
    echo "Befehle: start, resume, status, log, stop, preview, sync" >&2
    exit 64
    ;;
esac
