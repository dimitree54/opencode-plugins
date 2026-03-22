# Syncing Doppler Secrets to GitHub Actions

When a GitHub Actions workflow needs secrets (e.g., `PYPI_API_TOKEN` for publishing, API keys for deployment), use Doppler's native GitHub integration to auto-sync them — do **not** manually copy secrets into GitHub.

## Setup Steps

1. **Open the Doppler dashboard** → navigate to your project (e.g., `tg_auto_test`) → **Integrations** → select **GitHub**.
2. **Authorize the Doppler GitHub App** on the target GitHub account/org and grant access to the repository.
3. **Create a sync** with the following settings:
   - **Feature**: Actions
   - **Repository**: the target repo (e.g., `tg_auto_test`)
   - **Environment**: match the GitHub Actions `environment:` value in your workflow (e.g., `release`)
   - **Config**: the Doppler config where the secret lives (e.g., `prd` for production tokens)
4. Click **Set Up Integration**.

After setup, Doppler automatically syncs the selected config's secrets into the specified GitHub environment's secrets. Any future changes in Doppler auto-sync to GitHub — no manual updates needed.

## How It Works

- Doppler pushes secrets to **GitHub environment secrets** (not plain repo secrets), so your workflow must declare `environment: <name>` in the job.
- Only secrets from the selected Doppler config are synced. Choose the config that matches the workflow's purpose (typically `prd` for release/deploy workflows).
- Secrets appear in GitHub under **Settings → Environments → \<name\> → Environment secrets**.

## Example Workflow Reference

```yaml
jobs:
  release:
    runs-on: ubuntu-latest
    environment: release          # ← must match the Doppler sync target
    steps:
      - uses: actions/checkout@v4
      - name: Publish
        env:
          PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}  # ← auto-synced by Doppler
        run: ...
```

## Troubleshooting

- **Secret not available in workflow**: Verify the job has `environment: <name>` and that the Doppler sync targets that exact environment name.
- **Sync not updating**: Check the Doppler Integrations page for sync status/errors. Re-authorize the GitHub App if permissions changed.
- **Wrong secrets synced**: Confirm you selected the correct Doppler config (dev/stg/prd) when creating the sync.
