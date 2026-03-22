"""Generate a Telethon StringSession and save it to Doppler.

Run with:
    doppler run -- python scripts/create_telethon_session.py
"""

import os
import subprocess

from telethon.sessions import StringSession
from telethon.sync import TelegramClient

api_id = int(os.environ["TELETHON_API_ID"])
api_hash = os.environ["TELETHON_API_HASH"]

with TelegramClient(StringSession(), api_id, api_hash) as client:
    session_string = client.session.save()

subprocess.run(
    ["doppler", "secrets", "set", f"TELETHON_SESSION={session_string}"],
    check=True,
)
print("TELETHON_SESSION saved to Doppler.")
