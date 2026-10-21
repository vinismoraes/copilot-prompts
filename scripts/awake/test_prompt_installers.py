"""Exercise installer flags with fixture output directories and a fake setup helper."""
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest


@unittest.skipUnless(shutil.which('zsh'), 'prompt installers require zsh')
class PromptInstallerTests(unittest.TestCase):
    def exercise(self, installer, flags, expected):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            scripts = root / 'scripts'
            scripts.mkdir()
            for pack in ['core', 'awake']:
                (root / 'instructions' / pack).mkdir(parents=True)
                (root / 'prompts' / pack).mkdir(parents=True)
            (root / 'instructions/awake/awake.instructions.md').write_text('awake fixture')
            (root / 'prompts/awake/awake.prompt.md').write_text('awake prompt')
            helper = scripts / 'install-awake.sh'
            calls = root / 'calls'
            helper.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> ' + shlex.quote(str(calls)) + '\n')
            helper.chmod(0o755)
            source = Path(__file__).resolve().parents[1] / installer
            if not source.exists():
                self.skipTest('run this test from the copilot-prompts checkout')
            text = source.read_text()
            # Redirect only filesystem destinations; leave HOME and host config untouched.
            output = root / 'output'
            output.mkdir()
            if installer == 'install.sh':
                text = text.replace('PROMPTS_DIR="$HOME/Library/Application Support/Code/User/prompts"',
                                    'PROMPTS_DIR=' + shlex.quote(str(output)))
                text = text.replace('PROMPTS_DIR="$HOME/.config/Code/User/prompts"',
                                    'PROMPTS_DIR=' + shlex.quote(str(output)))
                instruction = output / 'awake.instructions.md'
            else:
                text = text.replace('CLAUDE_DIR="$HOME/.claude"', 'CLAUDE_DIR=' + shlex.quote(str(output)))
                instruction = output / 'instructions/awake.instructions.md'
                (output / 'CLAUDE.md').write_text('before\n<!-- BEGIN AUTO-INSTALLED INSTRUCTIONS -->\n<!-- END AUTO-INSTALLED INSTRUCTIONS -->\nafter\n')
            target = scripts / installer
            target.write_text(text)
            result = subprocess.run(['zsh', str(target), *flags], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            if expected is None:
                self.assertFalse(calls.exists())
            else:
                self.assertEqual(calls.read_text(), expected + '\n')
            self.assertEqual(instruction.is_symlink(), bool(flags))
            if installer == 'claude-install.sh' and flags:
                imports = (output / 'CLAUDE.md').read_text()
                self.assertIn('@instructions/awake.instructions.md', imports)
                self.assertTrue(imports.startswith('before\n'))
                self.assertTrue(imports.endswith('after\n'))

    def test_copilot_flags(self):
        for flags, expected in [([], None), (['--awake'], ''), (['--awake-codex'], '--codex'), (['--profile', 'all'], None)]:
            with self.subTest(flags=flags):
                self.exercise('install.sh', flags, expected)

    def test_claude_flags(self):
        for flags, expected in [([], None), (['--awake'], ''), (['--awake-codex'], '--codex'), (['--profile', 'all'], None)]:
            with self.subTest(flags=flags):
                self.exercise('claude-install.sh', flags, expected)


if __name__ == '__main__':
    unittest.main()
