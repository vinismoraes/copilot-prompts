"""Application-independent renewable leases and the macOS power backend."""
import os
import subprocess
import uuid

MODES = {'system': '-i', 'display': '-di', 'active': '-diu'}


def valid_id(value):
    if not isinstance(value, str) or str(uuid.UUID(value)) != value:
        raise ValueError('id must be a canonical UUID')
    return value


class Leases:
    def __init__(self):
        self.entries = {}

    def renew(self, lease_id, label, mode, ttl, now):
        valid_id(lease_id)
        if not isinstance(label, str) or not 1 <= len(label) <= 80 or not label.isprintable():
            raise ValueError('label must be 1–80 printable characters')
        if not isinstance(mode, str) or mode not in MODES:
            raise ValueError('mode must be system, display, or active')
        if type(ttl) is not int or not 1 <= ttl <= 300:
            raise ValueError('ttl must be an integer from 1 to 300 seconds')
        if lease_id not in self.entries and len(self.entries) >= 128:
            raise ValueError('too many leases')
        self.entries[lease_id] = {'id': lease_id, 'label': label, 'mode': mode, 'expires': now + ttl}

    def release(self, lease_id):
        self.entries.pop(valid_id(lease_id), None)

    def snapshot(self, now):
        self.entries = {key: item for key, item in self.entries.items() if item['expires'] > now}
        return [{**item, 'remaining_seconds': round(item['expires'] - now, 1)}
                for item in self.entries.values()]

    def mode(self, now):
        modes = [item['mode'] for item in self.snapshot(now)]
        return max(modes, key=list(MODES).index) if modes else None


class Power:
    def __init__(self, spawn=subprocess.Popen):
        self.spawn = spawn
        self.child = None
        self.mode = None
        self.renewed = float('-inf')

    def update(self, mode, now):
        if mode is None:
            self.stop()
        elif mode != self.mode or self.child is None or self.child.poll() is not None or now - self.renewed >= 20:
            old = self.child
            self.child = self.spawn(['/usr/bin/caffeinate', MODES[mode], '-t', '45', '-w', str(os.getpid())],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.mode, self.renewed = mode, now
            self._stop(old)

    @staticmethod
    def _stop(child):
        if child is not None and child.poll() is None:
            child.terminate()
            child.wait(timeout=2)

    def stop(self):
        self._stop(self.child)
        self.child, self.mode = None, None
