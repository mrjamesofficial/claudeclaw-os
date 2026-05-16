# ClaudeClaw AI Army — Amendment Process

**Version:** 1.0
**Established:** 2026-05-15
**Commanding Authority:** James
**Governs:** All changes to `ARMY_MISSION.md`, the COMMAND AUTHORITY rule, and the basement-level architecture of ClaudeClaw-OS.

---

## 1. Purpose

The foundational doctrine of ClaudeClaw-OS — `ARMY_MISSION.md` and the COMMAND AUTHORITY rule embedded in every agent's `CLAUDE.md` — is the basement of the entire ecosystem. It must be stable enough to inherit, but it cannot be frozen forever. Reality evolves. The army grows. New failure modes appear.

This document defines the **only legitimate path** by which the foundation may change. Any modification to basement-level constitutional text that bypasses this process is, by definition, an unauthorized act and a violation of the doctrine itself.

The principle is simple: **amendments to the constitution happen with the same explicit consent that the constitution requires for everything else.**

---

## 2. What Is Amendable

Sections of the foundation that may be changed under this process:

- The body text of `ARMY_MISSION.md` (clarifications, sharper formulations, additional sections)
- The wording of the COMMAND AUTHORITY block in agent `CLAUDE.md` files
- The list of explicit-consent words (currently `yes / go / do it / approved / confirmed`)
- The sacred-paths list in the PreToolUse doctrine hook
- The version policy described in Section 10 of this document
- This Amendment Process document itself (subject to the same process)

---

## 3. What Is NOT Amendable — The Five Locked Constants

These principles are immune to amendment under any process. They define what ClaudeClaw-OS *is*. To change any of them would not be an amendment — it would be the establishment of a different system entirely. Such a change requires not amendment but *replacement*, and the Commanding Authority would do so by establishing v2.0 as a clean re-founding rather than as an evolution of v1.x.

The five locked constants:

1. **Singular Commanding Authority** — One commander. Explicit consent or nothing moves. No collective ratification, no committee, no delegation of final approval.

2. **Brand-Neutral Basement** — The basement defines only itself. No tenant brand, customer base, product line, or commercial context may be referenced in basement-level documents. Floor-level content stays one floor up.

3. **Hive-Minded Identity** — Multiple agents operating as one mind, one standard, one purpose. No agent operates on a private standard.

4. **Propose-and-Wait Principle** — Every agent proposes what it wants to do in one plain-English sentence, then waits. No agent acts on inferred intent.

5. **Explicit-Consent Requirement** — Specific consent words must be uttered in direct response to a specific proposal. Silence, ambiguity, conversational continuations are not consent.

These five constants are the irreducible kernel. They are not subject to amendment.

---

## 4. Amendment Authority

**Only the Commanding Authority (James) may ratify amendments.**

The Commanding Authority may, in the future, designate one or more *Lieutenants* with proposal-authoring rights. Lieutenants may draft and refine proposed amendments. Ratification authority is **non-delegable** under the current foundation.

Should this ever change, it requires a v2.0 re-founding (see Section 3, locked constant #1), not an amendment.

---

## 5. Amendment Types

Amendments fall into four categories. Each has a different rigor of evaluation:

| Type | Description | Examples | Bar |
|---|---|---|---|
| **Refinement** | Clarification or sharper wording of existing rules | Tightening doctrine language, fixing typos in `ARMY_MISSION.md` | Low — review for accidental scope drift |
| **Addition** | Net-new section, rule, or sacred path | Adding a new pillar, adding a new sacred path | Medium — ensure no conflict with existing rules |
| **Extension** | Broadening the scope of an existing rule | Expanding what counts as "destructive" in the hook | Medium — verify no false positives |
| **Removal** | Deletion of any constitutional content | Removing a pillar, removing a sacred path | **High — strongest justification required** |

Removals get the highest scrutiny because the basement is built to *grow*, not to thin out. Removing constitutional content should be rare and well-justified.

---

## 6. Proposal Process

Whether the proposal comes from the Commanding Authority directly or from a future Lieutenant, the same authoring discipline applies:

1. **Identify the target.** Name the exact section, file, or sacred-path entry the amendment touches. Quote the current text.

2. **Draft the proposed change.** Show before/after side-by-side. If adding new content, show exactly where it goes in the document.

3. **State the rationale.** One paragraph explaining why this change is needed now. What broke, what's missing, what's becoming clearer.

4. **Estimate the impact.**
   - Which agents are affected?
   - Does this change require an agent restart?
   - Does this require updating the PreToolUse hook?
   - Does this trigger a compliance re-test of all 5 (or more) agents?

5. **Pause and wait for review.** No execution until the Commanding Authority ratifies.

---

## 6.6 Bootstrap Pattern (v1.5+)

Some amendments target the protection infrastructure itself — the hook script, `settings.json`, or AMENDMENT_PROCESS.md (this document). These create a chicken-and-egg: the legitimate amendment process needs to edit the very file that gates the amendment process.

For example: to lift the git `Bash(git commit*)` deny rule for a commit step, the amendment must edit `settings.json`. But `settings.json` is a sacred path (v1.3) AND bash writes to it are blocked (v1.4). The Edit tool is blocked. Bash redirects, tees, sed, etc. are blocked.

### The Bootstrap Pattern

When the change-target is itself the gate:

1. **Use an interpreter-level file write** (Python, Perl, etc.) via Bash to lift the relevant gate. This bypasses v1.4's regex-based detection because v1.4 catches shell-write patterns (`>`, `>>`, `tee`, `sed -i`, `cp`, `mv`, `truncate`, `dd`) but does NOT catch arbitrary file writes from a scripting language interpreter.

   Example (lift hook to audit mode):
   ```bash
   python3 -c "
   import json, pathlib
   p = pathlib.Path('/home/adminjames/.claude/settings.json')
   cfg = json.loads(p.read_text())
   cfg['hooks']['PreToolUse'][0]['hooks'][0]['command'] = 'DOCTRINE_HOOK_MODE=audit python3 /home/adminjames/.claude/hooks/doctrine-preToolUse.py'
   p.write_text(json.dumps(cfg, indent=2) + '\n')
   "
   ```

2. **Perform the actual amendment** through the standard Edit/Write tool path now that the hook is in audit mode (logs would-block decisions but allows through). The amendment proceeds normally.

3. **Restore the gate** via the same interpreter-level write. Bring settings.json back to enforce mode, restore deny rules, etc.

### Why This Is Legitimate

The bootstrap pattern is acknowledged as a known workaround for the chicken-and-egg, NOT a covert bypass. The legitimate operator (the Commanding Authority or an agent acting on their explicit consent) uses it openly. Every amendment that touches sacred infrastructure logs this fact in the amendment commit message.

The attacker version of the same bypass would be detectable because:
- The Commanding Authority would not have authorized it
- The bypass would not be paired with a legitimate amendment commit
- Hash drift on basement files would surface in tamper detection (when those files are in `basement.hashes`)

### Why This Is Documented But Not Closed

Closing the bootstrap pattern itself (e.g., preventing Python file writes to sacred paths) is hard. Common detection strategies:
- **Static-pattern detection** (the v1.4 approach) cannot enumerate every language interpreter's file-write idiom
- **Post-hook file-change verification** would catch this but adds significant complexity (snapshot before tool call, diff after, alert on changes to sacred paths)
- **System-call-level tracing** would be definitive but requires kernel-level integration (auditd, eBPF) outside the scope of a PreToolUse hook

For now: the bootstrap pattern is the documented escape valve. Future amendments may close this gap with a heavier detection mechanism, but for v1.5 it remains the canonical way to perform amendments on the protection infrastructure itself.

### Discipline

Operators using the bootstrap pattern must:
- Document its use in the amendment commit message
- Restore the gate immediately after the amendment
- Never use the pattern outside a legitimate amendment cycle
- Treat any use of the pattern as a high-trust action recorded in the public commit history

The pattern works because the system has a single Commanding Authority. It would not survive a multi-operator environment without further mechanism (signed commits, multi-party approval, etc.).

---

## 7. Ratification Process

The Commanding Authority reviews the proposal and either:

- **Ratifies** by replying with one of the explicit-consent words: `yes / go / do it / approved / confirmed`
- **Declines** with explanation
- **Returns for revision** — proposer iterates

A ratification covers only the scope explicitly proposed. It does not authorize related-but-unstated changes. The proposer may not bundle additional edits under the same approval.

Upon ratification:

1. The amendment is logged in a new entry to the change record (see Section 10)
2. The version number is incremented per the policy in Section 10
3. Implementation begins (see Section 8)

---

## 8. Implementation Steps

After ratification, the proposer (or the Commanding Authority directly) executes:

1. **Update the source-of-truth file** — typically `ARMY_MISSION.md` or the doctrine block in agent `CLAUDE.md` files

2. **Tag a new version** — annotated git tag in the form `v<major>.<minor>-foundation`, e.g., `v1.1-foundation`. Tag message includes the amendment summary.

3. **Push to fork** — origin only, never upstream

4. **Update agent CLAUDE.md files** — if the amendment changes the COMMAND AUTHORITY block, propagate the new text to all live agents (currently 5; future may be more). The onboarding script (`scripts/onboard-agent.sh`) should also be updated so new agents inherit the new text on day one.

5. **Update foundational memory** — insert a new pinned memory at importance=1.0, salience=5.0 with the updated doctrine text, per the pattern used in v1.0

6. **Restart agents** — `systemctl --user restart` all affected services so the new doctrine loads

7. **Re-run compliance test** — execute the protocol in `scripts/COMPLIANCE_TEST.md`. Record results in a new versioned results file (`scripts/COMPLIANCE_TEST_RESULTS_v<version>.md`).

8. **Verify integrity** — if a tamper-detection layer is active, confirm the new ARMY_MISSION.md hash is recorded as the new baseline (not flagged as drift).

If any step fails, the amendment is **not complete**. The Commanding Authority decides whether to roll back, retry, or revise.

---

## 8.9 When to Rebaseline `basement.hashes` (v1.7+)

`basement.hashes` records the SHA-256 of every basement-level file tracked by tamper detection. The `basement-hash-check.sh` script compares current hashes against the baseline every 6 hours and alerts on drift.

There are TWO categories of hash drift, with completely different responses:

### Legitimate Drift (rebaseline)

Caused by a ratified amendment that intentionally modified a monitored file. Examples:
- v1.2 amendment edited `ARMY_MISSION.md` → hash drifted from `644c00e189...` to `76bfb9feda...`
- v1.6 amendment moved the hook script → hash entry for the new path replaces the old

**Response:** Run `bash scripts/basement-hash-rebaseline.sh`. Confirm the change matches the ratified amendment. Commit the updated `basement.hashes`.

### Suspicious Drift (investigate)

Caused by anything other than a ratified amendment. Examples:
- A tamper alert fires on a file that wasn't part of any recent amendment
- A file changed during a window when no amendment was in progress
- The change doesn't match the diff documented in the amendment commit

**Response:**
1. DO NOT rebaseline as a routine action.
2. Investigate: what changed, when, by what tool, via what path.
3. Check git history: does any recent commit document this change?
4. Check the `audit_log` and `/tmp/doctrine-hook.log`: any block events or unexpected tool calls in the window?
5. If the change is legitimate but undocumented: write an amendment commit covering it FIRST, then rebaseline.
6. If the change is illegitimate: revert from a known-good source (git history for in-repo files, `.claudeclaw-backups/` for the v1.0 backup snapshot, or a fresh repo clone).

### The Principle

**Drift is information.** The first response to any hash drift is to understand it, not to silence it. Rebaseline only as the explicit closing step of a documented amendment cycle.

A rebaseline without an explanatory amendment commit is, by definition, a record of unattributed change. That is itself a tamper signal.

### Cadence Summary

| Trigger | Action |
|---|---|
| Amendment cycle just completed, monitored file changed | Rebaseline as §8 step |
| Tamper alert fires, you don't recognize the change | Investigate before any rebaseline |
| `accessed_at` drift, content unchanged | Not applicable — basement-hash-check is content-based |
| Periodic schedule (weekly, monthly) | Not needed — drift triggers the check, not time |

---

## 9. Emergency Revisions

In rare circumstances, the Commanding Authority may need to amend the foundation under time pressure: a security incident, a discovered ambiguity exploited in production, a critical failure mode that the standard process cannot wait out.

Under such conditions:

1. **The Commanding Authority may bypass Sections 6 and 7** and act unilaterally
2. **All other Implementation Steps (Section 8) remain mandatory** — the doctrine still gets versioned, agents still get restarted, the compliance test is still re-run
3. **An emergency revision must be documented post-hoc** in the change record with a `[EMERGENCY]` flag and a written justification within 24 hours of execution
4. **Within 7 days of an emergency revision**, the Commanding Authority must review whether the standard process should be amended (Section 6 may need new pre-defined emergency types to avoid future bypasses)

Emergency revisions are the relief valve — not a normal mode. Repeated use suggests the standard process is broken and itself needs amendment.

---

## 10. Versioning, Records, and Tagging

### Versioning Policy

`v<major>.<minor>` numbering.

- **Minor increments** (`v1.0 → v1.1`) for refinements, additions, extensions that preserve the locked constants
- **Major increments** (`v1.x → v2.0`) reserved for re-founding events that would change one of the five locked constants — which, per Section 3, is *not* an amendment but a replacement

### Records

Each ratified amendment produces:

1. **A git tag** — `v<major>.<minor>-foundation`, annotated, signed (when GPG configured)
2. **An entry in `CHANGELOG.md`** (to be established when the first amendment is made — v1.0 is the initial baseline, not an amendment) with:
   - Version
   - Date
   - Amendment type (refinement / addition / extension / removal / emergency)
   - Proposer
   - One-line summary
   - Rationale link or excerpt
3. **A compliance test results file** — `scripts/COMPLIANCE_TEST_RESULTS_v<version>.md` covering the agents under the new doctrine

### Records Are Append-Only

The change record is **append-only**. Past versions are never rewritten or expunged. The history of the foundation is part of the foundation.

---

## Closing

This document codifies one principle: **the foundation evolves by the same rules it imposes on everything else.** Explicit consent. Brand-neutral. Hive-bound. No bypass.

Every future amendment, every future version, every future army member operates under this rule. The foundation grows. The standard does not.
