---
name: set-up-telegram-bot
description: Recommendations of how to set up telegram bot app. Use when implementing update handling, commands, conversation flows, or deployment for Telegram bots, and when deciding between polling vs webhooks and dev vs production bot tokens.
compatibility: opencode
---

# Telegram Bot

## Rules

1. **Default to long polling.** Prefer a simple Telegram bot library that listens for updates (long polling) whenever possible.
2. **Webhooks are last resort.** Never choose webhooks unless long polling is genuinely impossible. If you propose webhooks, you MUST explicitly state the specific blocking constraint that makes polling infeasible.
   - Valid "unavoidable" reasons include:
     - The hosting platform cannot run a long-lived process (strict request-driven/serverless-only runtime).
     - You must run multiple replicas and cannot guarantee "single active poller" reliably (horizontal scaling / HA requirement).
   - Invalid reasons (do NOT justify webhooks):
     - "Webhooks are more production."
     - "Lower latency." (Long polling is already near-real-time for bots.)
     - "Seems cleaner."
3. **Request `TELEGRAM_BOT_TOKEN` from the user — this exact name only.** Never use alternative names such as `TELEGRAM_TEST_BOT_TOKEN`, `TELEGRAM_BOT_TOKEN_DEV`, `TELEGRAM_BOT_TOKEN_PRD`, `TG_BOT_TOKEN`, or any other variant. The single secret name `TELEGRAM_BOT_TOKEN` is used across all environments. Recommend (soft) that the user creates separate bots via @BotFather for dev, stg, and prd so that development/testing never affects the production bot — each Doppler environment stores a different actual token value under the same `TELEGRAM_BOT_TOKEN` key.
4. **Request `TELEGRAM_BOT_USERNAME` — this exact name only.** Never use alternative names such as `TELEGRAM_BOT_USERNAME_DEV`, `TELEGRAM_BOT_USERNAME_PRD`, `TG_BOT_USERNAME`, `BOT_USERNAME`, or any other variant. Like `TELEGRAM_BOT_TOKEN`, the same key name is used in every Doppler environment with a different value (e.g. `@my_dev_bot` in dev, `@my_prd_bot` in prd). Format: with `@` prefix (e.g. `@my_dev_bot`).

## Starting from an empty repo

If starting from scratch, consider using `~/.config/opencode/resources/proto_apps/proto_tg_bot` as a base template (via the `init-repo` skill). It provides:
- Strict linting rules (`ruff.toml`) and a well-configured `pyproject.toml`
- Basic bot setup with config, entry point, and long-polling structure
- Test scaffolding with `pytest`
- `Makefile`, `vulture_whitelist.py`, and `uv.lock` for a ready-to-go dev workflow

## Quick checklist

- **Mandatory first step:** Ask the user for `TELEGRAM_BOT_TOKEN` and `TELEGRAM_BOT_USERNAME` (these exact names — never `TELEGRAM_TEST_BOT_TOKEN`, `TELEGRAM_BOT_TOKEN_DEV`, `TELEGRAM_BOT_USERNAME_DEV`, or any other variant). Store them using the skill for managing secrets. Recommend that the user creates separate bots for each environment (dev, stg, prd) and sets the corresponding values in each Doppler environment under the same key names, so development never disrupts production.
- **Highly recommended: Set up Telethon for e2e testing.** Bots are notoriously hard to test without actually sending messages. Telethon acts as a real Telegram user, letting you send messages to your dev bot and assert on responses — this is the closest thing to "clicking through the bot" automatically. Set it up early (before the bot grows complex) so every new handler gets e2e coverage from day one. Follow the full setup in [telethon_e2e_testing.md](./telethon_e2e_testing.md). Proactively suggest this to the user when setting up a new bot.
  - **Telethon requires two additional secrets:** `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`. These MUST be stored under exactly these names — no alternative names (e.g. `TG_API_ID`, `TELETHON_API_ID`, `API_ID`) are allowed.
- Default to long polling for dev/stg/prd. Do not propose webhooks unless blocked; if blocked, document the blocking constraint and the additional infra/security requirements webhooks introduce.
- Keep dev/prod config separated (env files, deployment targets, and secrets).
