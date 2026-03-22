# Secrets management
- All secrets are managed through `doppler` envs
- So if you need to run something with env vars available, run it through doppler, for example `doppler run -c dev -- uv run ...`
- Also, the doppler has different levels of environment configured (dev/stg). Use appropriate for use case environment.
- The list of available environments and env vars configured in each of them can be found in file `docs/ENV_VARS.md`
