#!/usr/bin/env python3
"""Validate local indexes, or their exact published HTTPS copies."""
import argparse
import bz2
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import lzma
from pathlib import Path
import subprocess
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
BASE = 'https://nogadamachine.github.io/Ginppai-Repo/'
SCHEMES = {'': {'iphoneos-arm', 'iphoneos-arm64'},
           'rootful/': {'iphoneos-arm'}, 'rootless/': {'iphoneos-arm64'}}
INDEXES = ['Packages', 'Packages.gz', 'Packages.bz2', 'Packages.xz']


def parse(text):
    records = []
    for stanza in text.strip().split('\n\n'):
        fields = {}
        for line in stanza.splitlines():
            if line.startswith((' ', '\t')):
                fields[key] += '\n'+line
            else:
                key, value = line.split(':', 1)
                assert key not in fields, f'Duplicate field {key}'
                fields[key] = value.strip()
        records.append(fields)
    return records


def verify(published=False):
    checked = set()
    debs = {}
    for path in (ROOT/'debs').glob('*.deb'):
        fields = parse(subprocess.check_output(['dpkg-deb', '-f', str(path)], text=True))[0]
        debs[path.name] = fields
    for directory, arches in SCHEMES.items():
        release = parse((ROOT/directory/'Release').read_text())[0]
        assert set(release['Architectures'].split()) == arches
        assert release['Components'] == 'main'
        for field, algorithm in [('MD5Sum', 'md5'), ('SHA256', 'sha256'), ('SHA512', 'sha512')]:
            rows = [line.split() for line in release[field].splitlines() if line.strip()]
            assert {row[2] for row in rows} == set(INDEXES)
            for digest, length, name in rows:
                data = (ROOT/directory/name).read_bytes()
                assert len(data) == int(length) and hashlib.new(algorithm, data).hexdigest() == digest
                checked.add(directory+name)
        raw = (ROOT/directory/'Packages').read_bytes()
        for extension, decompress in [('gz', gzip.decompress), ('bz2', bz2.decompress), ('xz', lzma.decompress)]:
            assert decompress((ROOT/directory/('Packages.'+extension)).read_bytes()) == raw
        records = parse(raw.decode())
        keys = [(p['Package'], p['Architecture']) for p in records]
        assert len(keys) == len(set(keys)), 'Repeated package architecture'
        expected = {(p['Package'], p['Architecture']) for p in debs.values() if p['Architecture'] in arches}
        assert set(keys) == expected, 'Missing or incompatible architecture'
        for package in records:
            url = urljoin(BASE+directory, package['Filename'])
            assert url.startswith(BASE+'debs/')
            relative = url[len(BASE):]
            assert '..' not in Path(relative).parts
            data = (ROOT/relative).read_bytes()
            metadata = debs[Path(relative).name]
            for key, value in metadata.items():
                assert package[key] == value, f'Control mismatch: {relative}: {key}'
            assert len(data) == int(package['Size'])
            for field, algorithm in [('MD5sum', 'md5'), ('SHA1', 'sha1'), ('SHA256', 'sha256')]:
                assert hashlib.new(algorithm, data).hexdigest() == package[field]
            for old in debs.values():
                if (old['Package'], old['Architecture']) == (package['Package'], package['Architecture']):
                    subprocess.run(['dpkg', '--compare-versions', package['Version'], 'ge', old['Version']], check=True)
            checked.add(relative)
        assert (ROOT/directory/'ginppai.list').read_text() == f'deb {BASE+directory} ./\n'
        checked.update(directory+name for name in ['Release', 'ginppai.list', 'index.html'])
        print(f'{directory or "main"}: {len(records)} packages, versions, architectures, compression and hashes OK')
    for line in (ROOT/'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest
    checked.update(['SHA256SUMS', 'assets/site.css', 'assets/site.js', 'depictions/customizer.html', 'depictions/ipad.html'])
    if published:
        def compare(relative):
            request = Request(BASE+relative, headers={'User-Agent': 'Ginppai-Repo-verifier', 'Cache-Control': 'no-cache'})
            with urlopen(request, timeout=30) as response:
                assert response.status == 200
                assert urlparse(response.url).scheme == 'https'
                assert response.read() == (ROOT/relative).read_bytes(), f'Published bytes differ: {relative}'
            return relative
        with ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(compare, sorted(checked)))
        print(f'Published HTTPS copies match all {len(checked)} checked files.')
    print(f'All {len(debs)} archived DEB hashes are valid.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--published', action='store_true')
    verify(parser.parse_args().published)
