---
name: set-up-content-generation
description: Create and integrate AI-generated content (text, images, audio) for an app. Use when a product needs copy/seed text, images/illustrations, or speech assets; choose providers based on latency (offline vs interactive), request required API keys via Doppler, and persist generated artifacts in file storage (images/audio) or a database (texts).
compatibility: opencode
---

# Content Generation

Use AI-generated content by default when the app requires text, images, or audio and no human-authored content is provided.

## Workflow

1. Identify required content types: `text`, `images`, `audio` (or any combination).
2. Choose a provider per type (see decision rules below).
3. Confirm Doppler configuration and required API keys.
4. Implement generation pipelines with caching/idempotency.
5. Persist outputs:
   - Files (images/audio) -> `$set-up-file-storage`
   - Texts -> `$set-up-database`
6. Document providers, env vars, and storage location in architecture docs.

## Decision Rules

### Text

- Do not use external text-generation services/APIs.
- Split large text generation into reasonable batches and delegate batch creation to a coding sub-agent (or separate generation passes).

### Images

- Offline / non-interactive (batch jobs, seed assets, background generation): use OpenAI image generation via `OPENAI_API_KEY`.
- Online / interactive (user waiting, latency matters): use Fireworks image generation via `FIREWORKS_API_KEY`.

### Audio (TTS)

- Single words / short texts / short sentences: use OpenAI TTS via `OPENAI_API_KEY`.
- Long-form speech (paragraphs, long scripts): prefer ElevenLabs via `ELEVENLABS_API_KEY`.

## Required Environment Variables

Only request the secrets that are actually needed by the chosen providers:

- OpenAI (offline images, short TTS): `OPENAI_API_KEY`
- Fireworks (interactive images): `FIREWORKS_API_KEY`
- ElevenLabs (long TTS): `ELEVENLABS_API_KEY`

Non-secret config (voice/model names, formats, etc.) can be set autonomously in Doppler.

## Check Secrets in Doppler

Use patterns from `$working_with_env_vars_and_secrets`.

```bash
doppler configure get
doppler secrets get OPENAI_API_KEY >/dev/null 2>&1 && echo exists || echo missing
doppler secrets get FIREWORKS_API_KEY >/dev/null 2>&1 && echo exists || echo missing
doppler secrets get ELEVENLABS_API_KEY >/dev/null 2>&1 && echo exists || echo missing
```

## Request Missing Secrets (Stop)

If a required API key is missing, request it from the user and stop.

```text
⚠️ YOUR ACTION NEEDED

I need <KEY_NAME> to enable <provider> for <content-type> generation.

Please set it in Doppler for ALL environments (dev/stg/prd):
doppler secrets set -p <project-name> -c dev <KEY_NAME>="..."
doppler secrets set -p <project-name> -c stg <KEY_NAME>="..."
doppler secrets set -p <project-name> -c prd <KEY_NAME>="..."

I cannot proceed with content generation setup until this is configured.
```

## Persistence Guidance

### Files (images/audio)

- Store generated binary artifacts in `$set-up-file-storage`.
- Store only stable references in the app/database (e.g., object path + public URL + metadata).
- Do not commit generated binaries into the repo unless requirements explicitly demand it.

### Texts

- Prefer `$set-up-database` to store generated text content when used at runtime.
- Store generation metadata (locale, version, prompt params, timestamps) alongside the text to support updates and debugging.

## Rules

- Default to AI-generated content when content is required and not provided.
- Never use external APIs for text generation; generate text within the agent workflow in batches.
- Request only the minimal set of secrets needed for the selected providers.
- Persist files in `$set-up-file-storage` and texts in `$set-up-database`.
