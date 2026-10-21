#!/usr/bin/env python3
"""Install or remove Awake for the current macOS user."""
import argparse
import json
import os
from pathlib import Path
import plistlib
import shlex
import shutil
import subprocess
import sys
import time

LABEL = 'com.local.awake'
CORE = ['awake.py', 'core.py', 'service.py', 'install.py', 'README.md', 'test_core.py', 'test_integration.py']
OPTIONAL = ['codex_monitor.py', 'test_codex.py']


def plist_data(root, adapter=False, mode='system'):
    label = LABEL + ('.codex' if adapter else '')
    args = ['adapter', 'codex', 'run', '--mode', mode] if adapter else ['serve']
    return {
        'Label': label,
        'ProgramArguments': [sys.executable, str(root / 'awake.py'), *args],
        'RunAtLoad': True,
        'KeepAlive': True,
        'ThrottleInterval': 10,
        'ProcessType': 'Background',
        'StandardOutPath': str(root / ('codex.log' if adapter else 'service.log')),
        'StandardErrorPath': str(root / ('codex.err.log' if adapter else 'service.err.log')),
        'EnvironmentVariables': {'PYTHONUNBUFFERED': '1', 'AWAKE_HOME': str(root)},
    }


def ensure_existing(root, binary, agents, source, codex, mode, run=subprocess.run):
    """Reuse a recognized installation and optionally add the Codex adapter."""
    marker = root / 'installation.json'
    if not marker.is_file():
        raise ValueError('unrecognized installation; refusing to overwrite it')
    metadata = json.loads(marker.read_text())
    if metadata.get('application') != 'awake' or metadata.get('version') != '0.1.0':
        raise ValueError('unrecognized installation version; explicit reinstall required')
    if not binary.is_file() or '# awake-managed-launcher' not in binary.read_text():
        raise ValueError('missing or unmanaged awake launcher')
    for name in ['awake.py', 'core.py', 'service.py']:
        if not (root / name).is_file():
            raise ValueError('incomplete Awake installation; reinstall required')
    core_plist = agents / (LABEL + '.plist')
    adapter_plist = agents / (LABEL + '.codex.plist')
    if not core_plist.is_file():
        raise ValueError('missing core launch agent; reinstall required')
    for path in [core_plist, adapter_plist]:
        if path.exists():
            data = plistlib.loads(path.read_bytes())
            arguments = data.get('ProgramArguments', [])
            if len(arguments) < 2 or arguments[1] != str(root / 'awake.py'):
                raise ValueError('unexpected launch agent; refusing to replace it')
    domain = f'gui/{os.getuid()}'
    if codex:
        for name in OPTIONAL:
            target = root / name
            if not target.exists():
                shutil.copy2(source / name, target)
        if adapter_plist.exists():
            data = plistlib.loads(adapter_plist.read_bytes())
            previous = data['ProgramArguments']
            if mode is not None:
                arguments = [sys.executable, str(root / 'awake.py'), 'adapter', 'codex', 'run', '--mode', mode]
                if arguments != previous:
                    data['ProgramArguments'] = arguments
                    temp = adapter_plist.with_suffix('.tmp')
                    temp.write_bytes(plistlib.dumps(data))
                    temp.chmod(0o600)
                    temp.replace(adapter_plist)
                    run(['/bin/launchctl', 'bootout', f'{domain}/{LABEL}.codex'], capture_output=True)
        else:
            with adapter_plist.open('xb') as stream:
                plistlib.dump(plist_data(root, True, mode or 'system'), stream)
            adapter_plist.chmod(0o600)
        metadata['codex'] = True
        marker.write_text(json.dumps(metadata) + '\n')
    run([sys.executable, str(root / 'awake.py'), 'start'], check=True)
    if codex:
        run([sys.executable, str(root / 'awake.py'), 'adapter', 'codex', 'start'], check=True)
    print('Reused existing Awake installation; installed code was preserved.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex', action='store_true', help='Install the optional VS Code Codex adapter')
    parser.add_argument('--codex-mode', choices=['system', 'display', 'active'])
    parser.add_argument('--ensure', action='store_true', help='Reuse an existing installation, preserving its adapter mode unless explicitly changed')
    parser.add_argument('--uninstall', action='store_true')
    args = parser.parse_args()
    if sys.platform != 'darwin':
        raise SystemExit('This release supports macOS only.')
    source = Path(__file__).resolve().parent
    root = Path.home() / '.local/share/awake'
    binary = Path.home() / '.local/bin/awake'
    agents = Path.home() / 'Library/LaunchAgents'
    domain = f'gui/{os.getuid()}'
    labels = [LABEL, LABEL + '.codex']
    marker = root / 'installation.json'

    if args.uninstall:
        if not marker.exists() or json.loads(marker.read_text()).get('application') != 'awake':
            raise SystemExit('No recognized Awake installation found.')
        for label in reversed(labels):
            plist = agents / (label + '.plist')
            if not plist.exists():
                continue
            data = plistlib.loads(plist.read_bytes())
            if data.get('ProgramArguments', [None, None])[1] != str(root / 'awake.py'):
                raise SystemExit('Unexpected launch agent; refusing to remove it.')
            subprocess.run(['/bin/launchctl', 'disable', f'{domain}/{label}'], check=True)
            subprocess.run(['/bin/launchctl', 'bootout', f'{domain}/{label}'], capture_output=True)
            plist.unlink()
        if binary.exists() and '# awake-managed-launcher' in binary.read_text():
            binary.unlink()
        for name in [*CORE, *OPTIONAL, 'installation.json', 'service.lock', 'awake.sock',
                     'service.log', 'service.err.log', 'codex.log', 'codex.err.log']:
            (root / name).unlink(missing_ok=True)
        cache = root / '__pycache__'
        if cache.is_dir():
            for file in cache.glob('*.pyc'):
                file.unlink()
            try:
                cache.rmdir()
            except OSError:
                pass
        try:
            root.rmdir()
        except OSError:
            print('Preserved additional files in', root)
        print('Awake uninstalled; normal macOS power settings apply.')
        return

    if args.ensure and root.exists():
        ensure_existing(root, binary, agents, source, args.codex, args.codex_mode)
        return
    if root.exists() or binary.exists() or any((agents / (label + '.plist')).exists() for label in labels):
        raise SystemExit('Existing files found; refusing to overwrite. Uninstall the existing Awake package first.')
    selected = labels if args.codex else labels[:1]
    files = CORE + (OPTIONAL if args.codex else [])
    for name in files:
        if not (source / name).is_file():
            raise SystemExit('Package is missing ' + name)
    root.mkdir(parents=True, mode=0o700)
    binary.parent.mkdir(parents=True, exist_ok=True)
    agents.mkdir(parents=True, exist_ok=True)
    created_plists = []
    try:
        for name in files:
            shutil.copy2(source / name, root / name)
        launcher = ('#!/bin/sh\n# awake-managed-launcher\nexec ' + shlex.quote(sys.executable)
                    + ' ' + shlex.quote(str(root / 'awake.py')) + ' "$@"\n')
        with binary.open('x') as stream:
            stream.write(launcher)
        binary.chmod(0o700)
        for label in selected:
            plist = agents / (label + '.plist')
            with plist.open('xb') as stream:
                plistlib.dump(plist_data(root, label.endswith('.codex'), args.codex_mode or 'system'), stream)
            plist.chmod(0o600)
            created_plists.append(plist)
            subprocess.run(['/bin/launchctl', 'enable', f'{domain}/{label}'], check=True)
            subprocess.run(['/bin/launchctl', 'bootstrap', domain, str(plist)], check=True)
        from service import request
        for attempt in range(50):
            try:
                request({'op': 'status'}, root)
                break
            except OSError:
                if attempt == 49:
                    raise
                time.sleep(0.1)
        marker.write_text(json.dumps({'application': 'awake', 'version': '0.1.0', 'codex': args.codex}) + '\n')
    except BaseException:
        for plist in reversed(created_plists):
            subprocess.run(['/bin/launchctl', 'bootout', f'{domain}/{plist.stem}'], capture_output=True)
            plist.unlink(missing_ok=True)
        binary.unlink(missing_ok=True)
        # This directory was created by this invocation and never existed beforehand.
        shutil.rmtree(root)
        raise
    print('Installed and started:', root)
    print('Command:', binary)
    if str(binary.parent) not in os.environ.get('PATH', '').split(os.pathsep):
        print('Add ~/.local/bin to PATH to use the short command: export PATH="$HOME/.local/bin:$PATH"')


if __name__ == '__main__':
    main()
