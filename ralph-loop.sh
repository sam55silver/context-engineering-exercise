#!/bin/bash
set -euo pipefail

MAX_ITERATIONS="${MAX_ITERATIONS:-20}"
SLEEP_SECONDS="${SLEEP_SECONDS:-2}"

echo "=== Ralph Loop — Watchlist Feature Builder ==="
echo "Max iterations: $MAX_ITERATIONS"
echo ""

iteration=0

while [ "$iteration" -lt "$MAX_ITERATIONS" ]; do
  iteration=$((iteration + 1))
  echo "--- Iteration $iteration / $MAX_ITERATIONS ---"

  # Always reset to repo root to avoid cwd drift from agent cd commands
  cd "$(dirname "$0")"

  # Check for dirty state (interrupted previous iteration)
  if git diff --quiet && git diff --cached --quiet; then
    # Clean tree — pull latest changes
    git pull --rebase --quiet 2>/dev/null || true
  else
    echo "Dirty working tree detected — resuming previous work..."
  fi

  # Check if all tickets are done
  TODO_COUNT=$(grep -c '\[todo\]' tickets.md 2>/dev/null || echo "0")
  IN_PROGRESS_COUNT=$(grep -c '\[in_progress\]' tickets.md 2>/dev/null || echo "0")

  if [ "$TODO_COUNT" = "0" ] && [ "$IN_PROGRESS_COUNT" = "0" ]; then
    echo "All tickets complete. Exiting."
    break
  fi

  echo "Remaining: $TODO_COUNT todo, $IN_PROGRESS_COUNT in progress"

  # Run the agent
  opencode run --agent build "@RALPH.md"

  # Check for RALPH_DONE signal (agent outputs this when finished)
  # If agent crashed, dirty tree check on next iteration handles resume

  sleep "$SLEEP_SECONDS"
done

echo "=== Ralph Loop finished after $iteration iterations ==="
