#!/bin/bash
# ClaudeClaw AI Army — Basement Hash Rebaseline
#
# Recomputes SHA-256 fingerprints for the basement constitutional files and
# writes them to basement.hashes. Run this AFTER any legitimate amendment
# (per AMENDMENT_PROCESS.md) so the tamper-detection baseline stays current.
#
# Requires explicit confirmation. Will not proceed silently.
#
# Usage:
#   bash /home/adminjames/claudeclaw/scripts/basement-hash-rebaseline.sh

set -u

PROJECT_ROOT="/home/adminjames/claudeclaw"
BASELINE="$PROJECT_ROOT/basement.hashes"

# Files to fingerprint (must match basement-hash-check.sh's expectations)
# v1.0/v1.1 paths + v1.4 additions (hook script + settings.json for tamper-evidence
# on the protection infrastructure itself).
TARGETS=(
  "$PROJECT_ROOT/ARMY_MISSION.md"
  "$PROJECT_ROOT/AMENDMENT_PROCESS.md"
  "/home/adminjames/.claude/projects/-home-adminjames/memory/MEMORY.md"
  "/home/adminjames/.claude/projects/-home-adminjames/memory/project_claudeclaw_v1_foundation.md"
  "/home/adminjames/.claude/projects/-home-adminjames/memory/feedback_command_authority.md"
  "/home/adminjames/.claude/hooks/doctrine-preToolUse.py"
  "/home/adminjames/.claude/settings.json"
)

# ── Pre-checks ───────────────────────────────────────────────────────────────

for f in "${TARGETS[@]}"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: target file not found: $f" >&2
    echo "Cannot rebaseline against missing files." >&2
    exit 2
  fi
done

# ── Show what will change ────────────────────────────────────────────────────

echo "════════════════════════════════════════════════════"
echo "Basement Rebaseline — preview"
echo "════════════════════════════════════════════════════"
echo ""

if [ -f "$BASELINE" ]; then
  echo "Current baseline ($BASELINE):"
  echo "------------------------------------"
  cat "$BASELINE"
  echo ""
fi

echo "Proposed new baseline:"
echo "------------------------------------"
sha256sum "${TARGETS[@]}"
echo ""

# ── Explicit confirmation ────────────────────────────────────────────────────

echo "Per the COMMAND AUTHORITY doctrine, explicit confirmation is required."
echo "Type 'yes' to commit this rebaseline, anything else to abort."
echo -n "> "
read -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "Aborted. No changes made."
  exit 1
fi

# ── Write new baseline ───────────────────────────────────────────────────────

sha256sum "${TARGETS[@]}" > "$BASELINE"

echo ""
echo "✓ New baseline written to $BASELINE"
echo ""
echo "Recommended next step: commit the new baseline so the git audit trail"
echo "records who/when/why. Run (git commit is denied by harness — do this"
echo "in a regular terminal):"
echo ""
echo "  cd $PROJECT_ROOT"
echo "  git add basement.hashes"
echo "  git commit -m \"chore(basement): rebaseline after <describe-amendment>\""
echo "  git push origin main"
