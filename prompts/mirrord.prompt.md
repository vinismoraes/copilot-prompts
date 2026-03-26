---
description: Run mirrord to test a local app against a remote environment
---

# Mirrord Testing

Run mirrord to test your local code against a remote environment.

Default configuration:
- **App**: messaging
- **Env**: test2-ca
- **MIRRORD_ROUTE**: empty (exclusive env usage)

## Steps

1. Set `MIRRORD_ROUTE` to empty to skip the interactive prompt
2. Run `./run_with_mirrord.sh` from `src/el/` with the app and env

Run this command in the terminal as a background process (it stays running):

```bash
cd ~/GoProjects/services/src/el && MIRRORD_ROUTE= ./run_with_mirrord.sh messaging test2-ca
```

If the user specifies a different app or env, substitute accordingly.
The script handles gcloud auth, kubectl context switching, building with `-tags=cse,mirrord`, and `mirrord exec`.
