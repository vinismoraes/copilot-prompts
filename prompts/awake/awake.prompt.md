---
description: Set up or inspect optional macOS keep-awake automation
---

Use the Awake tool in this copilot-prompts checkout (`scripts/awake/README.md`).
For setup, run `./scripts/install-awake.sh`; if the user requested automatic
Codex turn detection, add `--codex`. Add `--codex-mode active` only when the
user wants display activity as well. Setup is idempotent and starts the
per-user login service.

For an installed tool, use `~/.local/bin/awake status`, `start`, or `stop` as
requested. The optional adapter has separate `adapter codex start` and
`adapter codex stop` controls. Report active leases and any errors. Never stop
the entire service just to finish one command or conversation.

For foreground jobs, prefer `awake run -- command args`. Explain that Codex
turn detection is optional and separate; Copilot/Claude commands can use the
generic wrapper without Codex installed.
