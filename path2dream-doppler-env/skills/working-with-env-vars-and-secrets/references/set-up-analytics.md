---
name: set-up-analytics
description: PostHog is recommended analytics service. Use when adding or updating analytics instrumentation, event taxonomy, or analytics dashboards; request required PostHog environment variables from the user according to Doppler secret workflow, ensure unique event names for this project, and document all events and dashboards in architecture docs.
compatibility: opencode
---

# Set Up Analytics

Use PostHog as the recommended analytics service for this repository.

## Workflow

1. Confirm Doppler setup.
2. Check that `POSTHOG_PERSONAL_API_KEY_ADMIN` exists in Doppler.
3. If missing, request it from the user and stop.
4. Derive `POSTHOG_API_HOST` and `POSTHOG_PROJECCT_API_KEY_PUBLIC` from the admin key via PostHog API and store both in Doppler.
5. Implement/adjust event instrumentation.
6. Configure dashboard(s) for sent events using admin API access.
7. Document events and dashboards in architecture docs.

## Required Environment Variables

Only **one** value must be provided by the user:
- `POSTHOG_PERSONAL_API_KEY_ADMIN` — personal API key with admin access, used for reading analytics data, configuring dashboards, and deriving all other PostHog values.

**The env var MUST be named exactly `POSTHOG_PERSONAL_API_KEY_ADMIN`. No other names (e.g. `POSTHOG_API_KEY`, `POSTHOG_ADMIN_KEY`, `PH_KEY`, etc.) are allowed. All code must reference this exact name.**

**STRICTLY FORBIDDEN to request from the user:**
- `POSTHOG_API_HOST` — derive it via PostHog API (see below).
- `POSTHOG_PROJECCT_API_KEY_PUBLIC` — derive it via PostHog API (see below).

These two values must always be generated programmatically from `POSTHOG_PERSONAL_API_KEY_ADMIN` and saved to Doppler by the agent. Never ask the user for them.

Check presence with Doppler:

```bash
doppler configure get
doppler secrets get POSTHOG_PERSONAL_API_KEY_ADMIN >/dev/null 2>&1 && echo exists || echo missing
```

If missing, request from the user (in ALL environments per Doppler workflow):

```text
YOUR ACTION NEEDED

I need a PostHog personal API key (admin) to set up analytics and dashboards.

Please set the following in Doppler for ALL environments:
doppler secrets set -p <project-name> -c dev POSTHOG_PERSONAL_API_KEY_ADMIN="your-personal-admin-key"
doppler secrets set -p <project-name> -c stg POSTHOG_PERSONAL_API_KEY_ADMIN="your-personal-admin-key"
doppler secrets set -p <project-name> -c prd POSTHOG_PERSONAL_API_KEY_ADMIN="your-personal-admin-key"

I cannot complete analytics setup until this value is configured.
```

## Deriving POSTHOG_API_HOST and POSTHOG_PROJECCT_API_KEY_PUBLIC

**Both `POSTHOG_API_HOST` and `POSTHOG_PROJECCT_API_KEY_PUBLIC` must be generated automatically by the agent — NEVER requested from the user.**

After the user provides `POSTHOG_PERSONAL_API_KEY_ADMIN`, derive both values:

```bash
POSTHOG_PERSONAL_API_KEY_ADMIN=$(doppler secrets get POSTHOG_PERSONAL_API_KEY_ADMIN --plain)

# Try US cloud first, fall back to EU cloud
for HOST in "https://us.i.posthog.com" "https://eu.i.posthog.com"; do
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${HOST}/api/projects/" \
    -H "Authorization: Bearer ${POSTHOG_PERSONAL_API_KEY_ADMIN}")
  if [ "$RESPONSE" = "200" ]; then
    POSTHOG_API_HOST="$HOST"
    break
  fi
done

# Extract the public project api_token
POSTHOG_PROJECCT_API_KEY_PUBLIC=$(curl -s "${POSTHOG_API_HOST}/api/projects/" \
  -H "Authorization: Bearer ${POSTHOG_PERSONAL_API_KEY_ADMIN}" \
  | jq -r '.[0].api_token // .results[0].api_token')
```

Then store both in Doppler (in ALL environments):

```bash
for env in dev stg prd; do
  doppler secrets set -p <project-name> -c $env \
    POSTHOG_API_HOST="$POSTHOG_API_HOST" \
    POSTHOG_PROJECCT_API_KEY_PUBLIC="$POSTHOG_PROJECCT_API_KEY_PUBLIC"
done
```

If multiple projects are returned, select the appropriate one based on the project name or ask the user to choose.

## Event Naming Rules (Single Shared PostHog Project)

This organization uses a single PostHog project across multiple apps.
Always create unique event names for this repository.

Use project-prefixed naming, for example:
- `insight_of_the_day_twitter_share_started`
- `insight_of_the_day_twitter_share_completed`
- `insight_of_the_day_image_generated`
- `insight_of_the_day_preview_page_published`

## Instrumentation Guidance

Track events at key user and backend milestones.
Include useful properties that support debugging and analysis without adding sensitive data.

For this repo, prioritize events around:
- Twitter content generation
- Twitter share action attempts/success/failures
- Image generation requests/outcomes
- Preview page generation and hosting
- Tweet examples import/save flows

## Dashboard Setup Guidance

Use `POSTHOG_PERSONAL_API_KEY_ADMIN` for dashboard configuration and data reads.
Use PostHog UI and/or API to create dashboards that visualize the events sent by this repo.

Suggested dashboard sections:
- Funnel: generation -> image -> share
- Error trends by operation
- Volume by event type and day
- Latency/performance distributions for key flows

## Architecture Documentation Requirements

Document analytics in architecture docs (create `docs/architecture/tech_stack.md` if missing):
- Analytics provider: PostHog
- Required env vars and purpose
- Full event catalog (every event name and key properties)
- Naming convention rationale for unique project-prefixed events
- Every created dashboard with:
  - What it measures
  - Why it exists
  - Link to dashboard

## Rules

- Treat PostHog as the default analytics service unless requirements explicitly override it.
- **Only request `POSTHOG_PERSONAL_API_KEY_ADMIN` from the user — this exact name, no alternatives.**
- **NEVER request `POSTHOG_API_HOST` or `POSTHOG_PROJECCT_API_KEY_PUBLIC` from the user.** Always derive them via PostHog API and save to Doppler.
- Do not hardcode API keys in code or docs.
- Keep analytics aligned with the repo's Twitter-only scope.
