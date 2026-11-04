"""Provision exact historical ZIPs, never regenerate evidence or execute its code.

The versioned manifest is an unchanged STEP49 byte copy. Missing/expired remote
artifacts, conflicting bytes and invalid archives are hard errors. Existing local
archives can be verified offline; they are never overwritten or silently repaired.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request

import phase2d_step50_reproduction as original

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/'docs/phase2d-final-evidence/original-archive-manifest.json'
MANIFEST_SHA256 = '4ca1db2a783f2d62295e5ec2ef623b434a03c1b5a2a485f728c0f67df3d4a26e'
ARCHIVES = ROOT/'results/phase2d/step49-original-archives-20261102-120255-a1314650'
REPOSITORY = 'Nejatbakhsh-y/stellarator-robust-magnetic-optimization'
API = 'https://api.github.com/repos/'+REPOSITORY


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def api(path, token, binary=False):
    """Never forward the GitHub credential to an artifact storage redirect."""
    if not token:
        raise ValueError('GITHUB_TOKEN with actions:read required for historical retrieval')
    request = urllib.request.Request(API+path, headers={
        'Authorization': 'Bearer '+token, 'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'stellarator-evidence-provisioner'})
    try:
        response = urllib.request.build_opener(NoRedirect).open(request, timeout=60)
    except urllib.error.HTTPError as exc:
        if not binary or exc.code != 302:
            raise RuntimeError(f'Historical GitHub retrieval HTTP {exc.code}: {path}') from None
        location = exc.headers.get('Location', '')
        parsed = urllib.parse.urlsplit(location)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError('Unsafe artifact download redirect')
        # New request, no Authorization header. No archived code is executed.
        response = urllib.request.urlopen(location, timeout=60)
    with response:
        raw = response.read((original.MAX_ARCHIVE if binary else 8*1024**2)+1)
    if len(raw) > (original.MAX_ARCHIVE if binary else 8*1024**2):
        raise ValueError('Historical retrieval size limit')
    return raw if binary else original.decode(raw)


def pinned_manifest():
    raw = MANIFEST.read_bytes()
    if original.digest(raw) != MANIFEST_SHA256:
        raise ValueError('Original manifest SHA256 mismatch')
    value = original.decode(raw)
    records = [a for r in value['runs'] for a in r['artifacts']]
    if (value['repository'] != REPOSITORY or len(value['runs']) != 4
            or len(records) != 71 or len({a['id'] for a in records}) != 71
            or len({a['file'] for a in records}) != 71):
        raise ValueError('Incomplete original manifest')
    for run in value['runs']:
        for item in run['artifacts']:
            if (item['file'] != f"{run['run_id']}/artifact-{item['id']}.zip"
                    or item['github_sha256'] != 'sha256:'+item['verified_sha256']):
                raise ValueError('Conflicting original artifact identity')
    return raw, value


def remote_inventory(run, token, request=api):
    records, page = [], 1
    while True:
        value = request(f"/actions/runs/{run['run_id']}/artifacts?per_page=100&page={page}", token)
        entries = value['artifacts']
        records.extend(entries)
        if len(records) >= value['total_count']:
            break
        if not entries:
            raise ValueError('Incomplete remote artifact pagination')
        page += 1
    by_id = {a['id']: a for a in records}
    if len(by_id) != len(records):
        raise ValueError('Duplicate remote artifact identity')
    for item in run['artifacts']:
        meta = by_id.get(item['id'])
        if meta is None or meta.get('expired'):
            raise ValueError(f"Original artifact missing/expired: {item['id']}")
        if (meta['digest'] != item['github_sha256'] or meta['name'] != item['name']
                or meta['workflow_run']['id'] != run['run_id']
                or meta['workflow_run']['head_sha'] != run['source_sha']):
            raise ValueError(f"Original artifact metadata mismatch: {item['id']}")
    return by_id


def verify(path, item):
    members = original.archive(path, item['verified_sha256'])
    if not members or any(r['status'] == 'MISMATCH'
                          for seal in original.seals(members) for r in seal['records']):
        raise ValueError('Original internal manifest mismatch')
    return len(members)


def provision(root, token=None, request=api, verify_only=False):
    raw, manifest = pinned_manifest()
    root = Path(root).absolute()
    if root.is_symlink() or any(p.is_symlink() for p in root.parents):
        raise ValueError('Historical archive root must not use symbolic links')
    target_manifest = root/'manifest.json'
    if target_manifest.is_symlink():
        raise ValueError('Historical manifest must not be a symbolic link')
    if target_manifest.exists() and target_manifest.read_bytes() != raw:
        raise ValueError('Existing historical manifest differs; never overwrite')
    rows = []
    for run in manifest['runs']:
        paths = [(item, root/item['file']) for item in run['artifacts']]
        missing = [item for item, path in paths if not path.exists()]
        if missing and verify_only:
            raise FileNotFoundError('Original archives unavailable in verify-only mode')
        if missing:
            remote_inventory(run, token, request)
        for item, path in paths:
            source = 'EXISTING_PINNED_BYTES'
            if not path.exists():
                raw_zip = request(f"/actions/artifacts/{item['id']}/zip", token, binary=True)
                if original.digest(raw_zip) != item['verified_sha256']:
                    raise ValueError(f"Original downloaded SHA256 mismatch: {item['id']}")
                path.parent.mkdir(parents=True, exist_ok=True)
                if path.parent.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
                    raise ValueError('Historical output path escape')
                # Exclusive creation: do not replace any existing historical bytes.
                with path.open('xb') as stream:
                    stream.write(raw_zip)
                source = 'GITHUB_ORIGINAL_ARTIFACT'
            members = verify(path, item)
            rows.append(dict(artifact_id=item['id'], sha256=item['verified_sha256'],
                             source=source, members_verified=members))
    # The manifest is published only after all original ZIPs validate.
    if not target_manifest.exists():
        with target_manifest.open('xb') as stream:
            stream.write(raw)
    return dict(status='PASS', manifest_sha256=MANIFEST_SHA256, archives=rows,
                historical_replay='PROVISIONED_NOT_SCIENTIFIC_ACCEPTANCE',
                scientific_acceptance='NOT_ESTABLISHED', production_acceptance='FAIL')


def main(argv=None):
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--archive-root', type=Path, default=ARCHIVES)
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args(argv)
    if args.report.exists():
        parser.error('Fresh provisioning report required')
    args.report.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = provision(args.archive_root, os.getenv('GITHUB_TOKEN'), verify_only=args.verify_only)
        code = 0
    except Exception as exc:
        result = dict(status='FAIL', error=str(exc), historical_replay='MISSING_OR_INVALID_EVIDENCE',
                      scientific_acceptance='NOT_ESTABLISHED', production_acceptance='FAIL')
        code = 1
    with args.report.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'archives'}))
    return code


if __name__ == '__main__':
    sys.exit(main())
