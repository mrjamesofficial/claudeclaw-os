---
name: standup
description: Team standup — all 5 agents report last 24h activity, synthesized into a unified status report
user_invocable: true
---

# Standup Skill

Query the last 24 hours of activity from all 5 agents in the ClaudeClaw database, then synthesize a unified team standup report.

## Steps

1. Get the project root and DB path:
```bash
PROJECT_ROOT=/home/adminjames/claudeclaw
DB="$PROJECT_ROOT/store/claudeclaw.db"
SINCE=$(date -d '24 hours ago' '+%s')
```

2. Pull each agent's assistant messages from the last 24 hours:
```bash
sqlite3 "$DB" "
  SELECT agent_id, substr(content, 1, 800)
  FROM conversation_log
  WHERE created_at > $SINCE
    AND role = 'assistant'
    AND agent_id IN ('main','research','comms','content','ops')
  ORDER BY agent_id, created_at ASC;
"
```

3. Also pull each agent's received user messages to understand what they were asked:
```bash
sqlite3 "$DB" "
  SELECT agent_id, substr(content, 1, 400)
  FROM conversation_log
  WHERE created_at > $SINCE
    AND role = 'user'
    AND agent_id IN ('main','research','comms','content','ops')
  ORDER BY agent_id, created_at ASC;
"
```

4. For each agent, summarize in 2-3 bullets what they worked on. If an agent has no activity, note "No activity in last 24h".

5. Format the final report as:

```
📋 Team Standup — [date]

🔵 General
• [bullet]
• [bullet]

🟢 Research
• [bullet]

🟡 Comms
• [bullet]

🟠 Content
• [bullet]

🔴 Ops
• [bullet]

─────────────
Summary: [2-3 sentence synthesis of overall team activity and any cross-agent themes]
```

Keep each agent section tight — facts only, no padding. If multiple agents worked on related things, call it out in the Summary.
