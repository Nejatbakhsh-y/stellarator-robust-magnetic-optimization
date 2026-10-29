"""Portable source fingerprints; numerical evidence retains raw byte hashes."""
import hashlib
from pathlib import Path


def file_hash(path):
    path = Path(path)
    raw = path.read_bytes()
    if path.suffix == '.py' or path.parent.name == 'configs' or path.name == '.gitattributes':
        raw = raw.replace(b'\r\n', b'\n')
    return hashlib.sha256(raw).hexdigest()
