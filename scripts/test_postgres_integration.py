"""Run connection contracts against disposable Docker PostgreSQL with/without TLS.

Only fictional local credentials; containers, keys and data are removed on exit.
Requires Docker and openssl. Does not read any project database configuration.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]


def command(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, capture_output=True, **kwargs).stdout.strip()


def main():
    names = []
    with tempfile.TemporaryDirectory(prefix='skills-pg-tls-') as directory:
        certs = Path(directory)
        try:
            for stem in ('server', 'wrong'):
                command('openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                        '-keyout', str(certs / f'{stem}.key'), '-out', str(certs / f'{stem}.crt'),
                        '-days', '1', '-subj', '/CN=localhost',
                        '-addext', 'subjectAltName=DNS:localhost')
            urls = {}
            for tls in (False, True):
                name = 'skills-pg-fixture-' + uuid.uuid4().hex[:12]
                names.append(name)
                args = ['docker', 'run', '--rm', '-d', '--name', name,
                        '-p', '127.0.0.1::5432', '--tmpfs', '/var/lib/postgresql/data',
                        '-e', 'POSTGRES_PASSWORD=fixture-password',
                        '-e', 'POSTGRES_DB=skills_fixture']
                if tls:
                    args += ['-v', f'{certs}:/fixture-certs:ro', '--entrypoint', 'sh',
                             'postgres:17-alpine', '-c',
                             'cp /fixture-certs/server.* /tmp/; '
                             'chown postgres:postgres /tmp/server.*; chmod 600 /tmp/server.key; '
                             'exec docker-entrypoint.sh postgres -c ssl=on '
                             '-c ssl_cert_file=/tmp/server.crt -c ssl_key_file=/tmp/server.key']
                else:
                    args += ['postgres:17-alpine']
                command(*args)
                port = command('docker', 'port', name, '5432/tcp').rsplit(':', 1)[1]
                deadline = time.monotonic() + 60
                while True:
                    ready = subprocess.run(['docker', 'exec', name, 'pg_isready', '-h', '127.0.0.1',
                                            '-U', 'postgres', '-d', 'skills_fixture'], capture_output=True)
                    if ready.returncode == 0:
                        break
                    if time.monotonic() > deadline:
                        raise RuntimeError('Disposable PostgreSQL did not become ready.')
                    time.sleep(0.3)
                urls[tls] = f'postgresql://postgres:fixture-password@localhost:{port}/skills_fixture'
            env = os.environ | {
                'SKILLS_TEST_DATABASE_URL': urls[False]+'?sslmode=disable',
                'SKILLS_TEST_TLS_DATABASE_URL': urls[True],
                'SKILLS_TEST_CA': str(certs/'server.crt'),
                'SKILLS_TEST_WRONG_CA': str(certs/'wrong.crt'),
            }
            return subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                                  cwd=ROOT, env=env).returncode
        finally:
            for name in reversed(names):
                subprocess.run(['docker', 'rm', '-f', name], capture_output=True)


if __name__ == '__main__':
    raise SystemExit(main())
