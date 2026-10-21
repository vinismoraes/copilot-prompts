import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

from service import request


@unittest.skipUnless(sys.platform == 'darwin', 'macOS power backend')
class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='awake-test-', dir='/private/tmp')
        self.root = Path(self.temp.name)
        # Deliberately omit every Codex module: the core must work without them.
        for name in ['awake.py', 'core.py', 'service.py']:
            shutil.copy2(Path(__file__).parent / name, self.root / name)
        self.env = {**os.environ, 'AWAKE_HOME': str(self.root), 'CODEX_HOME': str(self.root / 'absent')}
        self.cli = [sys.executable, str(self.root / 'awake.py')]
        self.server = subprocess.Popen([*self.cli, 'serve'], env=self.env,
                                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        for _ in range(50):
            if (self.root / 'awake.sock').exists():
                break
            if self.server.poll() is not None:
                self.fail(self.server.stderr.read().decode())
            time.sleep(0.05)
        self.assertTrue((self.root / 'awake.sock').exists())
        self.children = []

    def tearDown(self):
        for child in self.children:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=5)
        self.server.terminate()
        self.server.wait(timeout=5)
        self.server.stderr.close()
        self.temp.cleanup()

    def send(self, **message):
        return request(message, self.root)

    def test_overlapping_leases_expire_and_reject_invalid_requests(self):
        one, two = str(uuid.uuid4()), str(uuid.uuid4())
        self.send(op='renew', id=one, label='one', mode='system', ttl=30)
        self.send(op='renew', id=two, label='two', mode='active', ttl=1)
        self.assertEqual(self.send(op='status')['mode'], 'active')
        with self.assertRaises(ValueError):
            self.send(op='renew', id=one, label='one', mode='active', ttl=-1)
        time.sleep(1.2)
        self.assertEqual(self.send(op='status')['mode'], 'system')
        self.send(op='release', id=one)
        self.assertFalse(self.send(op='status')['power_active'])

    def test_command_exit_status_cleanup_and_launch_failure(self):
        result = subprocess.run([*self.cli, 'run', '--', sys.executable, '-c', 'raise SystemExit(7)'], env=self.env)
        self.assertEqual(result.returncode, 7)
        self.assertEqual(self.send(op='status')['leases'], [])
        result = subprocess.run([*self.cli, 'run', '--', '/nonexistent/awake-test-command'],
                                env=self.env, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.send(op='status')['leases'], [])

    def test_termination_forwards_to_command_and_releases_lease(self):
        marker = self.root / 'terminated'
        code = ('import signal,time,pathlib; '
                f'signal.signal(signal.SIGTERM, lambda *a: (pathlib.Path({str(marker)!r}).touch(), exit(0))); '
                'time.sleep(20)')
        child = subprocess.Popen([*self.cli, 'run', '--', sys.executable, '-c', code], env=self.env)
        self.children.append(child)
        time.sleep(0.5)
        self.assertEqual(len(self.send(op='status')['leases']), 1)
        child.terminate()
        self.assertEqual(child.wait(timeout=5), 0)
        self.assertTrue(marker.exists())
        self.assertEqual(self.send(op='status')['leases'], [])

    def test_wrapper_renews_after_service_restart(self):
        child = subprocess.Popen([*self.cli, 'run', '--', sys.executable, '-c', 'import time; time.sleep(20)'], env=self.env)
        self.children.append(child)
        time.sleep(0.5)
        self.assertEqual(len(self.send(op='status')['leases']), 1)
        self.server.terminate()
        self.server.wait(timeout=5)
        self.server.stderr.close()
        self.server = subprocess.Popen([*self.cli, 'serve'], env=self.env,
                                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        time.sleep(0.3)
        self.assertEqual(self.send(op='status')['leases'], [])
        for _ in range(55):
            if self.send(op='status')['leases']:
                break
            time.sleep(0.2)
        self.assertEqual(len(self.send(op='status')['leases']), 1)


if __name__ == '__main__':
    unittest.main()
