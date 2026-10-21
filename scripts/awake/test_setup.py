import json
from pathlib import Path
import plistlib
import tempfile
import unittest

import install


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / 'awake'
        self.root.mkdir()
        self.agents = self.base / 'agents'
        self.agents.mkdir()
        self.binary = self.base / 'bin-awake'
        self.binary.write_text('# awake-managed-launcher\n' + str(self.root / 'awake.py'))
        for name in ['awake.py', 'core.py', 'service.py']:
            (self.root / name).write_text('# installed\n')
        (self.root / 'installation.json').write_text(json.dumps({'application': 'awake', 'version': '0.1.0', 'codex': False}))
        self.write_agent(False)
        self.calls = []

    def tearDown(self):
        self.temp.cleanup()

    def write_agent(self, adapter, mode='system'):
        path = self.agents / ('com.local.awake' + ('.codex' if adapter else '') + '.plist')
        path.write_bytes(plistlib.dumps(install.plist_data(self.root, adapter, mode)))
        return path

    def run_setup(self, codex=False, mode=None):
        install.ensure_existing(self.root, self.binary, self.agents, Path(__file__).parent,
                                codex, mode, run=lambda args, **kw: self.calls.append(args))

    def test_reuses_install_without_overwriting_code(self):
        self.run_setup()
        self.run_setup()
        self.assertEqual((self.root / 'awake.py').read_text(), '# installed\n')
        self.assertFalse((self.root / 'codex_monitor.py').exists())

    def test_adds_adapter_and_preserves_existing_mode_on_repeat(self):
        self.run_setup(True, 'active')
        self.assertTrue((self.root / 'codex_monitor.py').is_file())
        path = self.agents / 'com.local.awake.codex.plist'
        before = path.read_bytes()
        self.calls.clear()
        self.run_setup(True)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(any('bootout' in call for call in self.calls))

    def test_rejects_unmanaged_files_before_starting_services(self):
        (self.root / 'installation.json').write_text('{"application":"other"}')
        with self.assertRaises(ValueError):
            self.run_setup()
        self.assertEqual(self.calls, [])

    def test_rejects_foreign_adapter_before_mutation(self):
        path = self.write_agent(True)
        data = plistlib.loads(path.read_bytes())
        data['ProgramArguments'][1] = '/other/application.py'
        path.write_bytes(plistlib.dumps(data))
        with self.assertRaises(ValueError):
            self.run_setup(True)
        self.assertEqual(self.calls, [])


if __name__ == '__main__':
    unittest.main()
