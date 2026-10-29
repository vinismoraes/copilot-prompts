"""Verify fresh installs, managed upgrades, and custom-instruction protection."""
from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('codex_installer', Path(__file__).with_name('install.py'))
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)

PREVIOUS_OVERRIDE = "# Codex working instructions\n\nInstalled by `copilot-prompts/scripts/install.sh --codex-efficiency`. Keep any generated `AGENTS.md` intact. Follow the current repository's `AGENTS.md` and load linked guidance only when the task calls for it.\n\n## Work across repositories\n\n- Follow repository instructions for coding conventions, tests, data handling, and release rules.\n- Keep context focused: read the files and guidance needed for the task, and summarize large tool results.\n- Before committing or pushing, show the changed files and a proposed one-line commit message and wait for approval. Never amend a pushed commit. After approval, commit and push together. Read `$CODEX_HOME/guidance/git-push.instructions.md` and `$CODEX_HOME/guidance/git-commits.instructions.md` when relevant.\n- Before posting a PR comment, show the draft and wait for approval. Read `$CODEX_HOME/guidance/pr-comments.instructions.md` when relevant.\n- For Go implementation, read `$CODEX_HOME/guidance/go-standards.instructions.md`.\n\n## Build only what the task needs\n\nFor each task, use this scope check without adding a separate planning turn for routine work:\n1. Identify the current outcome and how to verify it.\n2. Reuse existing code and tools; make the smallest change that satisfies the current requirements, including necessary tests and safety checks.\n3. Add an abstraction, automation, agent handoff, or report only when a current requirement, concrete risk, or observed repeated friction justifies it. Name that reason when adding one.\n4. Once the outcome is verified, stop. Leave speculative improvements unbuilt; note one briefly only if it will help later.\n\n## Agent-driven routing\n\nFor each coding task, decide whether to complete it directly or delegate one bounded, independent part. Prefer direct work for short or sequential tasks. Use `cost_explorer` for focused codebase searches that can return a concise file-and-symbol map. Use `quality_reviewer` after implementation when correctness, data handling, concurrency, or contract changes warrant independent review. Spawn at most two specialists at once; do not duplicate the same investigation. Choose the least costly role likely to meet the task's quality bar, then verify the result yourself. Mention the routing choice and any remaining uncertainty in the final report.\n"


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.codex = self.home / '.codex'
        self.codex.mkdir()

    def install(self):
        with redirect_stdout(io.StringIO()):
            installer.install(self.home, True, False)

    def test_fresh_install_includes_journaling_and_workflow(self):
        self.install()
        for name in ('obsidian-journaling', 'task-workflow'):
            p = self.codex / 'guidance' / (name + '.instructions.md')
            self.assertTrue(p.is_symlink() and p.exists())
        self.assertIn('linked daily completion entry', (self.codex / 'AGENTS.override.md').read_text())

    def test_previous_managed_override_upgrades_with_backup(self):
        p = self.codex / 'AGENTS.override.md'
        p.write_text(PREVIOUS_OVERRIDE)
        self.install()
        self.assertIn('linked daily completion entry', p.read_text())
        backups = list(self.codex.glob('AGENTS.override.md.backup-*'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), PREVIOUS_OVERRIDE)
        self.install()
        self.assertEqual(len(list(self.codex.glob('AGENTS.override.md.backup-*'))), 1)

    def test_custom_override_remains_protected(self):
        p = self.codex / 'AGENTS.override.md'
        custom = PREVIOUS_OVERRIDE + '\nMy custom rule.\n'
        p.write_text(custom)
        with self.assertRaises(SystemExit):
            self.install()
        self.assertEqual(p.read_text(), custom)
        self.assertFalse((self.codex / 'guidance').exists())


if __name__ == '__main__':
    unittest.main()
