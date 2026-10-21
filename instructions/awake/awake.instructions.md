---
applyTo: "**"
description: Use an installed Awake service automatically for long foreground commands on macOS
---

# Keep awake during long commands

Awake is an optional local macOS tool. The installer starts it at login;
agents do not need to run a keep-awake loop or launch another daemon per window.

- At the first long-running command in a session, check whether `awake` is
  available on PATH, falling back to `~/.local/bin/awake`, and run its `status`
  command once. If it is absent or stopped, run the original command normally.
  Do not install it or reverse an explicit stop without a user request.
- When the service is available, automatically wrap foreground builds, tests,
  benchmarks, and other noninteractive commands expected to take roughly a
  minute or more: `awake run -- command args`. Use the resolved executable path.
  Routine wrapping needs no separate confirmation.
- Default to `system` mode, which prevents idle system sleep. Use
  `awake run --mode active -- command args` only when the user requested keeping
  the display active as well. This does not override managed lock policies.
- For shell pipelines or compound commands, wrap the shell that runs the whole
  job, preserving the project's shell/environment and quoting. Keep credentials
  in environment variables; never interpolate their values into a command.
- The wrapper releases its own lease when the command exits. Do not run
  `awake stop`, kill all `caffeinate` processes, or release another task's lease
  when your command finishes: other windows may still be working.
- Do not wrap interactive shells, detached jobs, or an already wrapped command.
  Do not keep renewing a manual lease merely because an editor window is open.
- If Awake itself fails before launching the command, report that keep-awake is
  unavailable and run the original command. Do not blindly retry a command that
  actually started and failed: the wrapper preserves its exit code.

The optional Codex adapter already tracks active turns across VS Code windows.
These instructions automate foreground commands for Copilot and Claude; they
do not detect either assistant's complete reasoning/turn lifecycle.
