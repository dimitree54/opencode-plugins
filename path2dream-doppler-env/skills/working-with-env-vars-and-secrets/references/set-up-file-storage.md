---
name: set-up-file-storage
description: Google Cloud Storage is recommended file storage. Use when adding or changing file upload/download/public URL flows, preview page hosting, image storage, or Google credentials configuration with Doppler; the agent must choose (and preferably create) app-specific bucket names and document them, and must never ask the user for bucket names (only request GOOGLE_APPLICATION_CREDENTIALS_JSON).
compatibility: opencode
---

# Google Cloud Storage Recommended

Use Google Cloud Storage (GCS) as the recommended storage backend for files in this repo.

## Bucket Naming + Provisioning (Agent-Owned)

- Never ask the user for a bucket name. Bucket names are non-secret configuration chosen by the agent.
- Create buckets specifically for this app (and environment separation if needed). Prefer one bucket per app (or per app+env) rather than reusing shared buckets across unrelated apps.
- If the bucket does not exist, attempt to create it using the provided credentials. If creation fails due to IAM/org policy, ask the user to fix permissions or create the bucket with the agent-chosen name (do not ask them to pick a name).
- Document the final bucket name(s) in architecture docs (e.g. `docs/architecture/tech_stack.md`) along with the storage URL patterns and any public-access rules.

## Follow Existing Repo Pattern

Use `server/previewable_page_generator/google_storage.py` as the source of truth for storage behavior.

Current pattern in this repo:
- Create a GCS client with service-account credentials.
- Use bucket blobs for uploads/downloads.
- Make selected objects public for stable URLs (`https://storage.googleapis.com/...`).
- Reuse `build_default_storage()` in call sites like `server/image.py`.

## Set Up Credentials via Doppler (JSON Secret)

Store the full service-account JSON in Doppler as:
- `GOOGLE_APPLICATION_CREDENTIALS_JSON` (type: json)

**The env var MUST be named exactly `GOOGLE_APPLICATION_CREDENTIALS_JSON`. No other names (e.g. `GCP_SERVICE_ACCOUNT`, `GOOGLE_CREDENTIALS`, `GCS_KEY_JSON`, etc.) are allowed. All code must reference this exact name.**
**This is the only environment variable the agent may request from the user for file storage setup.** Any bucket names, prefixes, public URL settings, etc. must be set autonomously by the agent (as non-secret config if needed).

If this secret is missing, request from the user:

```text
⚠️ YOUR ACTION NEEDED

I need Google Cloud service account credentials to set up file storage.

Please set the following in Doppler:
doppler secrets set GOOGLE_APPLICATION_CREDENTIALS_JSON='{"type":"service_account", "project_id":"...", "private_key":"...", ...}'

You can download this JSON from the Google Cloud Console (IAM & Admin > Service Accounts).

I cannot proceed with storage setup until this is configured.
```

Configure bucket names autonomously in code/config; do not ask the user for bucket names.

Use this code pattern:

```python
import os
import json
from google.oauth2 import service_account

# Secret contains the *entire* service account JSON as a string
sa_json = os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
info = json.loads(sa_json)

# Add scopes if you're calling APIs that require them (common for Sheets/Drive/Gmail/etc.)
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

credentials = service_account.Credentials.from_service_account_info(
    info,
    scopes=SCOPES,
)

# Now use `credentials` with Google client libraries (examples below)
```

## GCS Client Snippet (Aligned With This Repo)

```python
from google.cloud import storage

client = storage.Client(credentials=credentials)
bucket = client.bucket("insight_of_the_day_public_pages")
```

## Upload Public File (Repo-Equivalent Behavior)

Equivalent to `GoogleCloudStorage.upload_file_public`:

```python
blob = bucket.blob("images/example.webp")
blob.upload_from_filename("/tmp/example.webp", content_type="image/webp")
blob.make_public()
public_url = blob.public_url
```

## Upload Public HTML (Repo-Equivalent Behavior)

Equivalent to `GoogleCloudStorage.upload_html_public`:

```python
blob = bucket.blob("previews/page-123.html")
blob.cache_control = "public, max-age=300"
blob.upload_from_string("<html>...</html>", content_type="text/html")
blob.make_public()
public_url = blob.public_url
```

## Download Text

Equivalent to `GoogleCloudStorage.download_blob_as_text`:

```python
blob = bucket.blob("previews/page-123.html")
html = blob.download_as_text(encoding="utf-8")
```

## Implementation Rules

- Prefer extending `server/previewable_page_generator/google_storage.py` over ad-hoc storage code.
- Keep credential loading env-based; do not hardcode credential files.
- **Always use `GOOGLE_APPLICATION_CREDENTIALS_JSON` as the env var name — never invent alternative names.**
- Configure bucket names autonomously with sensible defaults/env wiring; do not ask the user for bucket names.
- Keep bucket/blob naming explicit and stable for public URL consumers.
- Keep Twitter-only product scope intact; storage changes must support existing Twitter flows.
