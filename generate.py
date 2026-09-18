#!/usr/bin/env python3
"""Generate current-package flat APT indexes, preserving archived DEBs."""
import bz2
from datetime import datetime, timezone
from email.utils import format_datetime
import gzip
import hashlib
import lzma
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
BASE = 'https://nogadamachine.github.io/Ginppai-Repo/'
INDEXES = ['Packages', 'Packages.gz', 'Packages.bz2', 'Packages.xz']
SCHEMES = {'': ['iphoneos-arm', 'iphoneos-arm64'],
           'rootful': ['iphoneos-arm'], 'rootless': ['iphoneos-arm64']}


def generate():
    latest = {}
    debs = sorted((ROOT/'debs').glob('*.deb'))
    if not debs:
        raise SystemExit('No DEBs found.')
    for path in debs:
        control = subprocess.check_output(['dpkg-deb', '-f', str(path)], text=True).rstrip()
        fields = dict(line.split(': ', 1) for line in control.splitlines()
                      if line and not line[0].isspace() and ': ' in line)
        key = fields['Package'], fields['Architecture']
        if fields['Architecture'] not in SCHEMES['']:
            raise SystemExit(f'Unsupported architecture: {path.name}')
        if key in latest:
            result = subprocess.run(['dpkg', '--compare-versions', fields['Version'], 'gt',
                                     latest[key][0]['Version']])
            if result.returncode not in (0, 1):
                raise SystemExit(f'Invalid package version: {path.name}')
            if result.returncode == 1:
                continue
        latest[key] = fields, control, path
    stamp = format_datetime(datetime.now(timezone.utc), usegmt=True)
    for scheme, arches in SCHEMES.items():
        directory = ROOT/scheme
        directory.mkdir(exist_ok=True)
        records = []
        for key, (fields, control, path) in sorted(latest.items()):
            if fields['Architecture'] not in arches:
                continue
            data = path.read_bytes()
            filename = ('debs/' if not scheme else BASE+'debs/')+path.name
            records.append(control+'\n'+f'Filename: {filename}\nSize: {len(data)}\n'+
                ''.join(f'{name}: {hashlib.new(algorithm, data).hexdigest()}\n'
                        for name, algorithm in [('MD5sum', 'md5'), ('SHA1', 'sha1'), ('SHA256', 'sha256')]))
        packages = ('\n'.join(records)+'\n').encode()
        (directory/'Packages').write_bytes(packages)
        (directory/'Packages.gz').write_bytes(gzip.compress(packages, mtime=0))
        (directory/'Packages.bz2').write_bytes(bz2.compress(packages))
        (directory/'Packages.xz').write_bytes(lzma.compress(packages, check=lzma.CHECK_CRC32))
        label = 'Ginppai Repo'+(' ('+scheme+')' if scheme else '')
        release = '\n'.join([
            'Origin: Ginppai Repo', 'Label: '+label, 'Suite: stable', 'Version: 1.0',
            'Codename: ginppai', 'Architectures: '+' '.join(arches), 'Components: main',
            'Description: nogadamachine Ginppai jailbreak tweak repository', 'Date: '+stamp,
        ])+'\n'
        for heading, algorithm in [('MD5Sum', 'md5'), ('SHA256', 'sha256'), ('SHA512', 'sha512')]:
            release += heading+':\n'
            for name in INDEXES:
                data = (directory/name).read_bytes()
                release += f' {hashlib.new(algorithm, data).hexdigest()} {len(data)} {name}\n'
        (directory/'Release').write_text(release)
        url = BASE+(scheme+'/' if scheme else '')
        (directory/'ginppai.list').write_text(f'deb {url} ./\n')
        print(f'{scheme or "main"}: {len(records)} current packages, architectures {", ".join(arches)}')
    (ROOT/'SHA256SUMS').write_text(''.join(
        f'{hashlib.sha256(path.read_bytes()).hexdigest()}  debs/{path.name}\n' for path in debs))
    print(f'Preserved {len(debs)} DEBs for direct downloads and rollback.')


if __name__ == '__main__':
    generate()
