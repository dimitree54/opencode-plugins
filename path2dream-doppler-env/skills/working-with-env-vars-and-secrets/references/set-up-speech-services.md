---
name: set-up-speech-services
description: Set up and standardize speech services for (1) Pronunciation Assessment and (2) Speech-to-Text (STT). Use when a project needs Azure Speech Pronunciation Assessment (scripted/reference text) and must request `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION` from the user for Doppler, or when a project needs STT and must choose between Azure (short utterances, single sentences, word/phrase recognition) and OpenAI Whisper (longer free-form recordings where context helps, but may hallucinate on very short audio). Also use when documenting env vars and validation steps for these integrations.
compatibility: opencode
---

# Set Up Speech Services

## Overview

This skill standardizes two speech capabilities:
- **Pronunciation Assessment:** Use **Azure Speech** (recommended).
- **Speech-to-Text (STT):** Use **Azure Speech** for short prompts; use **OpenAI Whisper** for longer recordings.

## Decisions (Firm)

### 1) Pronunciation Assessment (Recommended: Azure)

Use Azure Speech Pronunciation Assessment in **reference-text/scripted** mode.

Required env vars (set in Doppler):
- `AZURE_SPEECH_KEY` (secret, user-provided)
- `AZURE_SPEECH_REGION` (secret-ish, user-provided; treat as secret to keep setup consistent)

### 2) Speech-to-Text (STT) (Decision Tree)

Use these rules:
- **Short audio (single sentence, word/phrase recognition, scripted prompt validation):** use **Azure Speech** STT (more stable for short utterances in this product context).
- **Long audio (multi-sentence, longer monologues, free-form content):** use **OpenAI Whisper** via OpenAI API (context helps, but be aware it can hallucinate on very short audio).

Required env vars:
- Azure STT uses the same `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION`.
- Whisper uses `OPENAI_API_KEY` (secret, user-provided).

## Workflow (Doppler + Provider Setup)

### 1) Ensure Doppler is the Source of Truth

Never create `.env` files. All env vars go to Doppler and apps/tests run via `doppler run -- ...`.

Check the Doppler project exists (replace if repo uses a different name):

```bash
doppler projects get <project-name> >/dev/null 2>&1 && echo exists || echo missing
```

### 2) Request Azure Speech Credentials From the User (Required)

The agent MUST NOT invent or guess these values. The user must obtain them in Azure.

Tell the user to:
1. Create an Azure **Speech** resource in the Azure Portal.
2. Open the resource → **Keys and Endpoint**.
3. Copy:
   - **KEY 1** → `AZURE_SPEECH_KEY`
   - **Location/Region** (e.g., `germanywestcentral`) → `AZURE_SPEECH_REGION`

Then ask them to set in Doppler:

```bash
doppler secrets set -p <project-name> -c <dev|stg|prd> \
  AZURE_SPEECH_KEY="..." \
  AZURE_SPEECH_REGION="..."
```

### 3) Request OpenAI Credentials From the User (Whisper STT)

If the product uses OpenAI Whisper for long-form STT, request:

```bash
doppler secrets set -p <project-name> -c <dev|stg|prd> OPENAI_API_KEY="..."
```

### 4) Validation (Non-Destructive)

The agent SHOULD validate that required keys exist in Doppler without printing values:

```bash
doppler secrets get AZURE_SPEECH_KEY -p <project-name> -c <config> >/dev/null 2>&1 && echo ok || echo missing
doppler secrets get AZURE_SPEECH_REGION -p <project-name> -c <config> >/dev/null 2>&1 && echo ok || echo missing
doppler secrets get OPENAI_API_KEY -p <project-name> -c <config> >/dev/null 2>&1 && echo ok || echo missing
```

Functional validation (making a paid API call) is project-specific and should be implemented as an explicit `verify_integrations` script in the repo that runs with `doppler run -- ...`.

## Reference Links

- Azure Pronunciation Assessment: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-pronunciation-assessment
- Azure Speech region + locale support: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support
- OpenAI Speech-to-Text: https://platform.openai.com/docs/guides/speech-to-text
