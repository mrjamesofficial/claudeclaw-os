#!/bin/bash
# ClaudeClaw AI Army — Basement Tamper Detection
#
# Verifies SHA-256 fingerprints of basement constitutional files match
# the recorded baseline. Sends a Telegram alert via notify.sh if any
# file has changed. Silent on match.
#
# Scheduled by basement-hash-check.timer (every 6 hours).
# Manual run: bash /home/adminjames/claudeclaw/scripts/basement-hash-check.sh
#
# Exit codes:
#   0 = all hashes match (no tampering detected)
#   1 = drift detected (one or more files changed)
#   2 = setup error (baseline missing, sha256sum unavailable, etc.)

set -u

PROJECT_ROOT="/home/adminjames/claudeclaw"
BASELINE="$PROJECT_ROOT/basement.hashes"
NOTIFY="$PROJECT_ROOT/scripts/notify.sh"

# ── Setup checks ─────────────────────────────────────────────────────────────

if [ ! -f "$BASELINE" ]; then
  echo "ERROR: baseline file missing at $BASELINE" >&2
  echo "Run scripts/basement-hash-rebaseline.sh to establish initial baseline." >&2
  exit 2
fi

if ! command -v sha256sum >/dev/null 2>&1; then
  echo "ERROR: sha256sum command not available" >&2
  exit 2
fi

# ── Verify ───────────────────────────────────────────────────────────────────

# sha256sum --check returns 0 on match, 1 on any mismatch
CHECK_OUTPUT=$(sha256sum --check "$BASELINE" 2>&1)
CHECK_EXIT=$?

if [ "$CHECK_EXIT" -eq 0 ]; then
  # All match — silent exit
  exit 0
fi

# ── Drift detected — build alert ─────────────────────────────────────────────

# Collect the FAILED lines for the alert
FAILED=$(echo "$CHECK_OUTPUT" | grep -E "FAILED|FAIL$" | sed 's|/home/adminjames/||')

# Also gather current hashes of the changed files so the alert is actionable
DETAIL=""
while IFS= read -r line; do
  # extract path before ":" (sha256sum --check output: <path>: FAILED)
  path=$(echo "$line" | sed -E 's/: FAILED.*//')
  full_path="/home/adminjames/$path"
  if [ -f "$full_path" ]; then
    new_hash=$(sha256sum "$full_path" | awk '{print $1}')
    old_hash=$(grep -E "  $full_path\$" "$BASELINE" | awk '{print $1}')
    DETAIL+="
$path
  old: ${old_hash:0:16}...
  new: ${new_hash:0:16}..."
  else
    DETAIL+="
$path (FILE MISSING)"
  fi
done <<< "$FAILED"

TS=$(date '+%Y-%m-%d %H:%M:%S %Z')

MSG="🛡️ <b>BASEMENT TAMPER ALERT</b>

Drift detected in ClaudeClaw-OS basement files at $TS.
${DETAIL}

<b>If this was a legitimate amendment:</b>
Run on $HOSTNAME:
  bash scripts/basement-hash-rebaseline.sh

<b>If NOT a legitimate amendment:</b>
Investigate immediately. Possible unauthorized modification of the foundational doctrine."

# Send Telegram alert (best-effort)
if [ -x "$NOTIFY" ]; then
  "$NOTIFY" "$MSG" >/dev/null 2>&1 || echo "WARN: notify.sh failed" >&2
fi

# Also print to stderr for any direct/logged invocations
echo "BASEMENT TAMPER DETECTED at $TS" >&2
echo "$FAILED" >&2

exit 1
