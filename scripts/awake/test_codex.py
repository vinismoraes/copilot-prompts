import datetime
import json
import tempfile
import unittest
from pathlib import Path

import codex_monitor as awake


def event(kind, turn='a', timestamp='2026-10-20T15:00:00Z'):
    return (json.dumps({'timestamp': timestamp, 'type': 'event_msg',
                        'payload': {'type': kind, 'turn_id': turn}}) + '\n').encode()


class WatcherTests(unittest.TestCase):
    def test_lifecycle_and_partial_writes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'session.jsonl'
            path.write_bytes(event('task_started'))
            reader = awake.Session(path)
            self.assertTrue(reader.running(0))
            complete = event('task_complete')
            with path.open('ab') as f:
                f.write(complete[:20])
            self.assertTrue(reader.running(0))
            with path.open('ab') as f:
                f.write(complete[20:])
            self.assertFalse(reader.running(0))
            for ending in ['turn_aborted', 'task_complete']:
                with self.subTest(ending=ending):
                    path.write_bytes(event('task_started', 'b') + event(ending, 'b'))
                    self.assertFalse(awake.Session(path).running(0))

    def test_previous_process_and_stale_completion(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'session.jsonl'
            path.write_bytes(event('task_started', 'b') + event('task_complete', 'a'))
            reader = awake.Session(path)
            self.assertTrue(reader.running(0))
            later = datetime.datetime(2026, 10, 20, 16, tzinfo=datetime.timezone.utc).timestamp()
            self.assertFalse(reader.running(later))

    def test_large_tail_and_rotation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'session.jsonl'
            noise = (json.dumps({'type': 'response_item', 'payload': 'x' * 5000}) + '\n').encode()
            path.write_bytes(event('task_started') + noise * 100)
            reader = awake.Session(path)
            self.assertTrue(reader.running(0))
            replacement = path.with_suffix('.new')
            replacement.write_bytes(event('task_started') + event('task_complete'))
            replacement.replace(path)
            self.assertFalse(reader.running(0))

    def test_process_exit_removes_active_thread(self):
        rows = [('one', '/one', 0), ('two', '/two', 0)]
        self.assertEqual(awake.live_rows(rows, {'one': 123}), [('one', '/one', 123)])


if __name__ == '__main__':
    unittest.main()
