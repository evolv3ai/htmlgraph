#!/bin/bash
#
# HtmlGraph Post-Commit Hook
# Logs Git commit events for agent-agnostic continuity tracking
#
# This hook runs after every git commit and logs the commit
# metadata to HtmlGraph's event stream.

# Exit on any error (but don't block commits)
set +e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT" || exit 0

# Check if HtmlGraph is initialized
if [ ! -d ".htmlgraph" ]; then
    exit 0
fi

# Check if htmlgraph CLI is available
if ! command -v htmlgraph &> /dev/null; then
    # Try python module directly
    if command -v python3 &> /dev/null; then
        python3 -m htmlgraph.git_events commit &> /dev/null &
    fi
    exit 0
fi

# Log the commit event (async, in background)
# This ensures we don't slow down the commit
htmlgraph git-event commit &> /dev/null &

# Always exit successfully (never block commits)
exit 0
