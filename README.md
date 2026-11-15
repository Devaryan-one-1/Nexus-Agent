# NEXUS — Telegram + Discord + Email agent starter

A **single-owner development starter**, not a production-ready autonomous agent. Includes FastAPI, OpenAI Agents SDK structured task routing, PostgreSQL storage, Celery/Redis task jobs, proactive digests/deadline alerts and channel-specific delivery.

## Quickstart

1. Copy `.env.example` to `.env`. Replace `OPENAI_API_KEY` and `NEXUS_ADMIN_TOKEN` with valid secrets, and configure at least one channel. Avoid committing `.env`.
2. Start: `docker compose up --build -d`.
3. Check: `curl http://localhost:8000/healthz`.
4. Create a task:

```bash
curl -X POST http://localhost:8000/v1/tasks \
  -H 'Content-Type: application/json' \
  -H 'X-Admin-Token: REPLACE_ADMIN_TOKEN' \
  -d '{"title":"Write project brief", "description":"Summarise project goals", "priority":2, "delegate_to":"planning"}'
```

5. Inspect tasks:

```bash
curl -H 'X-Admin-Token: REPLACE_ADMIN_TOKEN' http://localhost:8000/v1/tasks
```

6. Force a test notification by running `docker compose exec worker celery -A app.workers.celery_app call app.workers.daily_digest`.
7. Review worker logs with `docker compose logs -f worker`.

Your API needs a **public HTTPS endpoint** for provider webhooks. A secure development tunnel is fine for local development; production requires HTTPS reverse proxy with rate limiting.

## Telegram setup

1. Create a Telegram bot through BotFather and save the bot token.
2. Send a DM to your bot. Obtain your own Telegram numeric user ID and numeric chat ID; put them in `TELEGRAM_OWNER_USER_ID`, `TELEGRAM_CHAT_ID`.
3. Generate a secret containing only letters, numbers, underscore and hyphen and put it in `TELEGRAM_WEBHOOK_SECRET`.
4. Set Telegram webhook using POST to `https://api.telegram.org/bot<BOT_TOKEN>/setWebhook` with JSON `{"url":"https://YOUR_HOST/webhooks/telegram","secret_token":"YOUR_SECRET"}`.
5. Send `/tasks` or ask the agent to create/delegate work.

## Discord setup

1. Create a Discord application/bot in the Developer Portal.
2. Install it with `applications.commands` and `bot` scopes in a private server/channel. Give only necessary permissions to send messages in that channel.
3. Configure `DISCORD_BOT_TOKEN`, `DISCORD_PUBLIC_KEY`, `DISCORD_OWNER_USER_ID`, `DISCORD_CHANNEL_ID`. Use a dedicated private channel to prevent information leakage.
4. Configure Discord Interactions Endpoint URL as `https://YOUR_HOST/webhooks/discord`; it validates signature and answers PING requests.
5. Register a `/nexus` application command with required string option named `text`. Example command definition:

```json
{"name":"nexus","description":"Send an instruction to NEXUS","type":1,"options":[{"type":3,"name":"text","description":"Instruction","required":true}]}
```

6. Invoke `/nexus text:Create a follow-up task`. The interaction responds ephemerally with acknowledgement, while the worker posts the result in the designated private channel.

## Email setup

1. Configure Resend sending with a verified domain and sender address, e.g. `nexus@agent.example.com`.
2. Set `RESEND_API_KEY`, `EMAIL_FROM`, and `EMAIL_OWNER` (the permitted owner address, not the NEXUS sender).
3. Enable Resend Receiving for a dedicated address or subdomain. Avoid moving the MX records of your existing personal email domain by accident.
4. Register an `email.received` webhook: `https://YOUR_HOST/webhooks/resend`.
5. Set `RESEND_WEBHOOK_SECRET`. The webhook checks the Svix signature; the worker retrieves the full plain-text email body via Resend's Receiving API.
6. Email the NEXUS inbound address from `EMAIL_OWNER`. Reports/answers go to `EMAIL_OWNER`.

**Security:** Email sender address matching is only a convenience filter and can be spoofed. This starter supports only task creation/analysis and owner notifications, not unrestricted privileged actions. For production, require secondary signed verification / approval for consequential email commands. Add email threading and loop prevention before live mailbox usage.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/healthz` | Liveness |
| `GET` | `/v1/tasks` | Owner task list |
| `POST` | `/v1/tasks` | Create human task or delegate to AI |
| `POST` | `/v1/tasks/{id}/complete` | Mark completed |
| `POST` | `/webhooks/telegram` | Verified Telegram inbound |
| `POST` | `/webhooks/discord` | Signed Discord command interactions |
| `POST` | `/webhooks/resend` | Signed Resend received-email event |

API routes in `/v1` require `X-Admin-Token` for the development starter. Replace with OIDC, access scopes and per-user ownership checks in production.

## Agent behaviour

* `/tasks`: list outstanding tasks by priority.
* `/done <task-id-prefix>`: mark a human task completed.
* Natural language: supervisor selects `reply`, `create_task`, or `delegate` (research/planning).
* Delegated agent tasks are run by Celery, saved to DB, and completion is broadcast to configured channels.
* Daily priorities are sent at 09:00 in configured `TIMEZONE`.
* Deadline alerts run at 09:00, 13:00 and 17:00 for human tasks that have `due_at` set. Set `due_at` in `POST /v1/tasks` as an ISO 8601 timestamp with offset (e.g. `2026-11-20T17:00:00+00:00`).
* `reconcile` scans pending work and outbox every minute.

The research specialist **does not have live browsing**. Connect a vetted search tool and evidence storage before using it for current affairs. The execution agent, approval routes, dependency graph and long-term semantic memory are in the production blueprint, not implemented in this starter.

## Database

`app/models.py` contains the implemented single-owner starter schema, created on startup with `Base.metadata.create_all`. For the multi-user production target, see `docs/schema.sql` and `docs/architecture.md`; the SQL target is **not** an applied migration. Set up Alembic before schema evolution.

## Operational limitations

- `reconcile` and Celery deliver at-least-once, **not** exactly-once. A crash after provider acceptance can duplicate an outbound message. Add provider idempotency keys where available.
- Stalled jobs are reclaimed on a timeout; long-running calls can cause replay. Add per-run leases and deadlines for production.
- Inbound messages are currently truncated for model classification; attachments and HTML are not processed.
- Discord receives slash commands, not all regular DMs. Regular DM support needs Gateway bot + privileged intent consideration.
- Multi-user and multiple notification targets, approval workflow, conversation history, quiet hours, rate limits and complete monitoring are future milestones.
- Telegram/Discord messages are intentionally length-limited; for long reports, store report artefacts and send a secure link instead.
- The Docker Compose file uses simple development database credentials and exposes port 8000; change credentials and use a public HTTPS reverse proxy and private networks in production.