# Awake

A small macOS keep-awake service for builds, tests, and local agents. Python
3.9+ and macOS's built-in `caffeinate` are the only requirements. No packages
to download, network service, account, or Codex installation is required.

## Install from copilot-prompts

From the repository root:

```sh
./scripts/install-awake.sh
# Optional Codex task detection and display activity:
./scripts/install-awake.sh --codex --codex-mode active
```

The helper uses `--ensure`: it reuses a recognized version 0.1.0 installation,
can add the optional adapter, and preserves its mode unless explicitly changed.
It starts the requested services, but does not overwrite installed code or
upgrade it automatically. To upgrade package code, uninstall and reinstall.

## Install on another Mac

Copy and extract `awake-0.1.0.tar.gz`, then run:

```sh
cd awake-0.1.0
python3 install.py
~/.local/bin/awake status
```

This installs into `~/.local/share/awake`, creates `~/.local/bin/awake`, and
starts a per-user login service. To use `awake` without the full path, add
`export PATH="$HOME/.local/bin:$PATH"` to your shell configuration if needed.
The installer generates paths for the current machine; don't copy installed
LaunchAgent plist files between machines. No administrator privileges needed.

For automatic detection across VS Code Codex windows, choose this install
command instead:

```sh
python3 install.py --codex --codex-mode active
```

Codex is optional and runs in a separate adapter process. To add or configure an adapter in an existing installation, pass `--ensure`
with the desired flags. Without `--ensure`, existing files are never overwritten.

## Use with any command

```sh
awake run -- make test
awake run --mode display -- python3 long_job.py
awake run --mode active -- ./build.sh
```

| Mode | Behavior |
| --- | --- |
| `system` (default) | Prevent idle system sleep; display and lock timers can operate normally |
| `display` | Also prevent idle display sleep |
| `active` | Also renew macOS user activity to discourage ordinary idle locking |

The wrapper preserves command exit codes, forwards termination signals to the
command's process group, and releases its lease when the foreground command
exits. It is intended for foreground noninteractive jobs such as builds and
tests, not interactive shells or commands that detach their work into the
background. It never records command arguments.

Keep the laptop lid open. No mode unlocks an already locked screen, changes
password settings, or overrides managed lock policies. Releasing a lease
restores normal timers; it does not force immediate sleep or locking.

## Controls

```sh
awake status
awake stop
awake start
awake adapter codex stop
awake adapter codex start
python3 ~/.local/share/awake/install.py --uninstall
```

`stop` disables the core service at future logins as well as stopping it now.
The optional adapter has its own start/stop control. It can remain running
while the core is stopped, but cannot keep the machine awake until the core
starts again. `status` queries the live service and shows leases, their remaining
lifetimes, the combined mode, and whether its `caffeinate` child is alive.

Logs live in `~/.local/share/awake/{service,codex}{,.err}.log` and contain only
operational state. The service listens on an owner-only local Unix socket.

## Integrate another tool

Acquire a lease, renew it before its lifetime elapses, and release it when done:

```sh
lease_id=$(awake lease acquire --label "local test job" --ttl 30)
awake lease renew "$lease_id" --label "local test job" --ttl 30
awake lease release "$lease_id"
```

Renew every 10 seconds for a 30-second lease. Clients must keep the same UUID
and resend the label, mode, and TTL on renewal. Each independent task gets its
own lease; releasing one never releases another. If a client crashes, its
lease expires automatically. TTL must be an integer from 1 to 300 seconds.

The local socket protocol accepts one JSON line per connection (maximum 4096
bytes), then returns one JSON response. The socket is
`~/.local/share/awake/awake.sock`; `AWAKE_HOME` overrides this for isolated tests.

```json
{"op":"renew","id":"00000000-0000-4000-8000-000000000001","label":"local job","mode":"system","ttl":30}
{"op":"release","id":"00000000-0000-4000-8000-000000000001"}
{"op":"status"}
```

Responses have `ok: true`, `mode`, `leases`, and `power_active`, or `ok: false`
and an `error`. Release is idempotent. Renew also acquires the lease, allowing
clients to recover after service restart. Leases live only in service memory
and use a monotonic clock. At most 128 leases can be active concurrently.

## How it works

The service combines all unexpired leases and chooses the strongest requested
mode. It renews a 45-second `caffeinate` assertion every 20 seconds and ties it
to its own PID. No leases means the assertion is released within about one
second. On service restart, clients must renew their leases; the command
wrapper retries automatically, with a brief unprotected interval possible.

The optional Codex adapter checks every five seconds and holds one aggregated
30-second lease while any VS Code turn is active, including turns waiting for
input. It adds a 15-second idle grace period. It reads local lifecycle metadata
and checks the owning process's start time to exclude stale/crashed sessions.
It does not retain conversation text. Other adapters do not need to know
anything about Codex.

The Codex adapter was verified against extension version
`26.1007.21434-darwin-arm64`. It uses private session/lock formats and
`state_5.sqlite`, so extension updates may require adapter changes. Detection
errors stop lease renewal and are recorded in the adapter log. The generic
service and wrapper are unaffected by Codex format changes.

## Validate

```sh
python3 -m unittest discover -s . -v
```

Tests cover overlapping leases, expiry, modes, input validation, process signal
forwarding, exit codes, failed command launches, and service restart recovery.
Core integration tests run without Codex modules present and briefly create
real macOS power assertions. Adapter tests use synthetic session files.

Windows and Linux power backends are not implemented in version 0.1.0.
