#!/usr/bin/env python3
"""Generate a flat APT repository from the published DEBs."""
import bz2
from datetime import datetime, timezone
from email.utils import format_datetime
import gzip
import hashlib
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
records=[]
debs=sorted((ROOT/'debs').glob('*.deb'))
if not debs: raise SystemExit('No DEBs found.')
for path in debs:
    fields=subprocess.check_output(['dpkg-deb','-f',str(path)],text=True).rstrip()
    data=path.read_bytes()
    records.append(fields+'\n'+f'Filename: debs/{path.name}\nSize: {len(data)}\n'+
        ''.join(f'{name}: {hashlib.new(algorithm,data).hexdigest()}\n'
                for name,algorithm in [('MD5sum','md5'),('SHA1','sha1'),('SHA256','sha256')]))
packages=('\n'.join(records)+'\n').encode()
(ROOT/'Packages').write_bytes(packages)
(ROOT/'Packages.gz').write_bytes(gzip.compress(packages,mtime=0))
(ROOT/'Packages.bz2').write_bytes(bz2.compress(packages))
release='\n'.join([
    'Origin: Ginppai Repo', 'Label: Ginppai Repo', 'Suite: stable', 'Version: 1.0',
    'Codename: ginppai', 'Architectures: iphoneos-arm iphoneos-arm64', 'Components: main',
    'Description: nogadamachine Ginppai jailbreak tweak repository',
    'Date: '+format_datetime(datetime.now(timezone.utc),usegmt=True),
])+'\n'
for heading,algorithm in [('MD5Sum','md5'),('SHA256','sha256')]:
    release+=heading+':\n'
    for name in ['Packages','Packages.gz','Packages.bz2']:
        data=(ROOT/name).read_bytes()
        release+=f' {hashlib.new(algorithm,data).hexdigest()} {len(data)} {name}\n'
(ROOT/'Release').write_text(release)
(ROOT/'SHA256SUMS').write_text(''.join(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  debs/{path.name}\n' for path in debs))
print(f'Generated flat APT repository: {len(debs)} packages.')
