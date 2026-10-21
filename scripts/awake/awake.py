#!/usr/bin/env python3
"""Keep macOS awake while local tasks hold renewable leases."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

from core import MODES
from service import home, request, serve

LABEL = 'com.local.awake'


def control(action, adapter=False):
    label = LABEL + ('.codex' if adapter else '')
    target = f'gui/{os.getuid()}/{label}'
    plist = Path.home() / 'Library/LaunchAgents' / (label + '.plist')
    if not plist.exists():
        raise ValueError('service is not installed; run install.py' + (' --codex' if adapter else ''))
    if action == 'stop':
        subprocess.run(['/bin/launchctl', 'disable', target], check=True)
        subprocess.run(['/bin/launchctl', 'bootout', target], capture_output=True)
    else:
        subprocess.run(['/bin/launchctl', 'enable', target], check=True)
        found = subprocess.run(['/bin/launchctl', 'print', target], capture_output=True)
        if found.returncode:
            subprocess.run(['/bin/launchctl', 'bootstrap', f'gui/{os.getuid()}', str(plist)], check=True)
    print(('Codex adapter' if adapter else 'Awake service') + ' ' + ('enabled' if action == 'start' else 'disabled'))


def release(lease_id):
    try:
        request({'op': 'release', 'id': lease_id})
    except (OSError, ValueError, RuntimeError):
        pass  # The finite lease expires if the service cannot be reached.


def run_command(command, mode):
    if command and command[0] == '--':
        command = command[1:]
    if not command:
        raise ValueError('provide a command after --')
    lease_id = str(uuid.uuid4())
    message = {'op': 'renew', 'id': lease_id, 'label': 'command: ' + Path(command[0]).name[:60], 'mode': mode, 'ttl': 30}
    request(message)
    child = None
    pending_signal = None
    handlers = {}
    def forward(signum, frame):
        nonlocal pending_signal
        pending_signal = signum
        if child is not None and child.poll() is None:
            try:
                os.killpg(child.pid, signum)
            except ProcessLookupError:
                pass
    try:
        for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            handlers[signum] = signal.signal(signum, forward)
        child = subprocess.Popen(command, start_new_session=True)
        if pending_signal is not None:
            forward(pending_signal, None)
        next_renewal, warned = time.monotonic() + 10, False
        while child.poll() is None:
            if time.monotonic() >= next_renewal:
                try:
                    request(message)
                    warned = False
                    next_renewal = time.monotonic() + 10
                except (OSError, ValueError, RuntimeError):
                    if not warned:
                        print('awake: service unavailable; command continues, but keep-awake may expire', file=sys.stderr)
                    warned = True
                    next_renewal = time.monotonic() + 2
            time.sleep(0.2)
        return child.returncode if child.returncode >= 0 else 128 - child.returncode
    finally:
        release(lease_id)
        for signum, handler in handlers.items():
            signal.signal(signum, handler)


def codex_adapter(mode):
    # The core service and command wrapper never import or inspect Codex.
    from codex_monitor import Monitor
    monitor = Monitor(Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))).resolve())
    lease_id, stopping = str(uuid.uuid4()), False
    def stop(signum, frame):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    last_active, previous = float('-inf'), None
    try:
        while not stopping:
            try:
                count = monitor.count()
                if count:
                    last_active = time.monotonic()
                if time.monotonic() - last_active < 15:
                    request({'op': 'renew', 'id': lease_id, 'label': f'Codex: {count} active tasks', 'mode': mode, 'ttl': 30})
                else:
                    release(lease_id)
                state = {'active_tasks': count, 'error': None}
            except Exception as error:
                # A broken adapter must not renew a lease forever. Never log session contents.
                state = {'active_tasks': None, 'error': type(error).__name__}
            if state != previous:
                print(json.dumps(state), flush=True)
                previous = state
            for _ in range(25):
                if stopping:
                    break
                time.sleep(0.2)
    finally:
        release(lease_id)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    subs.add_parser('serve', help='Run the local lease service')
    subs.add_parser('status', help='Show active leases and actual power state')
    subs.add_parser('start', help='Enable the core login service')
    subs.add_parser('stop', help='Disable the core login service and release assertions')
    run = subs.add_parser('run', help='Wrap a foreground build/test command')
    run.add_argument('--mode', choices=MODES, default='system')
    run.add_argument('args', nargs=argparse.REMAINDER)
    adapter = subs.add_parser('adapter', help='Optional application adapters')
    adapter.add_argument('name', choices=['codex'])
    adapter.add_argument('action', choices=['start', 'stop', 'run'])
    adapter.add_argument('--mode', choices=MODES, default='system')
    lease = subs.add_parser('lease', help='Integration API for other local tools')
    lease.add_argument('action', choices=['acquire', 'renew', 'release'])
    lease.add_argument('id', nargs='?')
    lease.add_argument('--label', default='external task')
    lease.add_argument('--mode', choices=MODES, default='system')
    lease.add_argument('--ttl', type=int, default=30)
    args = parser.parse_args()
    try:
        if sys.platform != 'darwin':
            raise ValueError('this version supports macOS only')
        if args.command == 'serve':
            serve()
        elif args.command == 'status':
            print(json.dumps(request({'op': 'status'}), indent=2))
        elif args.command in ('start', 'stop'):
            control(args.command)
        elif args.command == 'run':
            return run_command(args.args, args.mode)
        elif args.command == 'adapter':
            if args.action == 'run':
                codex_adapter(args.mode)
            else:
                control(args.action, adapter=True)
        else:
            lease_id = args.id or (str(uuid.uuid4()) if args.action == 'acquire' else None)
            if not lease_id:
                raise ValueError('provide the lease ID')
            if args.action == 'release':
                request({'op': 'release', 'id': lease_id})
            else:
                request({'op': 'renew', 'id': lease_id, 'label': args.label, 'mode': args.mode, 'ttl': args.ttl})
                print(lease_id)
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f'awake: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
