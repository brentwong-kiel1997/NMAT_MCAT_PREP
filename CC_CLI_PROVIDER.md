# Claude Code CLI as the study-coach model

Gabay's AI coach can run its completions through this server's **Claude
Code CLI** instead of an HTTP API — reusing the CLI's existing model
configuration and authentication, with **no API key and no base URL** to
manage. This document is the complete configuration reference.

## How it works

```
coach call ──portal/llm.py chat_completion()
               └─ api_style == "claude-code"
                  └─ claude -p --output-format json
                        --system-prompt "<coach persona>"
                        --model "<provider.model_id>"          (stdin: conversation)
                     cwd = <RUNTIME_DIR>/cc-workspace   (dedicated empty dir)
```

- Every call is **stateless**: `-p` print mode, a fresh session id per
  call, never `--continue` / `--resume`.
- **Isolated from development CC by four locks** (verified by audit):
  1. `cwd` is pinned to the dedicated empty workspace — a missing
     `CC_WORKSPACE` refuses to run rather than inheriting the deploy
     checkout's project config;
  2. **all tools are denied** (`--disallowedTools` covers Bash/Write/Edit/
     Web*/Task/…) so a crafted learner prompt cannot reach the shell even
     though this machine's user CC settings carry `bypassPermissions`
     (empirically confirmed: the model reports "no Bash tool in this
     session");
  3. `--permission-mode manual` as a second lock against permissive
     user-level settings;
  4. session transcripts the CLI writes under `~/.claude/projects/` are
     swept daily (best-effort) so learner prompt content and disk do not
     accumulate.
- The coach persona arrives via `--system-prompt`; the model is pinned per
  provider row via `--model` (pattern-guarded to a plain token).
- `max_tokens`/`temperature` have no CLI equivalents — replies are bounded
  only by the CLI; the shared daily per-user coach budget
  (`GABAY_COACH_DAILY_LIMIT`) caps total use.
- Failures (CLI missing, timeout, non-zero exit, `is_error`, non-JSON
  output) degrade exactly like the other backends: a message, never a 500.
- gunicorn runs with `--timeout 120`, above the coach's 90 s CLI ceiling,
  so a slow call can't abort the worker and orphan the CLI child.

## Enabling it (staff)

1. Sign in as staff → **Manage → Models**.
2. Add a model:
   - **API style**: `Claude Code CLI (this server)`
   - **Display name**: anything (e.g. `Claude Code CLI (server)`)
   - **Base URL**: leave blank
   - **API key**: leave blank
   - **Model id**: the model tag your CLI routes to (on this server:
     `glm-5.3[1m]`); blank falls back to the CLI's configured default
3. Press **Test** — it sends a tiny live completion through the CLI and
   shows the reply or the exact CLI error.
4. **Set current** when you want the coach switched over. Switching back to
   an HTTP provider is the same one-click action.

A provider row named `Claude Code CLI (server)` already exists in the
production database (created inactive) — just Test, then Set current.

## Environment

| Variable | Default | Purpose |
| --- | --- | --- |
| `GABAY_CC_WORKSPACE` | `<RUNTIME_DIR>/cc-workspace` | cwd for CLI calls; created lazily. Keep it an **empty, dedicated** directory — that emptiness is the isolation boundary for project-level CC config. |

The CLI's own auth/model configuration (whatever `claude` on this server
already uses) is read by the CLI itself — Gabay never stores or copies it.

## Operational notes

- **Cost/latency**: a CLI call carries the CLI harness overhead (~13k
  input tokens, ~$0.07, 6–10 s in practice). The daily budget caps total
  usage; timeouts follow the coach's existing 90 s ceiling.
- **Concurrency**: CLI calls block a gunicorn sync worker exactly like the
  HTTP backends' 90 s calls do — two workers absorb the normal coach load.
- **Upgrade path**: `claude` CLI updates change nothing here; the bridge
  only depends on `-p --output-format json` staying stable.

## Troubleshooting

| Symptom | Meaning / fix |
| --- | --- |
| Test says `claude CLI exited ...` | Run `claude -p ok` by hand on the server; check auth/model routing. |
| Test says `no API key set` | You picked an HTTP style, not `Claude Code CLI (this server)`. |
| Coach pages say "No AI model configured" with the CLI provider active | Upgrade past commit `529c141` — `coach_ready()` initially required a stored key and dead-ended this style (fixed). |
| Empty replies | Check the provider row's Model id matches a model your CLI can route. |
