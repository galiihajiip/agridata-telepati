#!/bin/bash
# Convenience helper for auto_commit_daemon.py
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_EXEC="python3"

case "$1" in
  start)
    $PYTHON_EXEC "$SCRIPT_DIR/auto_commit_daemon.py" --start
    ;;
  stop)
    $PYTHON_EXEC "$SCRIPT_DIR/auto_commit_daemon.py" --stop
    ;;
  status)
    $PYTHON_EXEC "$SCRIPT_DIR/auto_commit_daemon.py" --status
    ;;
  run-once)
    $PYTHON_EXEC "$SCRIPT_DIR/auto_commit_daemon.py" --run-once
    ;;
  logs)
    tail -n 25 -f "$SCRIPT_DIR/../auto_commit.log"
    ;;
  *)
    echo "Usage: ./scripts/auto_commit.sh {start|stop|status|run-once|logs}"
    exit 1
    ;;
esac
