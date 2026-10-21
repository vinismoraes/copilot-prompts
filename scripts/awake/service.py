"""Local JSON protocol over an owner-only Unix socket; no application imports."""
import fcntl
import json
import os
from pathlib import Path
import signal
import socket
import socketserver
import stat
import time

from core import Leases, Power


def home():
    return Path(os.environ.get('AWAKE_HOME', str(Path.home() / '.local/share/awake'))).resolve()


def request(message, root=None):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(3)
        connection.connect(str((root or home()) / 'awake.sock'))
        connection.sendall(json.dumps(message).encode() + b'\n')
        with connection.makefile('rb') as stream:
            data = stream.readline(262144)
        if not data.endswith(b'\n'):
            raise RuntimeError('incomplete service response')
        result = json.loads(data)
        if not result.get('ok'):
            raise ValueError(result.get('error', 'request failed'))
        return result


def dispatch(leases, message, now):
    if not isinstance(message, dict):
        raise ValueError('request must be an object')
    op = message.get('op')
    if op == 'renew':
        leases.snapshot(now)
        leases.renew(message.get('id'), message.get('label'), message.get('mode'), message.get('ttl'), now)
    elif op == 'release':
        leases.release(message.get('id'))
    elif op != 'status':
        raise ValueError('unknown operation')
    return {'ok': True, 'mode': leases.mode(now), 'leases': leases.snapshot(now)}


def serve(root=None, power=None):
    root = root or home()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    if root.stat().st_uid != os.getuid():
        raise RuntimeError('service directory must be owned by you')
    root.chmod(0o700)
    lock = (root / 'service.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    path = root / 'awake.sock'
    if path.exists():
        info = path.lstat()
        if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid():
            raise RuntimeError('refusing to replace unexpected socket path')
        path.unlink()
    leases, power = Leases(), power or Power()
    stopping = False
    def stop(signum, frame):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    class Handler(socketserver.StreamRequestHandler):
        timeout = 0.5
        def handle(self):
            try:
                raw = self.rfile.readline(4097)
                if len(raw) > 4096 or not raw.endswith(b'\n'):
                    raise ValueError('request must be one JSON line, at most 4096 bytes')
                response = dispatch(leases, json.loads(raw), time.monotonic())
                power.update(response['mode'], time.monotonic())
                response['power_active'] = power.child is not None and power.child.poll() is None
            except (ValueError, TypeError, OSError) as error:
                response = {'ok': False, 'error': str(error)}
            try:
                self.wfile.write(json.dumps(response).encode() + b'\n')
            except OSError:
                pass

    try:
        with socketserver.UnixStreamServer(str(path), Handler) as server:
            path.chmod(0o600)
            server.timeout = 1
            while not stopping:
                server.handle_request()
                power.update(leases.mode(time.monotonic()), time.monotonic())
    finally:
        power.stop()
        path.unlink(missing_ok=True)
        lock.close()
