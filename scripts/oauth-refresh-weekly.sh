#!/bin/bash
# Weekly summary: last 7 days of claudeclaw-oauth-refresh activity.
# Pipes to Telegram via notify.sh.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SINCE="7 days ago"

# Refresh service runs in the past week.
STARTED=$(journalctl --user -u claudeclaw-oauth-refresh.service \
  --since "$SINCE" --no-pager 2>/dev/null \
  | grep -c "Starting claudeclaw-oauth-refresh.service")

FINISHED=$(journalctl --user -u claudeclaw-oauth-refresh.service \
  --since "$SINCE" --no-pager 2>/dev/null \
  | grep -c "Finished claudeclaw-oauth-refresh.service")

FAILED=$(journalctl --user -u claudeclaw-oauth-refresh.service \
  --since "$SINCE" --no-pager 2>/dev/null \
  | grep -cE "Failed|status=[1-9]")

# Most recent run.
LAST_RUN=$(systemctl --user show claudeclaw-oauth-refresh.timer \
  --property=LastTriggerUSec --value --no-pager)

# Next scheduled run.
NEXT_RUN=$(systemctl --user show claudeclaw-oauth-refresh.timer \
  --property=NextElapseUSecRealtime --value --no-pager)

# OAuth health-check alerts from the 5 agents in the past week.
ALERTS=$(journalctl --user -u 'claudeclaw*' --since "$SINCE" --no-pager 2>/dev/null \
  | grep -iE "oauth.*(expir|alert|fail|error)" \
  | grep -v "OAuth health check initialized" \
  | grep -v "OAuth health check disabled" \
  | wc -l)

MSG="📊 OAuth refresh — weekly summary (last 7d)

<b>Refresh service</b>
Started:  ${STARTED}
Finished: ${FINISHED}
Failed:   ${FAILED}

<b>Timer</b>
Last:  ${LAST_RUN}
Next:  ${NEXT_RUN}

<b>Health-check alerts</b>
Count: ${ALERTS}"

"$SCRIPT_DIR/notify.sh" "$MSG"
