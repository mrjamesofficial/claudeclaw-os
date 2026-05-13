---
name: discuss
description: Multi-agent discussion — all relevant agents contribute their perspective on a topic, General synthesizes
user_invocable: true
---

# Discuss Skill

Takes a topic and sends it to all 5 agents via mission tasks. Each agent responds from their area of expertise. General synthesizes the final output.

## Extracting the topic

The user's message will look like `/discuss <topic>`. Strip the `/discuss` prefix and use the rest as the topic. If no topic is provided, ask the user for one.

## Steps

1. Get the project root:
```bash
PROJECT_ROOT=/home/adminjames/claudeclaw
```

2. Create a mission task for each agent with a tailored prompt:

```bash
# Research agent
node "$PROJECT_ROOT/dist/mission-cli.js" create --agent research --title "Discuss: <topic>" \
  "From your perspective as the Research agent (deep web research, academic sources, competitive intel, trend analysis): What do you know about '<topic>'? What are the key facts, trends, or data points relevant to this topic? Be specific and concise — 3-5 bullet points."

# Comms agent
node "$PROJECT_ROOT/dist/mission-cli.js" create --agent comms --title "Discuss: <topic>" \
  "From your perspective as the Comms agent (email, messaging, community, outreach): How does '<topic>' affect or relate to communications strategy? What should we know from a comms angle? Be specific — 3-5 bullet points."

# Content agent
node "$PROJECT_ROOT/dist/mission-cli.js" create --agent content --title "Discuss: <topic>" \
  "From your perspective as the Content agent (YouTube, LinkedIn, writing, trends): What content opportunities or angles does '<topic>' present? How should we think about it from a content perspective? Be specific — 3-5 bullet points."

# Ops agent
node "$PROJECT_ROOT/dist/mission-cli.js" create --agent ops --title "Discuss: <topic>" \
  "From your perspective as the Ops agent (calendar, admin, billing, systems): What are the operational implications of '<topic>'? What does this mean for how we run things? Be specific — 3-5 bullet points."
```

3. Capture the task IDs from the output of each create command (each prints the task ID).

4. Tell the user: "Collecting perspectives from all agents on: <topic>. This takes ~60 seconds..."

5. Wait 60 seconds, then poll for each result:
```bash
node "$PROJECT_ROOT/dist/mission-cli.js" result <task-id>
```

6. If a result isn't ready yet, wait another 30 seconds and try once more. If still not ready after 2 attempts, note that agent as "timed out".

7. As General (the main agent), synthesize all responses into a final output:

```
💬 Discussion: <topic>

🟢 Research
[research agent's bullets]

🟡 Comms
[comms agent's bullets]

🟠 Content
[content agent's bullets]

🔴 Ops
[ops agent's bullets]

─────────────
🔵 General's Take
[2-4 sentence synthesis that connects the perspectives, highlights agreements/tensions, and gives a clear overall view or recommendation]
```

Keep it conversational but substantive. The synthesis should add something — don't just repeat what the agents said.
