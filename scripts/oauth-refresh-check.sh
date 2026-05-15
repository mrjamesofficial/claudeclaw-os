#!/bin/bash
# One-shot check: did claudeclaw-oauth-refresh.service fire at 04:45 PDT?
# Pipes result to Telegram via notify.sh.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

STATUS=$(systemctl --user show claudeclaw-oauth-refresh.service \
  --property=ActiveState,Result,ExecMainStatus,ExecMainExitTimestamp \
  --no-pager)

TIMER=$(systemctl --user show claudeclaw-oauth-refresh.timer \
  --property=LastTriggerUSec,NextElapseUSecRealtime \
  --no-pager)

MSG="🔑 OAuth refresh check (04:50 PDT)

<b>Service</b>
${STATUS}

<b>Timer</b>
${TIMER}"

"$SCRIPT_DIR/notify.sh" "$MSG"
