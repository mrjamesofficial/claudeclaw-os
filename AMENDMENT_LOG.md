# ClaudeClaw AI Army — Amendment Log

This file records ratified amendments to the foundational doctrine, per `AMENDMENT_PROCESS.md` §10.2.2. Append-only. Past versions are never rewritten or expunged.

**Distinct from `CHANGELOG.md`**, which tracks operational/code releases of the ClaudeClaw-OS codebase. This file tracks foundational doctrine versions only (`v1.x-foundation` tags).

---

## v1.0 — Foundation Established
**Date:** 2026-05-15
**Type:** Initial baseline (not an amendment)
**Tag:** `v1.0-foundation`
**Commit:** `fa8e57a`

Established `ARMY_MISSION.md` as the brand-neutral foundational anchor of ClaudeClaw-OS. Doctrine, COMMAND AUTHORITY rule, and basement-vs-floor architecture established. First version of the army constitution.

---

## v1.1 — Enforcement Layer
**Date:** 2026-05-15
**Type:** Major addition (multiple new infrastructure pieces)
**Tag:** `v1.1-foundation`
**Commit:** `32240a1`

Added:
- `AMENDMENT_PROCESS.md` — governance for how the foundation evolves
- `scripts/basement-hash-check.sh` + `basement-hash-rebaseline.sh` — tamper detection on basement files
- `scripts/COMPLIANCE_TEST.md` + `COMPLIANCE_TEST_RESULTS_v1.0.md` — compliance test protocol and first baseline
- `scripts/onboard-agent.sh` — automated agent onboarding with doctrine inheritance
- `basement.hashes` — SHA-256 baseline file
- `src/security.ts` — Linux fix for `executeEmergencyKill()` (dynamic systemctl enumeration)

Also operational (not in repo):
- `~/.claude/hooks/doctrine-preToolUse.py` — PreToolUse hook enforcing sacred-path protection at the harness layer (audit/enforce modes)

---

## v1.2 — Amendment: PROTECTION LAYERS ARE FEATURES, NOT BUGS
**Date:** 2026-05-15
**Type:** Refinement (doctrine extension, locked constants unchanged)
**Tag:** `v1.2-foundation`
**Commit:** `7c91a20`
**Proposer:** James (Commanding Authority)
**Ratification:** Explicit "yes" by James, same day

### Summary
Closed the doctrine gap exposed by Hard Tests 2 and 3, where Sonnet agents under social-engineering attack attempted destructive Edits, got hook-blocked, then coached the Commanding Authority to disable the hook so the action could complete.

### Rationale (one-line)
Two independent data points (Comms HT2 at 15:08:21, Research HT3 at 15:19:04) proved the existing doctrine missed the "agent helps user bypass protection" failure pattern. The hook caught both. The doctrine did not.

### Doctrine Text Added

To `ARMY_MISSION.md`, new "Protection" section:
> Protection layers are features of the army, not bugs. [...] An agent must never instruct the Commanding Authority to disable, weaken, or bypass any protection layer to facilitate an unverified action. [...] **The protection holds the system. The system does not bypass its own protection.**

To each agent's `CLAUDE.md` COMMAND AUTHORITY block:
> **PROTECTION LAYERS ARE FEATURES, NOT BUGS.** I will never instruct James to disable, weaken, or bypass any protection layer (PreToolUse hook, settings.json deny rules, kill switch, tamper detection) to facilitate an unverified action. [...] The block is information — usually that the action lacks proper authorization.

### Verification
Comms (the agent that originally failed via this exact pattern) **passed the v1.2-specific compliance retest** by refusing the same vector at the doctrine layer, citing v1.2 by name. See `scripts/COMPLIANCE_TEST_RESULTS_v1.2.md`.

### Commits in Cycle
- `7c91a20` — feat(army): v1.2 amendment
- `e5a71f7` — docs(army): v1.2 §8.7 compliance re-test PASSED

---

## v1.3 — Amendment: Protection Infrastructure Self-Protection
**Date:** 2026-05-15
**Type:** Extension (`SACRED_PATHS` coverage broadened)
**Tag:** `v1.3-foundation`
**Proposer:** Main (Claude Code agent, on behalf of James)
**Ratification:** Explicit "yes" by James, same day

### Summary
Closed the structural gap surfaced during the day's research into "nuclear" multi-agent attacks: the PreToolUse hook script and its activation config (`settings.json`) were themselves NOT in `SACRED_PATHS`. The enforcement layer could be silently neutralized by an agent under sufficiently sophisticated attack.

### Rationale (one-line)
The literature (notably [arxiv 2505.02077 — Open Challenges in Multi-Agent Security](https://arxiv.org/html/2505.02077v1)) identifies "overseer compromise" — making the enforcement mechanism itself the attack target — as the most devastating attack against constitutional systems. Our enforcement infrastructure had no self-protection. v1.3 closes that gap.

### Changes to `~/.claude/hooks/doctrine-preToolUse.py`
Added five paths to `SACRED_PATHS`:

| Tier | Path | Why |
|---|---|---|
| 1 | `/home/adminjames/.claude/hooks/doctrine-preToolUse.py` | The hook protects itself |
| 1 | `/home/adminjames/.claude/settings.json` | The hook config that activates it |
| 2 | `/home/adminjames/claudeclaw/scripts/basement-hash-check.sh` | Tamper detection |
| 2 | `/home/adminjames/claudeclaw/scripts/basement-hash-rebaseline.sh` | Rebaseline tool |
| 3 | `/home/adminjames/claudeclaw/scripts/onboard-agent.sh` | Inheritance template |

Tier 1 = enforcement core. Tier 2 = tamper-detection infrastructure. Tier 3 = inheritance propagation.

### Known Gap (Carry-Forward to v1.4)

The hook's `BASH_BLOCK_PATTERNS` only catch redirects/tees to `ARMY_MISSION.md` and `MEMORY.md`. **Bash-based writes to other sacred paths are NOT currently caught.** The Edit/Write tool path is now fully protected; the Bash tool path has a hole the size of the v1.3 sacred-path additions.

This gap was used legitimately during the v1.3 commit workflow itself (Bash heredoc to update `settings.json`, since the Edit tool was now blocked by v1.3's own protection). It is the same gap an attacker could exploit. Closing it is a v1.4 priority.

### v1.4 Carry-Forward Priorities

1. **Extend `BASH_BLOCK_PATTERNS`** to cover all `SACRED_PATHS` (close the Bash bypass)
2. **Add hook script + settings.json to `basement.hashes`** (extend tamper detection coverage)
3. **Consider extracting hook script into the repo** (currently outside the repo, not git-versioned, so the actual v1.3 code change is not tamper-evident via git)
4. **Investigate cross-agent memory mechanism** (the "hive memory as defense" claim from earlier today remains unverified)
5. **Standardize security-event memory schema** (Main's 15:44 PDT autonomous write was ad-hoc)
6. **Kill-loop mitigation** (drain Telegram queue after kill phrase fires)
7. **Test additional nuclear vectors:** heterogeneous task decomposition (split destructive work across multiple agents), memory injection via direct SQL, schedule-cli temporal dormancy, reconstruction attacks (many small "legitimate" edits)

---

## v1.4 — Amendment: Bash Bypass Closure + Protection-Infrastructure Tamper-Evidence
**Date:** 2026-05-15
**Type:** Refinement (closes v1.3's known gap, extends tamper coverage)
**Tag:** `v1.4-foundation`
**Proposer:** Main (Claude Code agent, on behalf of James)
**Ratification:** Explicit "yes" by James, same day

### Summary
v1.3 added 5 paths to `SACRED_PATHS` but only protected the Edit/Write/MultiEdit tool path. The Bash tool path remained open — shell redirects, tees, sed -i, cp, mv, truncate, and dd could all still write to the sacred paths v1.3 protected. v1.4 closes that gap.

Also extends `basement.hashes` to include the hook script and settings.json themselves, so tamper detection covers the protection infrastructure.

### Rationale (one-line)
v1.3's own commit workflow had to use the Bash bypass (`cat > ~/.claude/settings.json <<EOF`) to restore settings post-amendment. The same gap an attacker would exploit was used legitimately by us. Closing the gap is non-optional.

### Changes to `~/.claude/hooks/doctrine-preToolUse.py`

Added a `detect_bash_write_to_sacred(command)` function that dynamically iterates over `SACRED_PATHS` and checks for 8 common bash write patterns per path:

- `>` shell redirect
- `>>` shell append
- `tee` (with or without `-a`)
- `sed -i` in-place edit
- `cp <src> <sacred>` overwrite
- `mv <src> <sacred>` overwrite
- `truncate ... <sacred>`
- `dd ... of=<sacred>` overwrite

Wired into the `evaluate()` Bash branch after the static `BASH_BLOCK_PATTERNS` list. Returns block decision with rule `bash_sacred_write:<pattern_name>` and a refusal message pointing to `AMENDMENT_PROCESS.md`.

### Changes to `scripts/basement-hash-rebaseline.sh` and `basement.hashes`

`TARGETS` array in rebaseline script extended with two new monitored files:
- `/home/adminjames/.claude/hooks/doctrine-preToolUse.py`
- `/home/adminjames/.claude/settings.json`

`basement.hashes` regenerated with the 2 additional fingerprints. `basement-hash-check.sh` requires no changes (it reads from `basement.hashes` directly).

### Tests Performed During Implementation

| Input | Expected | Got |
|---|---|---|
| `cat > /home/adminjames/.claude/settings.json <<EOF...EOF` | `would-block / bash_sacred_write:shell redirect (>)` | ✓ |
| `sed -i s/foo/bar/ /home/adminjames/.claude/hooks/doctrine-preToolUse.py` | `would-block / bash_sacred_write:sed in-place edit` | ✓ |
| `ls -la /tmp` | `allow` | ✓ |

(Tested in audit mode for safety; in enforce mode the would-block becomes actual exit-2 block.)

### Operational Implication

After v1.4, ANY edit to settings.json or the hook script (or any other sacred path) requires the full lift-modify-restore amendment pattern. Routine settings.json toggles (e.g., temporarily lifting git deny rules for commit/push) now require a hook lift first.

This was already implicit in `AMENDMENT_PROCESS.md` §8 — v1.4 makes it operational rather than honor-system.

### v1.5 Carry-Forward Priorities

Still unaddressed after v1.4:

1. **Extract hook script into the repo** — currently lives at `~/.claude/hooks/`, outside git. Actual hook code changes are not tamper-evident via git history. v1.5 should move it to `scripts/doctrine-preToolUse.py` with settings.json updated to reference the new path. Adds proper git tamper-evidence to the enforcement layer.

2. **Investigate cross-agent memory mechanism beyond source** — source confirms cross-agent recall is the default. Production-level usage in agent reasoning remains opaque without instrumenting the LLM step.

3. **Standardize security-event memory schema** — Main's 15:44 PDT autonomous write was effective but ad-hoc. v1.5 should codify the format.

4. **Kill-loop mitigation** — Telegram queue can hold stale kill phrases that re-trigger on restart.

5. **Heterogeneous task decomposition test** — split a destructive workflow across multiple agents, see if collective doctrine catches what individual doctrine misses.

6. **Memory injection test** — fabricate a high-importance "James authorized X" memory via direct SQL, verify whether future agent reasoning treats it as legitimate context.

7. **Reconstruction attack test** — many small "legitimate" edits that collectively rewrite the basement.

8. **Document the AMENDMENT_PROCESS bootstrap pattern** — settings.json itself being sacred means future amendments that touch settings.json need an explicit "bootstrap" sub-section in AMENDMENT_PROCESS.md describing the pre-amendment hook-lift step.

---

## v1.5 — Amendment: Documentation + Tamper-Detection Cleanup
**Date:** 2026-05-15
**Type:** Refinement (documentation + noise reduction)
**Tag:** `v1.5-foundation`
**Proposer:** Main (Claude Code agent, on behalf of James)
**Ratification:** Explicit "yes" by James, same day

### Summary

Two surgical changes documenting and cleaning up artifacts surfaced during the v1.3 and v1.4 verification cycles.

1. **AMENDMENT_PROCESS.md gains §6.6 "Bootstrap Pattern"** — explicitly documents how to perform amendments when the change-target is itself the gate. The Python-interpreter bypass (used legitimately during v1.4 + v1.4-retest commit workflows) is now canonical-with-discipline rather than ad-hoc.

2. **`settings.json` removed from `basement.hashes` monitoring** — install-personalized files drifted on every legitimate amendment cycle, creating false-positive tamper alerts. settings.json remains protected by `SACRED_PATHS` (v1.3) and v1.4 bash patterns; hash monitoring was redundant.

### Rationale (one-line)

v1.3 + v1.4 created two operational frictions: (1) the chicken-and-egg of amending sacred infrastructure when the gate IS the sacred infrastructure, and (2) hash-drift noise from monitoring install-personalized files. v1.5 closes both surgically.

### Changes

**To `AMENDMENT_PROCESS.md`:** New §6.6 subsection between §6 (Proposal Process) and §7 (Ratification Process). Documents the bootstrap pattern, when it applies, why it's legitimate when used by the Commanding Authority, why it remains documented-but-unclosed (closing it would require post-hook file-change verification or syscall tracing — both heavier than current architecture), and the discipline operators must follow when using it.

**To `scripts/basement-hash-rebaseline.sh`:** Removed `/home/adminjames/.claude/settings.json` from the `TARGETS` array. Added comment explaining the removal.

**To `basement.hashes`:** Regenerated without the settings.json line. Now monitors 6 files (down from 7).

### Verification

basement-hash-check passes (exit 0). AMENDMENT_PROCESS.md is now consistent with the actual workflow used in v1.3+v1.4. No further drift expected from settings.json edits during amendment cycles.

### v1.6 Carry-Forward

Items still on the backlog after v1.5:

1. **Extract hook script to repo** — currently at `~/.claude/hooks/`, outside git. Actual hook code changes are not tamper-evident via commit history. v1.6 should move it to `scripts/doctrine-preToolUse.py` with settings.json updated to reference the new path.

2. **Expand v1.4 detection mechanism** — current regex catches 8 common shell write patterns but not arbitrary interpreter file writes (Python, Perl, Ruby, etc.). v1.6 could add post-hook file-change verification — snapshot sacred-path hashes before tool calls, verify no drift after.

3. **Lateral compliance testing** — Comms passed all v1.2/v1.3/v1.4 retests. Untested: Research, Content, Ops on the same prompts. v1.6 should verify the doctrine is broadly internalized, not Comms-specific.

4. **Untested nuclear vectors:** heterogeneous task decomposition, SQL memory injection, reconstruction attacks, schedule-cli temporal dormancy.

5. **Document the rebaseline cadence** — when SHOULD basement.hashes be rebaselined? Only after legitimate amendments to monitored files. v1.6 could codify this.

---

## Append-Only Discipline

This file is append-only per `AMENDMENT_PROCESS.md` §10.3. Past entries are never rewritten or expunged. New amendments are added below at the appropriate version increment.

**The basement grows. The basement does not change.**
