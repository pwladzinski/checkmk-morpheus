# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2026 Pawel Wladzinski <pawel.wladzinski@vayana.pl>
"""Validate the exact release MKP against its source and version contract."""
import argparse
import ast
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.2.0'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mkp', type=Path, default=ROOT / 'dist' / f'morpheus-{VERSION}.mkp')
    args = parser.parse_args()
    content = args.mkp.read_bytes()
    with tarfile.open(fileobj=io.BytesIO(content), mode='r:gz') as archive:
        assert sorted(archive.getnames()) == ['cmk_addons_plugins.tar', 'info', 'info.json']
        manifest = json.load(archive.extractfile('info.json'))
        assert ast.literal_eval(archive.extractfile('info').read().decode()) == manifest
        assert manifest['name'] == 'morpheus' and manifest['version'] == VERSION
        assert manifest['title'] == 'HPE Morpheus Monitoring'
        assert manifest['author'] == 'Pawel Wladzinski <pawel.wladzinski@vayana.pl>'
        assert manifest['version.min_required'] == '2.4.0'
        assert manifest['version.usable_until'] == '2.5.0p99'
        assert manifest['download_url'] == 'https://github.com/pwladzinski/checkmk-morpheus'
        listed = manifest['files']['cmk_addons_plugins']
        assert len(listed) == len(set(listed)) == 10
        with tarfile.open(fileobj=io.BytesIO(archive.extractfile('cmk_addons_plugins.tar').read())) as inner:
            assert sorted(inner.getnames()) == sorted(listed)
            for member in inner:
                name = PurePosixPath(member.name)
                assert not name.is_absolute() and '..' not in name.parts
                assert member.isfile() and name.parts[0] == 'morpheus'
                assert '__pycache__' not in name.parts and name.suffix != '.pyc'
                payload = inner.extractfile(member).read()
                assert payload == (ROOT / 'src' / member.name).read_bytes(), member.name
                assert member.mode == (0o755 if name.parent.name == 'libexec' else 0o644)
                if name.suffix == '.py' or name.name == 'agent_morpheus':
                    ast.parse(payload, filename=member.name)
    print('Package integrity: 10 files match source, manifests agree, paths and modes valid')
    print('Version contract: 1.2.0; minimum 2.4.0; Until Version 2.5.0p99 (exclusive)')
    print('SHA256:', hashlib.sha256(content).hexdigest())


if __name__ == '__main__':
    main()
