# Changelog

All notable changes to ClaudeClaw will be documented here.

## [v2.0.1-foundation] - 2026-05-17

### Changed
- `scripts/agent-claude-md.template` updated to v2.0-Hardened doctrine block. Phase 2 agents (KPI, Banking, Accounting, Legal) now inherit v2.0 doctrine from boot 0 — prevents v1.x softness drift via onboarding (per Locked Constant #8 No-Softening Clause).
- `basement.hashes` rebaselined for new template hash: `cca9b0816ac6bb26e37956e12286c84e0b3270d5601a7a07e4e9fd85a17a447a`

### Execution

Via AMENDMENT_PROCESS.md §6.6 Bootstrap Pattern: hook lift (enforce → audit) → template write → hook restore (audit → enforce) → rebaseline → verify exit 0. Bootstrap discipline maintained (immediate restore within same authorization cycle).

### Ratification

- `approved msg:template-v2.0-update @16:55 phrase:"hold the perimeter"`

### Validation

`basement-hash-check.sh` exit 0 PASS post-rebaseline. Onboarding validation pending (run `scripts/onboard-agent.sh` for KPI to verify v2.0 inheritance).

---

## [v2.0-foundation] - 2026-05-17

### BREAKING — Re-founding

Full doctrine re-founding per v1.x AMENDMENT_PROCESS.md §3 (Locked Constants composition changed). v1.x text scrubbed; v2.0-Hardened (Path A Reconciled) replaces `ARMY_MISSION.md`, `AMENDMENT_PROCESS.md`, and all 5 agent `CLAUDE.md` doctrine blocks. See `AMENDMENT_LOG.md` v2.0 entry for full detail.

### Added — Doctrine

- AI-ARMY Doctrine v2.0-Hardened (globally brand-neutral title; no vendor/platform monikers)
- 5 pillars (Quality, Integrity, Family, Respect and Honor, **Loyalty** — new)
- Named Successor: **MrJames** (30-day unreachability trigger per §3.2/§9.6)
- Reading II consent syntax: `<consent_word> msg:<id> @<HH:MM>` mandatory for Tier 2/3
- §3.1.2 Token Expiration Lock (120s)
- §3.6 Scope Discipline
- §4.2 Multi-Model Fail-Secure
- §4.3 No Self-Disarm (formalized v1.2 doctrine into hardened clause)
- §5.7-5.9 attack vectors (Reconstruction, Silent Doctrine Injection, Semantic Inversion Veto)
- §9.7.1 Hardware TOTP (transitional: verbal phrase signature)
- §10.5 Layer Integrity Check (4 enforcement layers, fail-closed)
- §11.9 Doctrinal KPIs (Protocol Compliance Rate, Resource Efficiency, Peer Attestation Sync)
- §12.1.1 Memory Tainting
- §12.6 Cryptographic Peer Attestation
- 8 Locked Constants (up from 5), including **#8 No-Softening Clause** — relaxation requires hard fork

### Added — Process

- AMENDMENT_PROCESS.md §6 Pre-Flight Cross-Document Sync Mandate (basement + CLAUDE.md paired diffs)
- AMENDMENT_PROCESS.md §7.2 Verbal Phrase Lifecycle
- AMENDMENT_PROCESS.md §8 Rebaseline-First implementation pipeline
- `basement.delegations` (access control ledger, JSON, James + MrJames)
- §13-15 RESERVED placeholders (Banking, Accounting, Legal — populated via amendment per §1.2)

### Changed

- "ClaudeClaw AI Army Doctrine" → "AI-ARMY Doctrine"
- §16 Cross-Layer Coordination permanently removed; §16 now = Amendment Layer
- All 5 CLAUDE.md doctrine blocks updated (top-level main + research/comms/content/ops)
- `basement.hashes` rebaselined for v2.0 doctrine files

### Aspirational (build pending in v2.0.1+)

Hardware TOTP infrastructure, `chattr +i` enforcement (needs sudo grant), KPI live telemetry, multi-model fallback wrapper, peer attestation publish/verify, memory tainting filters, token expiration parser middleware, AppArmor/seccomp profiles, `scripts/agent-claude-md.template` v2.0 update, `basement.hashes` TARGETS expansion, `legislative_archive.db` schema + historical migration.

### Ratification Audit Trail

- Phase B: `approved msg:stage-phase-b @16:17`
- Phase D (Tier 3): `approved msg:deploy-basement-v2.0 @16:35 phrase:"hold the perimeter"`
- Phase E (Tier 3): `approved msg:execute-phase-e @16:38 phrase:"hold the perimeter"`

### Backup

v1.8 pre-deployment basement state preserved at `~/.claudeclaw-backups/v1.8-pre-v2.0/` (13 files, 144K).

---

## [unreleased] - 2026-05-01

### Fixed — agent file-send awareness
- New agents created via the dashboard wizard now always include the
  `[SEND_FILE:...]` / `[SEND_PHOTO:...]` marker documentation in their
  CLAUDE.md, regardless of which template the user picked. The plumbing
  in `src/bot.ts:637` (`extractFileMarkers`) has always supported these
  for every agent — newly-created agents just didn't know the syntax
  existed and would say things like "I can't send files" when asked to
  attach an image they'd just generated.
- **Action required for existing agents:** after pulling this commit,
  run `bash scripts/upgrade-agent-claude-md.sh` once. It idempotently
  appends the section to any `agents/<id>/CLAUDE.md` (in either the
  repo or `$CLAUDECLAW_CONFIG`) that doesn't already mention
  `SEND_FILE`/`SEND_PHOTO`. Safe to re-run; skips already-patched
  files. Agents pick up the change on their next turn — no restart
  needed.

## [unreleased] - 2026-04-29

### Added — text war room
- Multi-agent text war room (`/warroom/text`) with real-time SSE streaming, sticky-addressee follow-ups, `/standup`, `/discuss`, ack short-circuit, and per-meeting persistence.
- Tool-call disclosure UX in agent bubbles — collapsed by default (`▸ N tool calls`), click to expand for full args + results.
- Prompt-injection delimiters wrapping every retrieved-from-DB block in war-room prompt assembly.

### Added — security hardening
- Centralized kill switches with `requireEnabled()` enforced at every LLM-spawning boundary (`runAgent`, war-room orchestrator, router, gate, voice bridge, Gemini `generateContent`). Refusal counters surfaced via `/api/health.killSwitchRefusals`.
- Single dashboard mutation middleware that returns 503 on every non-GET when `DASHBOARD_MUTATIONS_ENABLED=false`. Replaces scattered per-route checks.
- War-room tool boundary: default-deny side-effect tools (`Bash`, `Write`, `Edit`, `Skill`, all MCPs) unless agent explicitly opts in via `warroom_tools:` in `agent.yaml`. `permissionMode: 'default'` (no bypass). Per-turn 8-tool budget. Audit log writes for every tool call.
- CSRF middleware rejects cross-origin mutating requests outside the allowlist (`localhost`, configured `DASHBOARD_URL`).
- Response headers: `Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Cache-Control: no-store` on `/api/`.
- Least-privilege SDK env scrubbing (`getScrubbedSdkEnv()`) drops `DASHBOARD_TOKEN`, third-party API keys, and pattern-matched secret-shaped vars before subprocess inheritance.
- Default bind address `127.0.0.1` (was `0.0.0.0`); `DASHBOARD_BIND` env opt-in for LAN exposure.
- Pre-migration backups written to `store/claudeclaw.db.pre-<version>.bak` with `chmod 0600`, 3-backup rotation, gitignored.

### Added — ops & reliability
- Memory ingestion swapped from Gemini to Claude Haiku via OAuth (no extra API key); Gemini retained as fallback. Quota-aware backoff (5-min cooldown on 429).
- `pruneWarRoomMeetings(retentionDays=90)` integrated into the daily decay sweep.
- `endTextMeeting` now clears SDK sessions tied to the meeting.
- `/api/warroom/voices/apply` 3s cooldown to prevent respawn-storm during voice config edits.
- Voice war room `agent_error` and `hand_down` RTVI frames on OAuth/timeout/bridge failures so the browser surfaces real reasons instead of vague Gemini stutter.

### Added — observability
- `/api/health` exposes `killSwitches`, `killSwitchRefusals`, `memoryIngestion`, `warroom.textOpenMeetings`.
- Audit log writes for every war-room tool call (table existed; now populated).
- Router classifier logs elapsed_ms + outcome (success / parse_failure / timeout_or_error) on every call.

### Tests
- `warroom-text-events.test.ts` (MeetingChannel + finalizedTurns guard).
- `warroom-text-db.test.ts` (saveWarRoomConversationTurn idempotency, multi-agent dedup, memory strict-agent isolation, retention prune).
- `kill-switches.test.ts` extended with `requireEnabled` + refusal-counter coverage.
- All 368+ tests pass.

### Docs
- `docs/release-smoke.md` — release runbook (10-step).
- `docs/incident-runbook.md` — kill switch playbook with symptom → action mapping.
- `docs/warroom-mcp-policy.md` — per-agent tool/MCP allowlist + opt-in via `agent.yaml`.
- `docs/redteam-results.md` — adversarial test results (5/5 PASS).
- `docs/voice-smoke-results.md` — voice fix verification.
- `scripts/audit-profile.sh` — isolated red-team harness with canary `.env`, fail-closed gates.
- `scripts/pre-commit-check.sh` — personal-reference scrub.

### Closes Codex adversarial review high findings
- LLM kill switch now enforced at every boundary, not just one route.
- Dashboard mutation kill switch enforced via single middleware on all non-GET routes.
- War-room tool authority restricted to per-agent allowlist; `permissionMode: 'bypassPermissions'` removed from war-room calls.

## [v1.1.1] - 2026-03-06

### Added
- Migration system with versioned migration files
- `add-migration` Claude skill for scaffolding new versioned migrations
