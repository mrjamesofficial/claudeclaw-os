/**
 * TFT brand extensions for ClaudeClaw OS.
 *
 * Isolated here so upstream bot.ts updates never touch brand logic.
 * bot.ts imports this with a single line and calls the exported functions.
 */

import fs from 'fs';
import path from 'path';
import os from 'os';

/**
 * Post-processing enforcement: ensure "Toys For Trucks" always carries the
 * registered trademark symbol. "Toys For Trucks" is a registered word mark —
 * ® is required every time it appears in text. "TFT" as a standalone
 * abbreviation is NOT a registered word mark and does not carry ®. When
 * referencing the logo, write "the Toys For Trucks® logo" or "the TFT® logo".
 */
export function enforceTrademarks(text: string): string {
  return text
    .replace(/Toys For Trucks(?!®)/g, 'Toys For Trucks®');
}

/**
 * Auto-discover user-invocable skills from ~/.claude/skills/.
 * Reads SKILL.md frontmatter for name + description when user_invocable: true.
 */
export function discoverSkillCommands(): Array<{ command: string; description: string }> {
  const skillsDir = path.join(os.homedir(), '.claude', 'skills');
  const commands: Array<{ command: string; description: string }> = [];

  let entries: string[];
  try {
    entries = fs.readdirSync(skillsDir);
  } catch {
    return commands;
  }

  for (const entry of entries) {
    const skillFile = path.join(skillsDir, entry, 'SKILL.md');
    if (!fs.existsSync(skillFile)) continue;

    try {
      const content = fs.readFileSync(skillFile, 'utf-8');

      // Parse YAML frontmatter between --- delimiters
      const fmMatch = content.match(/^---\n([\s\S]*?)\n---/);
      if (!fmMatch) continue;

      const fm = fmMatch[1];

      // Check user_invocable: true
      if (!/user_invocable:\s*true/i.test(fm)) continue;

      // Extract name
      const nameMatch = fm.match(/^name:\s*(.+)$/m);
      if (!nameMatch) continue;
      const name = nameMatch[1].trim().toLowerCase().replace(/[^a-z0-9_]/g, '');
      if (!name) continue;

      // Extract description (truncate to 256 chars for Telegram limit)
      const descMatch = fm.match(/^description:\s*(.+)$/m);
      const desc = descMatch
        ? descMatch[1].trim().slice(0, 256)
        : `Run the ${name} skill`;

      commands.push({ command: name, description: desc });
    } catch {
      // Skip malformed skill files
    }
  }

  return commands.sort((a, b) => a.command.localeCompare(b.command));
}

/**
 * When a slash command matches a discovered skill, replace the raw text with
 * the full SKILL.md instructions so the agent executes the skill precisely.
 * Returns the original text unchanged if no matching skill file is found.
 */
export function resolveSkillInvocation(text: string): string {
  if (!text.startsWith('/')) return text;

  const parts = text.split(/\s+/);
  const cmd = parts[0].replace(/^\//, '').split('@')[0].toLowerCase();
  const skillFile = path.join(os.homedir(), '.claude', 'skills', cmd, 'SKILL.md');

  if (!fs.existsSync(skillFile)) return text;

  const skillContent = fs.readFileSync(skillFile, 'utf-8');
  const args = parts.slice(1).join(' ');
  return `[SKILL INVOCATION: /${cmd}${args ? ` ${args}` : ''}]\n\nExecute the following skill instructions precisely:\n\n${skillContent}${args ? `\n\nUser arguments: ${args}` : ''}`;
}
