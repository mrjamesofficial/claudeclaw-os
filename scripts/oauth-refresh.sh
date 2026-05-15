#!/usr/bin/env bash
# Refresh the Claude Code OAuth token before it expires, then ensure
# the 5 ClaudeClaw agents are running. Designed to be run by a systemd
# user timer every ~3 hours (tokens last ~8 hours).
#
# Why: Claude Max subscription uses OAuth, not API keys. The token expires
# every ~8 hours and crashes any background agent mid-request. This refresh
# keeps the hive mind autonomous.

set -euo pipefail

CRED_FILE="$HOME/.claude/.credentials.json"
LOG_FILE="$HOME/.claude/oauth-refresh.log"
CLIENT_ID="9d1c250a-e61b-44d9-88ed-5944d1962f5e"
TOKEN_URL="https://platform.claude.com/v1/oauth/token"
SERVICES=(claudeclaw claudeclaw-research claudeclaw-comms claudeclaw-content claudeclaw-ops)
NOTIFY_SCRIPT="$HOME/claudeclaw/scripts/notify.sh"

log() {
  echo "[$(date -Iseconds)] $*" | tee -a "$LOG_FILE"
}

# Silent on success, audible on failure — pings Telegram if refresh breaks
alert() {
  if [ -x "$NOTIFY_SCRIPT" ]; then
    "$NOTIFY_SCRIPT" "<b>⚠️ ClaudeClaw OAuth refresh FAILED</b>%0A%0A$1%0A%0ARun: <code>claude login</code> then <code>systemctl --user restart claudeclaw*.service</code>" || true
  fi
}

if [ ! -f "$CRED_FILE" ]; then
  log "ERROR: credentials file missing at $CRED_FILE — run 'claude login' manually"
  alert "Credentials file missing at $CRED_FILE"
  exit 1
fi

node - <<'NODE' >>"$LOG_FILE" 2>&1
const fs = require('fs');
const https = require('https');
const path = require('path');

const CRED = process.env.HOME + '/.claude/.credentials.json';
const CLIENT_ID = '9d1c250a-e61b-44d9-88ed-5944d1962f5e';
const TOKEN_URL = 'https://platform.claude.com/v1/oauth/token';

const ts = () => new Date().toISOString();
const log = (m) => console.log(`[${ts()}] ${m}`);

const creds = JSON.parse(fs.readFileSync(CRED, 'utf8'));
const oauth = creds.claudeAiOauth;
if (!oauth || !oauth.refreshToken) {
  log('ERROR: no refreshToken in credentials');
  process.exit(2);
}

const body = JSON.stringify({
  grant_type: 'refresh_token',
  refresh_token: oauth.refreshToken,
  client_id: CLIENT_ID,
});

const u = new URL(TOKEN_URL);
const req = https.request({
  hostname: u.hostname,
  path: u.pathname,
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(body),
  },
}, (res) => {
  let data = '';
  res.on('data', (c) => data += c);
  res.on('end', () => {
    if (res.statusCode !== 200) {
      log(`ERROR: refresh returned ${res.statusCode}: ${data.slice(0,300)}`);
      process.exit(3);
    }
    const j = JSON.parse(data);
    if (!j.access_token || !j.expires_in) {
      log(`ERROR: unexpected response shape: keys=${Object.keys(j).join(',')}`);
      process.exit(4);
    }
    creds.claudeAiOauth.accessToken = j.access_token;
    if (j.refresh_token) creds.claudeAiOauth.refreshToken = j.refresh_token;
    creds.claudeAiOauth.expiresAt = Date.now() + j.expires_in * 1000;
    if (j.scope) creds.claudeAiOauth.scopes = j.scope.split(' ');

    const tmp = CRED + '.tmp';
    fs.writeFileSync(tmp, JSON.stringify(creds), { mode: 0o600 });
    fs.renameSync(tmp, CRED);
    fs.chmodSync(CRED, 0o600);

    const hours = (j.expires_in / 3600).toFixed(2);
    log(`OK: token refreshed; expires in ${hours}h at ${new Date(creds.claudeAiOauth.expiresAt).toISOString()}`);
  });
});
req.on('error', (e) => { log(`ERROR: ${e.message}`); process.exit(5); });
req.write(body);
req.end();
NODE

REFRESH_RC=$?
if [ $REFRESH_RC -ne 0 ]; then
  log "ERROR: refresh failed (rc=$REFRESH_RC) — manual 'claude login' may be required"
  alert "Refresh script exited with rc=$REFRESH_RC. Check log: $LOG_FILE"
  exit $REFRESH_RC
fi

# Restart any agent that is not currently active (crashed earlier on a 401)
for svc in "${SERVICES[@]}"; do
  state="$(systemctl --user is-active "$svc.service" 2>/dev/null || true)"
  if [ "$state" != "active" ]; then
    log "Restarting $svc (was: $state)"
    systemctl --user restart "$svc.service" || log "WARN: failed to restart $svc"
  fi
done

log "Refresh cycle complete"
