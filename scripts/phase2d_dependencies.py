"""Install exact cohort dependencies or fail; retain resolver and runtime evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--numpy', required=True, choices=['2.4.6', '2.3.5'])
    p.add_argument('--scipy', required=True, choices=['1.17.1', '1.16.3'])
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    status = {'status': 'INCONCLUSIVE', 'python': sys.version, 'steps': []}
    try:
        if sys.version_info[:2] != (3, 11):
            raise RuntimeError('Python 3.11 required')
        if (a.numpy, a.scipy) not in {('2.4.6', '1.17.1'), ('2.3.5', '1.17.1'), ('2.4.6', '1.16.3')}:
            raise ValueError('Unsupported cohort')
        pins = [line for line in Path('requirements-tested.txt').read_text(encoding='utf-8-sig').splitlines()
                if line and not line.startswith(('numpy==', 'scipy=='))]
        pins += [f'numpy=={a.numpy}', f'scipy=={a.scipy}', 'threadpoolctl==3.6.0',
                 'setuptools==80.9.0', 'wheel==0.45.1', 'PyYAML==6.0.3']
        lock = a.output/'requirements.txt'
        lock.write_text('\n'.join(pins)+'\n')
        commands = [
            ['install', '--only-binary=:all:', '--report', str(a.output/'resolver.json'), '-r', str(lock)],
            ['install', '--no-deps', '--no-build-isolation', '-e', '.'],
            ['check'],
        ]
        for i, command in enumerate(commands):
            with (a.output/f'pip-{i}.log').open('x') as log:
                result = subprocess.run([sys.executable, '-m', 'pip', *command], stdout=log, stderr=subprocess.STDOUT)
            status['steps'].append({'arguments': command, 'exit_code': result.returncode})
            if result.returncode:
                raise RuntimeError('Pinned dependency installation/check failed; no fallback permitted')
        from importlib.metadata import version
        for pin in pins:
            name, expected = pin.split('==')
            if version(name) != expected:
                raise RuntimeError('Installed version mismatch: '+name)
        probe = [
            sys.executable,
            '-c',
            'import sys; from stellarator_robust.upstream_attribution import environment, write; '
            'write(sys.argv[1], environment())',
            str(a.output/'environment.json'),
        ]
        with (a.output/'installed-package-import.log').open('x') as log:
            result = subprocess.run(
                probe, stdout=log, stderr=subprocess.STDOUT
            )
        status['steps'].append({
            'arguments': probe,
            'exit_code': result.returncode,
        })
        if result.returncode:
            raise RuntimeError(
                'Fresh-interpreter package import/environment capture failed'
            )
        status['status'] = 'PASS'
    except Exception as exc:
        status.update(status='FAIL', error=repr(exc))
        raise
    finally:
        (a.output/'status.json').write_text(json.dumps(status, indent=2)+'\n')
        files = {f.name: hashlib.sha256(f.read_bytes()).hexdigest()
                 for f in sorted(a.output.iterdir()) if f.is_file() and f.name != 'manifest.json'}
        (a.output/'manifest.json').write_text(json.dumps(files, indent=2)+'\n')


if __name__ == '__main__':
    main()
