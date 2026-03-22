# Telethon E2E Testing Setup

Telethon is a Telegram **client** library (MTProto API). It acts as a real user, letting you send messages to your bot and assert on responses. Use it for end-to-end testing of dev bots only.

## How it works

- The bot runs normally via python-telegram-bot (long polling)
- Telethon connects as the user's **personal Telegram account** on **production DC**
- Telethon sends messages to the dev bot by username and asserts on responses
- Uses `StringSession` stored in Doppler so tests can reconnect without interactive login

## Prerequisites

- User has `api_id` and `api_hash` from https://my.telegram.org (personal account — these identify the app, not the user)
- User has created a dev bot via @BotFather on their **main account** (production DC)

### Why production DC, not test DC?

Telegram's test DC is a separate isolated environment. Using it for bot testing would require running a local Telegram Bot API server (the official `api.telegram.org` only serves production). This adds significant infrastructure complexity. For most projects, production DC with a dedicated dev bot is sufficient.

The user's **Telegram account** is used for Telethon authentication. Test DC accounts (even with the same phone number) cannot see production DC bots.

So recommend user to have a separate phone number for testing (so if something goes wrong, the main account not being banned).

## Doppler secrets to request from user

**IMPORTANT:** The variable names below are mandatory and must be used exactly as written. Do NOT use alternative names (e.g. `TG_API_ID`, `TELETHON_API_ID`, `API_ID`, `TG_API_HASH`, `TELETHON_API_HASH`, `API_HASH`, `TELEGRAM_BOT_USERNAME`, `TG_BOT_USERNAME`, `BOT_USERNAME`). All code, fixtures, and scripts in this guide depend on these exact names.

| Variable | Format | Who sets | Description |
|---|---|---|---|
| `TELEGRAM_API_ID` | numeric string | user | From my.telegram.org. **Exact name required — no aliases.** |
| `TELEGRAM_API_HASH` | hex string | user | From my.telegram.org. **Exact name required — no aliases.** |
| `TELEGRAM_BOT_USERNAME` | with `@` (e.g. `@my_dev_bot`) | user | Copied directly from Telegram. Telethon resolves bots by username, not token. Same key in every Doppler environment, different value per env. **Exact name required — no aliases.** |
| `TELEGRAM_SESSION_STRING` | long base64 string | automated (via script) | Generated and pushed to Doppler by `scripts/create_session.py` in a single step. The user only runs the script — never ask them to copy/paste or manually set this value. |

## Setup steps

### 1. Add Telethon as a dev dependency

All dependencies needed for Telethon and the session script must be added to `pyproject.toml` via `uv add` — never rely on system-level or manually installed packages.

```bash
uv add --dev "Telethon>=1.42.0,<2"
```

If the session script or test fixtures require any additional packages beyond Telethon itself, add them the same way (`uv add --dev <package>`). Everything the script imports must be resolvable from the project's `pyproject.toml`.

### 2. Exclude scripts from ruff print/subprocess rules

In `ruff.toml`, add:

```toml
[lint.per-file-ignores]
"scripts/*" = ["T201", "S603"]
```

### 3. Request secrets from user

Ask for `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, and `TELEGRAM_BOT_USERNAME` using the standard Doppler secret request workflow. Example:

```
I need credentials for Telethon e2e testing. Please set:

    doppler secrets set TELEGRAM_API_ID="your-api-id" -p <project> -c dev
    doppler secrets set TELEGRAM_API_HASH="your-api-hash" -p <project> -c dev
    doppler secrets set TELEGRAM_BOT_USERNAME="@your_dev_bot" -p <project> -c dev
```

### 4. Create the session generation script

Copy the template script from the skill directory into the project:

```bash
cp ~/.config/opencode/skills/set-up-telegram-bot/create_telethon_session.py scripts/create_session.py
```

Then edit `scripts/create_session.py` and replace `<project-name>` with the actual Doppler project name.

**What the script does (single step — auth + Doppler push):**
The script handles everything in one run: it authenticates the user's personal Telegram account (phone number + verification code prompt), generates the `StringSession`, and automatically pushes it to Doppler as `TELEGRAM_SESSION_STRING`. The user runs one command and is done. **Never ask the user to perform auth and Doppler push as two separate actions** — the whole point of this script is to combine them.

The session string is like a saved login cookie — it lets Telethon reconnect without prompting for phone/code again. It can expire if the user changes their Telegram password or 2FA settings, in which case the user re-runs the same script.

**Commit this script to the repo.** It lives at `scripts/create_session.py` and should be checked in so that any team member (or the same user later) can re-run it when the session expires. It contains no secrets — it reads `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` from Doppler at runtime.

Source template: [create_telethon_session.py](./create_telethon_session.py)

### 5. Ask user to run the session script

**This is the agent's responsibility.** After `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` are set in Doppler, the agent must give the user the exact, copy-pasteable command to run from the repo root — with the real Doppler project name and the actual script path already filled in (no placeholders). Example:

```
Please run this command from the repo root — it will guide you through Telegram auth
and automatically save the session to Doppler (everything in one step):

    doppler run -p my-tg-bot -c dev -- uv run scripts/create_session.py
```

The agent must substitute the real project name and script path. Never give a generic command with `<project>` or `<script>` placeholders — the user should be able to copy-paste and run immediately.

**Never ask the user to do two separate steps** (e.g. "first authenticate, then run `doppler secrets set …`"). The script handles both.

The agent should then verify the session was stored by checking `doppler secrets -p <project> -c dev --only-names` for `TELEGRAM_SESSION_STRING`.

### 6. Create test fixtures

In `tests/conftest.py`, add a Telethon client fixture:

```python
"""Shared fixtures for e2e tests."""

from collections.abc import AsyncIterator
import os

import pytest_asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession


@pytest_asyncio.fixture
async def telegram_client() -> AsyncIterator[TelegramClient]:
    """Connect an authenticated Telethon client for e2e tests."""
    api_id: int = int(os.environ["TELEGRAM_API_ID"])
    api_hash: str = os.environ["TELEGRAM_API_HASH"]
    session_str: str = os.environ["TELEGRAM_SESSION_STRING"]

    client = TelegramClient(StringSession(session_str), api_id, api_hash)
    await client.connect()
    await client.get_me()
    await client.get_dialogs()

    yield client

    await client.disconnect()
```

`get_me()` and `get_dialogs()` are called after connect to warm up the client — Telethon needs this to resolve entities properly.

Add `telegram_client` to `vulture_whitelist.py` to suppress false-positive dead code warnings.

### 7. Write e2e tests with manual marker

Use `@pytest.mark.manual` so they are excluded from `make check` (which runs `-m "not manual"`). Use Telethon's `conversation()` context manager to pair sent messages with bot responses.

```python
"""End-to-end tests for the Telegram bot."""

import os

import pytest
from telethon import TelegramClient


@pytest.mark.manual
@pytest.mark.asyncio
class TestBotE2E:
    """E2E tests using Telethon to interact with the running bot."""

    async def test_start_command(self, telegram_client: TelegramClient) -> None:
        """Send /start and verify the bot replies with the expected greeting."""
        bot_username: str = os.environ["TELEGRAM_BOT_USERNAME"]

        async with telegram_client.conversation(bot_username, timeout=10) as conv:
            await conv.send_message("/start")
            response = await conv.get_response()

            assert response.text == "Expected response text"

    async def test_echo_message(self, telegram_client: TelegramClient) -> None:
        """Send a text message and verify the bot echoes it back."""
        bot_username: str = os.environ["TELEGRAM_BOT_USERNAME"]

        async with telegram_client.conversation(bot_username, timeout=10) as conv:
            test_message: str = "Hello from Telethon e2e test"
            await conv.send_message(test_message)
            response = await conv.get_response()

            assert response.text == test_message
```

## Running e2e tests

```bash
# Terminal 1: start the bot
doppler run -- uv run python -m <package_name>

# Terminal 2: run e2e tests
doppler run -- uv run pytest -m manual -v
```

Or have the agent start the bot in the background and run tests sequentially.

## Notes

- Only the **dev** bot is tested via Telethon — never production
- Tests run on **production DC** (simplest setup). The Telegram test DC requires a local Bot API server and adds significant complexity
- Running tests repeatedly in quick succession can trigger Telegram rate limiting (`FloodWaitError`). Run e2e tests sequentially, not with `-n auto`
- The `conversation()` timeout of 10 seconds is usually sufficient; increase to 30 if the bot does heavy processing
- `.gitignore` should include `*.session` as a safety net in case anyone creates file-based sessions
