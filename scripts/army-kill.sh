#!/bin/bash
# ClaudeClaw AI Army — Emergency Kill Switch
#
# Immediately stops all 5 agent services. Use when you need a full lockdown
# from the command line (independent of the Telegram kill phrase, which
# currently has a Linux service-naming bug — to be fixed in v1.1).
#
# Usage:  bash /home/adminjames/claudeclaw/scripts/army-kill.sh
# Restart with:  systemctl --user start claudeclaw.service claudeclaw-research.service \
#                  claudeclaw-comms.service claudeclaw-content.service claudeclaw-ops.service

set -u

SERVICES=(
  claudeclaw.service
  claudeclaw-research.service
  claudeclaw-comms.service
  claudeclaw-content.service
  claudeclaw-ops.service
)

echo "ClaudeClaw AI Army — emergency stop initiated $(date)"

systemctl --user stop "${SERVICES[@]}"

echo ""
echo "Status after stop:"
for svc in "${SERVICES[@]}"; do
  state=$(systemctl --user is-active "$svc" 2>/dev/null)
  printf "  %-35s %s\n" "$svc" "$state"
done

# Send Telegram alert via notify.sh if available (best-effort, non-blocking)
NOTIFY="/home/adminjames/claudeclaw/scripts/notify.sh"
if [ -x "$NOTIFY" ]; then
  "$NOTIFY" "🛑 ClaudeClaw AI Army — emergency stop executed at $(date '+%Y-%m-%d %H:%M:%S %Z'). All 5 agents halted." >/dev/null 2>&1 || true
fi

echo ""
echo "Army stopped. To restart, run:"
echo "  systemctl --user start ${SERVICES[*]}"
