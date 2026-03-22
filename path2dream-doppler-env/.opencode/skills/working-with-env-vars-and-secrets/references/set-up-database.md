---
name: set-up-database
description: Neon is recommended Postgress database service. Use when bootstrapping a new project's database, onboarding to an existing Neon project, rotating credentials, or standardizing local/dev/prod DB configuration; relies on reading or creating a repo-local NEON.md.
compatibility: opencode
---

# Set Up Database

## Workflow (Neon via CLI)

### 1) Ensure `neonctl` is installed and up to date

- Check if Neon CLI is installed: run `neonctl --version`.
- If not installed, install it: run `brew install neonctl`.
- If installed, update to the latest version: run `brew upgrade neonctl`.

### 2) Ensure the user is authenticated

- Check auth status: run `neon me`.
- **CRITICAL**: If it fails / indicates not authenticated, **IMMEDIATELY STOP** and ask the user:

```text
⚠️ YOUR ACTION NEEDED

You need to authenticate with Neon CLI.

Please run:
neon auth

After logging in, re-run this skill to continue.
```

- Do NOT attempt any fallbacks, workarounds, or proceed without a real Neon database connection.

### 3) Check for repo-local `NEON.md`

- Look for `NEON.md` in the repo root.

### 4) If `NEON.md` exists, read it and follow it

- Treat `NEON.md` as the source of truth for:
  - Neon project name/id
  - Branch/database name(s)
  - Connection string / required env vars
  - Any conventions (dev/prod separation, migrations, how to rotate credentials)
- Prefer reusing existing Neon resources over creating new ones.

### 5) If `NEON.md` does not exist, bootstrap a new Neon project and write it

- Create a new Neon project via CLI (choose names based on the repo name unless user specifies otherwise).
- Create or select an initial branch/database suitable for development.
- Create `NEON.md` in the repo root documenting at minimum:
  - Project name/id and region
  - Branch/database name(s)
  - How to get a connection string with `neonctl`
  - Which env vars to set (e.g., `DATABASE_URL`)
  - Any separation rules (dev vs prod) and how to add/rotate credentials

### 6) **AGENT RESPONSIBILITY: Retrieve and Store Database URLs**

**CRITICAL: The agent MUST handle database URL setup autonomously. NEVER request database URLs from the user.**

#### Agent Actions Required:

1. **Retrieve database URLs via CLI:**
   - For dev/stage environment: `neonctl connection-string --branch <branch-name>`
   - For production environment: `neonctl connection-string --branch main` (or prod branch)
   - The CLI returns the full `postgresql://...` connection string

2. **Add URLs to Doppler automatically:**
   - Use `doppler secrets set DATABASE_URL="<connection-string>" --config dev` for dev/stage
   - Use `doppler secrets set DATABASE_URL="<connection-string>" --config prd` for production
   - If Doppler is not set up, follow the `working_with_env_vars_and_secrets` skill first

3. **Document the setup in NEON.md:**
   - Include which Doppler configs contain which database URLs
   - Document the branch-to-environment mapping
   - Note: Do NOT include actual connection strings in NEON.md (they're in Doppler)

#### Why This Matters:

- Database URLs contain credentials and should flow directly from Neon CLI → Doppler vault
- Users should never need to copy/paste connection strings manually
- This prevents credential leakage and ensures proper secret management
- The agent has CLI access to both `neonctl` and `doppler`, making this fully automatable
