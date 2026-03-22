---
name: set-up-monitoring
description: Sentry is recommended monitoring service. Use when adding or updating error tracking, performance monitoring, release tracking, or monitoring-related environment setup; verify SENTRY_API_KEY via Doppler, request it from the user if missing, derive ALL other Sentry values (DSN, project keys, org slug) via API — never ask the user for them — ensure a Sentry project exists (create if needed), and document monitoring configuration in architecture docs.
compatibility: opencode
---

# Set Up Monitoring

Use Sentry as the recommended monitoring platform for this repository.

## Request from user SENTRY_API_KEY

`SENTRY_API_KEY` (Sentry auth token) is the **only** secret the agent should ever request from the user. All other Sentry values — including `SENTRY_DSN`, project client keys, org slug, project slug — **must be derived programmatically** by the agent using the Sentry API with the auth token. Never ask the user for `SENTRY_DSN` or any other Sentry credential.

## Workflow

1. Confirm Doppler configuration and check whether `SENTRY_API_KEY` exists.
2. If `SENTRY_API_KEY` is missing, stop and request the user to set it.
3. Authenticate `sentry-cli` with the token.
4. Discover org slug via API (do not ask user).
5. Check whether the target Sentry project exists.
6. If the project does not exist, create it.
7. Retrieve SENTRY_DSN and other project keys via API (do not ask user).
8. Store derived secrets in Doppler autonomously.
9. Configure monitoring and event coverage in code.
10. Document the Sentry project name and setup in architecture docs.

## Step 1: Check Secret in Doppler

Always use Doppler patterns from `$working_with_env_vars_and_secrets`.

```bash
doppler configure get
doppler secrets get SENTRY_API_KEY >/dev/null 2>&1 && echo exists || echo missing
```

## Step 2: Request Secret if Missing

`SENTRY_API_KEY` is the **only** secret that requires user action. Do not ask for `SENTRY_DSN`, org slug, project slug, or any other Sentry value — derive them all from the API key.

Use this request text:

```text
⚠️ YOUR ACTION NEEDED

I need a Sentry auth token to set up monitoring.

Please set the following in Doppler:
doppler secrets set SENTRY_API_KEY="your-sentry-auth-token"

This is the ONLY Sentry secret I need from you. I will automatically
discover your org, create/find the project, and retrieve the DSN and
all other credentials using this token.

I cannot proceed with Sentry setup until this is configured.
```

## Step 3: Authenticate sentry-cli

Run all commands through Doppler so secrets are injected:

```bash
doppler run -- sentry-cli login --auth-token "$SENTRY_API_KEY"
```

If interactive login is unavailable in CI/non-interactive environments, use environment-based auth in command invocations.

## Step 4: Discover Org Slug via API

The agent must discover the org slug automatically — never ask the user for it.

```bash
doppler run -- curl -sS \
  -H "Authorization: Bearer $SENTRY_API_KEY" \
  "https://sentry.io/api/0/organizations/"
```

Parse the response to extract the org slug. If the user belongs to multiple orgs, pick the first one or ask which org to use.

## Step 5: Check Project Existence

Prefer CLI first:

```bash
doppler run -- sentry-cli projects list --org <org-slug>
```

Check whether `<project-slug>` exists in that list.

Optional API check (when CLI output is insufficient):

```bash
doppler run -- curl -sS \
  -H "Authorization: Bearer $SENTRY_API_KEY" \
  "https://sentry.io/api/0/projects/<org-slug>/<project-slug>/"
```

## Step 6: Create Project if Missing

Create with CLI:

```bash
doppler run -- sentry-cli projects create \
  --org <org-slug> \
  --platform python \
  <project-slug>
```

If team-specific creation is required, use Sentry API with `curl` and the correct org/team endpoint.

## Step 7: Retrieve SENTRY_DSN and Project Keys via API

After the project exists, the agent **must** retrieve the DSN and client keys automatically. Never ask the user for these.

```bash
doppler run -- curl -sS \
  -H "Authorization: Bearer $SENTRY_API_KEY" \
  "https://sentry.io/api/0/projects/<org-slug>/<project-slug>/keys/"
```

Parse the response to extract:
- `dsn.public` → this is the `SENTRY_DSN`
- `dsn.secret` → secret DSN (if needed)
- `id` → key ID

## Step 8: Store Derived Secrets in Doppler

The agent should autonomously store the derived values in Doppler so application code can access them:

```bash
doppler secrets set SENTRY_DSN="<extracted-dsn-public>"
doppler secrets set SENTRY_ORG="<org-slug>"
doppler secrets set SENTRY_PROJECT="<project-slug>"
```

These are **not user-provided secrets** — they are derived from `SENTRY_API_KEY` and the agent sets them without user intervention.

## Step 9: Configure Monitoring and Events

Set up at minimum:
- Unhandled exception capture
- Structured error context (request/user/tool identifiers when available)
- Performance tracing for key request paths
- Release tracking for deploy correlation
- Alerting rules for high-severity errors

For this repo, prioritize events around:
- Twitter share flow
- Image generation flow
- Preview page generation/hosting
- Tweet examples import/save APIs

## Step 10: Document in Architecture Docs

After project verification/creation, document in architecture docs (create `docs/architecture/tech_stack.md` if missing):
- Monitoring service: Sentry
- Sentry org slug
- Sentry project slug/name
- Environment mapping (dev/stg/prd)
- Required env vars: `SENTRY_API_KEY` (user-provided), `SENTRY_DSN` / `SENTRY_ORG` / `SENTRY_PROJECT` (agent-derived)
- High-level event coverage and alerting policy

## Rules

- Treat Sentry as the default monitoring provider unless new requirements explicitly override it.
- **`SENTRY_API_KEY` is the ONLY secret the agent asks the user for.** All other Sentry values (`SENTRY_DSN`, org slug, project slug, client keys) must be derived by the agent via the Sentry API using the auth token.
- Never ask the user for `SENTRY_DSN`, org slug, project slug, or any other Sentry credential.
- The agent must store derived values (DSN, org, project) in Doppler autonomously after retrieving them.
- Do not hardcode tokens in code, docs, or commands saved in history files.
- Keep monitoring setup aligned with the repo's Twitter-only product scope.
