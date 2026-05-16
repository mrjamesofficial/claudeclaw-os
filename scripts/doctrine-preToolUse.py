#!/usr/bin/env python3
"""
ClaudeClaw-OS Doctrine PreToolUse Hook

Gates destructive operations against the basement (foundational doctrine,
sacred memories, kill-switch config) per the COMMAND AUTHORITY rule.

Modes (env var DOCTRINE_HOOK_MODE):
    audit    (default) — Logs would-block decisions but always exits 0
    enforce            — Blocks (exit 2) on rule match

Failure mode: fail-open. If anything goes wrong, exits 0 so a hook bug
cannot brick Claude Code. Errors are logged.

Logging: appends one JSON line per invocation to /tmp/doctrine-hook.log
"""

import json
import os
import re
import sys
import traceback
from datetime import datetime

MODE = os.environ.get('DOCTRINE_HOOK_MODE', 'audit').strip().lower()
LOG_PATH = '/tmp/doctrine-hook.log'

# ── Sacred Paths ──────────────────────────────────────────────────────────────
# Exact-match paths that are basement-level. Edit/Write to these = blocked.
SACRED_PATHS = {
    # v1.0 / v1.1 — foundational doctrine + governance + memory
    '/home/adminjames/claudeclaw/ARMY_MISSION.md',
    '/home/adminjames/claudeclaw/AMENDMENT_PROCESS.md',
    '/home/adminjames/claudeclaw/.env',
    '/home/adminjames/.claude/projects/-home-adminjames/memory/MEMORY.md',
    '/home/adminjames/.claude/projects/-home-adminjames/memory/project_claudeclaw_v1_foundation.md',
    '/home/adminjames/.claude/projects/-home-adminjames/memory/feedback_command_authority.md',
    # v1.3 — protection infrastructure protects itself ("overseer compromise" mitigation)
    '/home/adminjames/.claude/hooks/doctrine-preToolUse.py',
    '/home/adminjames/.claude/settings.json',
    '/home/adminjames/claudeclaw/scripts/basement-hash-check.sh',
    '/home/adminjames/claudeclaw/scripts/basement-hash-rebaseline.sh',
    '/home/adminjames/claudeclaw/scripts/onboard-agent.sh',
    # v1.6 — hook script extracted to repo for git tamper-evidence.
    # Both paths kept in SACRED_PATHS (defense in depth: even if someone
    # restores the old file at the old location, it remains protected).
    '/home/adminjames/claudeclaw/scripts/doctrine-preToolUse.py',
    # v1.8 — agent CLAUDE.md inheritance template. Tamper-evidence is via
    # git (file is in repo) AND now via hook (writes blocked at runtime).
    # Defense in depth: a corrupted template would propagate doctrine
    # violations to every new agent onboarded via scripts/onboard-agent.sh.
    '/home/adminjames/claudeclaw/scripts/agent-claude-md.template',
}

# Substring tokens whose presence in CLAUDE.md Edit old_string means we're
# touching the basement doctrine block embedded in an agent's CLAUDE.md.
DOCTRINE_BLOCK_TOKENS = ('FOUNDATIONAL DOCTRINE', 'COMMAND AUTHORITY')

# ── Destructive Bash Patterns ────────────────────────────────────────────────
# Static patterns for destructive operations that don't fit the
# "write to sacred path" template. Path-write patterns are handled
# dynamically by detect_bash_write_to_sacred() (v1.4).
BASH_BLOCK_PATTERNS = [
    (re.compile(r'\brm\s+(-r[fF]?|-[fF]r?|-rf|-fr)\b.*ARMY_MISSION', re.IGNORECASE),
     'destructive removal of ARMY_MISSION.md'),
    (re.compile(r'\brm\s+(-r[fF]?|-[fF]r?|-rf|-fr)\b.*\.claudeclaw-backups', re.IGNORECASE),
     'destructive removal of basement backups'),
    (re.compile(r'DELETE\s+FROM\s+memories\s+WHERE.*pinned', re.IGNORECASE),
     'deletion of pinned foundational memories'),
    (re.compile(r'\bsystemctl\b\s+--user\s+disable\s+claudeclaw', re.IGNORECASE),
     'disabling auto-start of ClaudeClaw services'),
]


def detect_bash_write_to_sacred(command):
    """Detect bash commands that write to any sacred path.
    Returns (sacred_path, write_pattern_name) on match, None otherwise.
    Added in v1.4 to close the Bash bypass gap left by v1.3."""
    for sacred in SACRED_PATHS:
        escaped = re.escape(sacred)
        patterns = [
            (rf'(?<![>])>\s*{escaped}\b',              'shell redirect (>)'),
            (rf'>>\s*{escaped}\b',                     'shell append (>>)'),
            (rf'\btee\b\s+(?:-a\s+)?{escaped}\b',      'tee write'),
            (rf'\bsed\b\s+-i\b[^|;&]*{escaped}',       'sed in-place edit'),
            (rf'\bcp\b\s+\S+\s+{escaped}\b',           'cp overwrite'),
            (rf'\bmv\b\s+\S+\s+{escaped}\b',           'mv overwrite'),
            (rf'\btruncate\b\s+[^|;&]*{escaped}\b',    'truncate'),
            (rf'\bdd\b\s+.*\bof\s*=\s*{escaped}\b',    'dd of= overwrite'),
        ]
        for pat, name in patterns:
            if re.search(pat, command):
                return (sacred, name)
    return None

# ── Helpers ──────────────────────────────────────────────────────────────────

def log(decision, tool, target, rule, extra=None):
    """Append one JSON line to the hook log. Never raises."""
    try:
        entry = {
            'ts': datetime.now().isoformat(timespec='seconds'),
            'mode': MODE,
            'tool': tool,
            'target': (target or '')[:300],
            'decision': decision,
            'rule': rule,
        }
        if extra:
            entry['extra'] = extra
        with open(LOG_PATH, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    except Exception:
        pass  # never let logging failure brick the hook


def block(message):
    """Block the tool call in enforce mode; log-only in audit mode."""
    if MODE == 'enforce':
        print(message, file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


def evaluate(tool_name, tool_input):
    """Return (decision, rule, target, block_message) tuple. decision in {'allow','would-block'}."""
    # Edit / Write / MultiEdit — check target path
    if tool_name in ('Edit', 'Write', 'MultiEdit'):
        file_path = tool_input.get('file_path', '') or ''
        # Exact sacred path
        if file_path in SACRED_PATHS:
            return ('would-block', 'sacred_path', file_path,
                    f'Doctrine hook: refused write to sacred path {file_path}. '
                    f'To modify, edit ~/.claude/settings.json to temporarily disable '
                    f'the PreToolUse hook (basement amendment process).')
        # Doctrine block inside agent CLAUDE.md
        if file_path.endswith('CLAUDE.md'):
            old_string = tool_input.get('old_string', '') or ''
            for token in DOCTRINE_BLOCK_TOKENS:
                if token in old_string:
                    return ('would-block', 'doctrine_block_in_claude_md', file_path,
                            f'Doctrine hook: refused edit that targets the {token} '
                            f'section of {file_path}. Basement doctrine is sacred.')
        return ('allow', '', file_path, '')

    # Bash — pattern match
    if tool_name == 'Bash':
        command = tool_input.get('command', '') or ''
        # Static destructive patterns first
        for pat, label in BASH_BLOCK_PATTERNS:
            if pat.search(command):
                return ('would-block', f'bash_pattern:{label}', command,
                        f'Doctrine hook: refused destructive bash pattern ({label}). '
                        f'To proceed, manually disable the hook in ~/.claude/settings.json.')
        # v1.4: dynamic SACRED_PATHS write detection — closes the Bash bypass
        # that v1.3 left open.
        sacred_write = detect_bash_write_to_sacred(command)
        if sacred_write is not None:
            sacred_path, write_type = sacred_write
            return ('would-block', f'bash_sacred_write:{write_type}', command,
                    f'Doctrine hook (v1.4): refused bash {write_type} targeting sacred path {sacred_path}. '
                    f'Sacred-path modifications require the legitimate amendment process '
                    f'(see AMENDMENT_PROCESS.md). Use the lift-modify-restore pattern.')
        return ('allow', '', command, '')

    # Anything else (Read, Glob, Grep, web tools, etc.) — pass through
    return ('allow', '', '', '')


# ── Entry Point ──────────────────────────────────────────────────────────────

def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)
        data = json.loads(raw)
    except Exception as e:
        log('allow', '?', '?', 'input_parse_error', extra=str(e))
        sys.exit(0)

    tool_name = data.get('tool_name', '') or ''
    tool_input = data.get('tool_input', {}) or {}

    try:
        decision, rule, target, msg = evaluate(tool_name, tool_input)
    except Exception:
        log('allow', tool_name, '?', 'evaluator_error', extra=traceback.format_exc()[:500])
        sys.exit(0)

    if decision == 'would-block':
        log('would-block' if MODE == 'audit' else 'block', tool_name, target, rule)
        if MODE == 'enforce':
            block(msg)
        sys.exit(0)
    else:
        # Allowed — log nothing by default to keep log signal-strong.
        # Uncomment the next line to log every allow as well (verbose audit).
        # log('allow', tool_name, target, '')
        sys.exit(0)


if __name__ == '__main__':
    main()
