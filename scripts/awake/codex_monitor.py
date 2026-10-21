#!/usr/bin/env python3
"""Optional adapter: detect active VS Code Codex turns from local metadata."""
from contextlib import closing
import datetime as dt
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import time

EVENT = re.compile(rb'"type"\s*:\s*"event_msg"')
LIFECYCLE = re.compile(rb'"type"\s*:\s*"(task_started|task_complete|turn_aborted)"')


class Session:
    def __init__(self, path):
        self.path = Path(path)
        self.identity = None
        self.offset = 0
        self.turn = None
        self.started = 0

    def running(self, process_started):
        stat = self.path.stat()
        identity = (stat.st_dev, stat.st_ino)
        if identity != self.identity or stat.st_size < self.offset:
            self.identity, self.offset, self.turn, self.started = identity, 0, None, 0
        with self.path.open('rb') as stream:
            stream.seek(self.offset)
            while True:
                line = stream.readline()
                if not line or not line.endswith(b'\n'):
                    break  # Retry an incomplete write on the next poll.
                self.offset = stream.tell()
                if not EVENT.search(line) or not LIFECYCLE.search(line):
                    continue
                record = json.loads(line)
                if record.get('type') != 'event_msg':
                    continue
                event = record['payload']
                kind, turn = event.get('type'), event.get('turn_id')
                if kind == 'task_started':
                    self.started = dt.datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00')).timestamp()
                    self.turn = turn or 'unknown'
                elif kind in ('task_complete', 'turn_aborted') and (turn is None or turn == self.turn):
                    self.turn = None
        return self.turn is not None and self.started >= process_started


def live_owners(root):
    if not (root / 'thread-writer-locks').is_dir():
        return {}
    result = subprocess.run(['/usr/sbin/lsof', '-nP', '-Fpn', '+d', str(root / 'thread-writer-locks')],
                            capture_output=True, text=True, timeout=10)
    if result.returncode not in (0, 1) or (result.returncode == 1 and result.stderr.strip()):
        raise RuntimeError('cannot inspect Codex process locks')
    owners, pid = {}, None
    for line in result.stdout.splitlines():
        if line.startswith('p'):
            pid = int(line[1:])
        elif line.startswith('n') and line.endswith('.lock') and pid:
            owners[Path(line[1:]).stem] = pid
    if not owners:
        return {}
    result = subprocess.run(['/bin/ps', '-p', ','.join(map(str, set(owners.values()))),
                             '-o', 'pid=,lstart=,comm='], capture_output=True, text=True,
                            timeout=10, env={**os.environ, 'LC_ALL': 'C'})
    if result.returncode not in (0, 1):
        raise RuntimeError('cannot inspect Codex process start times')
    births = {}
    for line in result.stdout.splitlines():
        parts = line.split(None, 6)
        if len(parts) == 7 and '/extensions/openai.chatgpt-' in parts[6] and parts[6].endswith('/codex'):
            births[int(parts[0])] = time.mktime(time.strptime(' '.join(parts[1:6]), '%a %b %d %H:%M:%S %Y'))
    return {thread: births[pid] for thread, pid in owners.items() if pid in births}


def live_rows(rows, owners):
    return [(thread, path, owners[thread]) for thread, path, _ in rows if thread in owners]


class Monitor:
    def __init__(self, root):
        self.root = root
        self.sessions = {}

    def count(self):
        owners = live_owners(self.root)
        if not owners:
            self.sessions.clear()
            return 0
        database = self.root / 'state_5.sqlite'
        with closing(sqlite3.connect(database.as_uri() + '?mode=ro', uri=True, timeout=2)) as db:
            marks = ','.join('?' for _ in owners)
            rows = db.execute(f'SELECT id, rollout_path, source FROM threads WHERE id IN ({marks}) AND source = ?',
                              [*owners, 'vscode']).fetchall()
        active, live = 0, set()
        for thread, path, birth in live_rows(rows, owners):
            live.add(thread)
            session = self.sessions.get(thread)
            if session is None or session.path != Path(path):
                session = self.sessions[thread] = Session(path)
            active += session.running(birth)
        self.sessions = {key: value for key, value in self.sessions.items() if key in live}
        return active
