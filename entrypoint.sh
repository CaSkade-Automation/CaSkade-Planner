#!/bin/bash
set -e

echo "Caskade Planner starting..."

case "$1" in
    "rest")
        echo "Starting REST API on port 5000..."
		exec gunicorn -w 2 -b 0.0.0.0:5000 smt_planning.planner_rest:app
		;;
    "cli")
        echo "Starting CLI mode..."
        shift  # Remove 'cli' from arguments
        exec python smt_planning/planner_cli.py "$@"
        ;;
    "plan-from-file")
        echo "Planning from file: ${@:2}"
        exec python smt_planning/planner_cli.py plan-from-file "${@:2}"
        ;;
    "plan-from-endpoint")
        echo "Planning from endpoint: ${@:2}"
        exec python smt_planning/planner_cli.py plan-from-endpoint "${@:2}"
        ;;
    "caskade-planner-cli")
        echo "Direct CLI access..."
        shift  # Remove 'caskade-planner-cli'
        exec python smt_planning/planner_cli.py "$@"
        ;;
    "bash")
        echo "Starting interactive bash..."
        exec /bin/bash
        ;;
    *)
        echo "Usage: $0 {rest|cli|plan-from-file|plan-from-endpoint|bash} [arguments...]"
        echo ""
        echo "Examples:"
        echo "  $0 rest                                           # Start REST API"
        echo "  $0 cli plan-from-file /data/ont.ttl http://cap   # CLI with file"
        echo "  $0 plan-from-file /data/ont.ttl http://cap       # Direct shortcut"
        echo "  $0 plan-from-endpoint http://endpoint http://cap # Direct shortcut"
        echo "  $0 bash                                          # Interactive shell"
        exit 1
        ;;
esac