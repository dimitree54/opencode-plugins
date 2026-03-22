---
name: working-with-env-vars-and-secrets
description: Skill describing how to add new env vars. This is protected skill, use it only if explicitly allowed by user or by your instructions.
---

# Working with Environment Variables and Secrets

All projects use **Doppler CLI** for managing environment variables and secrets. We do not use `.env` files or `.env.template` files.

## References

| File | Purpose |
| --- | --- |
| [`references/set-up-analytics.md`](references/set-up-analytics.md) | Reference for configuring analytics-related environment variables and secrets. |
| [`references/set-up-content-generation.md`](references/set-up-content-generation.md) | Reference for configuring content generation services and related variables. |
| [`references/set-up-database.md`](references/set-up-database.md) | Reference for setting up database credentials and connection variables. |
| [`references/set-up-file-storage.md`](references/set-up-file-storage.md) | Reference for configuring file storage providers and required variables. |
| [`references/set-up-github-secrets.md`](references/set-up-github-secrets.md) | Reference for exposing Doppler-managed secrets to GitHub Actions workflows. |
| [`references/set-up-monitoring.md`](references/set-up-monitoring.md) | Reference for configuring monitoring and observability services. |
| [`references/set-up-speech-services.md`](references/set-up-speech-services.md) | Reference for configuring speech and audio-related services. |
| [`references/set-up-telegram-bot`](references/set-up-telegram-bot) | Reference directory for Telegram bot setup and related secret management. |

## Core Concepts

- **Doppler Project**: Named after the repository/project name. Contains all environment variables and secrets.
- **Environments**: Each project has three environments: `dev`, `stg`, `prd`.
- **Secrets vs Non-Secrets**: Both are stored in Doppler. "Secrets" in Doppler terminology means all environment variables.

## Checking Current Configuration

### Check if Doppler project exists
```bash
doppler projects get <project-name> >/dev/null 2>&1 && echo exists || echo missing
```

### Check current setup
```bash
# Show current project and environment
doppler configure get

# List all variables in current environment
doppler secrets
```

### Get a specific variable
```bash
doppler secrets get KEY_NAME
```

## Setting Up a New Project

### 1. Create Doppler project
```bash
doppler projects create <project-name>
```

### 2. Configure environment
```bash
# Set up for development
doppler setup -p <project-name> -c dev

# Or for staging/production
doppler setup -p <project-name> -c stg
doppler setup -p <project-name> -c prd
```

This creates a `.doppler.yaml` file in the project root that remembers your configuration.

## Adding Environment Variables

**IMPORTANT: Always set variables in ALL environments (dev, stg, prd), not just the current one.** When you are responsible for setting a variable, you must configure it in every vault. Use the `-p` and `-c` flags to target each environment explicitly:

```bash
# Set in ALL environments — do this for every variable you add
doppler secrets set -p <project-name> -c dev  KEY="value"
doppler secrets set -p <project-name> -c stg  KEY="value"
doppler secrets set -p <project-name> -c prd  KEY="value"
```

### Non-secret configuration values
You can add these **autonomously** without asking the user:
- Port numbers
- Timeout values
- Model names
- Bucket names
- API endpoints (URLs)
- Feature flags
- Environment names
- Log levels
- Any other configuration that isn't sensitive

```bash
# Example: set in ALL three environments
doppler secrets set -p my-project -c dev PORT="8080" MODEL_NAME="gpt-4" TIMEOUT_MS="5000"
doppler secrets set -p my-project -c stg PORT="8080" MODEL_NAME="gpt-4" TIMEOUT_MS="5000"
doppler secrets set -p my-project -c prd PORT="8080" MODEL_NAME="gpt-4" TIMEOUT_MS="5000"
```

### Secret values (API keys, passwords, tokens)
For these, you must **halt and ask the user** to set them:
- API keys
- Database passwords
- Auth tokens
- Encryption keys
- Service account credentials
- OAuth secrets

**How to request from user (instruct them to set in ALL environments):**
```
I need credentials for [service name] to [reason why].

Please set the following in Doppler for ALL environments:
doppler secrets set -p <project-name> -c dev API_KEY="your-key-here"
doppler secrets set -p <project-name> -c stg API_KEY="your-key-here"
doppler secrets set -p <project-name> -c prd API_KEY="your-key-here"

I cannot proceed with [integration name] until this is configured.
```

## Modifying Environment Variables

**IMPORTANT: When modifying variables, update ALL environments (dev, stg, prd).**

### Non-secret values
You can modify these **autonomously** — but in every environment:
```bash
# Change a timeout in ALL environments
doppler secrets set -p my-project -c dev TIMEOUT_MS="10000"
doppler secrets set -p my-project -c stg TIMEOUT_MS="10000"
doppler secrets set -p my-project -c prd TIMEOUT_MS="10000"
```

### Secret values
You must **ask the user** to modify these — and remind them to update ALL environments:
```
The [service name] API key needs to be updated.

Please update the following in Doppler for ALL environments:
doppler secrets set -p <project-name> -c dev API_KEY="new-key-here"
doppler secrets set -p <project-name> -c stg API_KEY="new-key-here"
doppler secrets set -p <project-name> -c prd API_KEY="new-key-here"

Reason: [explain why it needs to change]
```

**Never modify secrets autonomously**, even if they appear invalid or expired. Always ask the user.

## Deleting Environment Variables

Delete from **ALL environments**:
```bash
doppler secrets delete -p <project-name> -c dev KEY_NAME
doppler secrets delete -p <project-name> -c stg KEY_NAME
doppler secrets delete -p <project-name> -c prd KEY_NAME
```

Only delete variables you're certain are no longer needed. For secrets, confirm with the user first.

## Running Applications

All commands that need environment variables must run with `doppler run`:

```bash
# Python
doppler run -- uv python app.py
doppler run -- python manage.py runserver

# Node.js
doppler run -- npm run dev
doppler run -- node server.js

# Tests
doppler run -- pytest
doppler run -- npm test

# Any command
doppler run -- <your-command>
```

Doppler automatically injects all environment variables when running the command.

## File-Based Secrets

For secrets that are files (GCP service account JSON, certificates, SSH keys):

### 1. Store file contents in Doppler
Store the entire file content as a secret:
```bash
doppler secrets set GCP_SERVICE_ACCOUNT="$(cat gcp-sa.json)"
```

### 2. Mount when running
```bash
doppler run --mount ./gcp-sa.json -- npm run dev
```

The `--mount` flag writes the secret to the specified path before running the command.

### 3. Multiple file secrets
```bash
doppler run --mount ./gcp-sa.json --mount ./cert.pem -- npm start
```

## Environment-Specific Configuration

Switch between environments as needed:

```bash
# Work on dev environment
doppler setup -p my-project -c dev
doppler run -- npm run dev

# Switch to staging
doppler setup -p my-project -c stg
doppler run -- npm run build

# Switch to production
doppler setup -p my-project -c prd
doppler run -- npm start
```

## Validation

### Check that a variable exists
```bash
doppler secrets get KEY_NAME >/dev/null 2>&1 && echo exists || echo missing
```

### Validate credentials work
Create a simple validation script that makes a non-destructive API call:

```bash
# Example: validate OpenAI API key
doppler run -- python -c "import openai; print(openai.models.list())"

# Example: validate database connection
doppler run -- python -c "import psycopg2; conn = psycopg2.connect()"
```

Always validate credentials after they're set to ensure they work.

## Common Patterns

### Setting multiple variables at once (in all environments)
```bash
for env in dev stg prd; do
  doppler secrets set -p my-project -c $env \
    PORT="8080" \
    MODEL_NAME="gpt-4" \
    TIMEOUT_MS="5000" \
    LOG_LEVEL="info"
done
```

### Copying a variable to all environments
```bash
VALUE=$(doppler secrets get -p my-project -c dev KEY_NAME --plain)
doppler secrets set -p my-project -c stg KEY_NAME="$VALUE"
doppler secrets set -p my-project -c prd KEY_NAME="$VALUE"
```

### Backup current configuration
```bash
doppler secrets download > backup.json
```

## Troubleshooting

### "No project configured"
Run `doppler setup -p <project-name> -c dev` to configure the project.

### "Secret not found"
List all secrets with `doppler secrets` to see what's available.

### Application can't find variables
Make sure you're running with `doppler run --` prefix.

### Wrong environment
Check current setup with `doppler configure get` and switch if needed.

## Rules Summary

✅ **DO:**
- Use Doppler CLI for all environment variables
- **Set variables in ALL environments (dev, stg, prd)** — never just one
- Set non-secret config values autonomously
- Run all commands with `doppler run --`
- Validate credentials after setting them
- When asking user to set secrets, instruct them to set in all environments

❌ **DON'T:**
- Create `.env` or `.env.template` files
- Store secrets in code or documentation
- Modify secret values without asking user
- Run applications without `doppler run --`
- Commit `.env` files (we don't use them)
- **Set a variable in only one environment** — always set in dev, stg, AND prd

## GitHub Actions Secrets

If you need to make Doppler secrets available to GitHub Actions workflows (e.g., `PYPI_API_TOKEN` for publishing), read the [GitHub Secrets guide](github-secrets.md) for setup instructions using Doppler's native GitHub integration.

# Document available secrets
All projects, environments, var names you configured should be listed in `docs/ENV_VARS.md` file. Of the repo.
