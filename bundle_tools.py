"""Download pinned Windows x64 runtimes, checking SHA-256 before extraction."""
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
PACKAGES = [
    ('FFmpeg', '9.0.2', 'https://github.com/GyanD/codexffmpeg/releases/download/9.0.2/ffmpeg-9.0.2-essentials_build.zip',
     '60f467265b1e312373dbcd92200c2618a74850f98d3d078e94296bb3fa2047ba', {'ffmpeg.exe', 'ffprobe.exe'}),
    ('Node.js', '22.23.4', 'https://nodejs.org/dist/v22.23.4/node-v22.23.4-win-x64.zip',
     'cbc74b5e0982c9dbb41525fd8fb5dcd32fbee237863f7829072f4639a1ce5f20', {'node.exe'}),
]


def main():
    cache = ROOT / 'build' / 'downloads'
    vendor = ROOT / 'vendor'
    cache.mkdir(parents=True, exist_ok=True)
    vendor.mkdir(exist_ok=True)
    manifest = []
    for name, version, url, digest, binaries in PACKAGES:
        target = cache / url.rsplit('/', 1)[1]
        if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            print('Downloading ' + name + ' ' + version, flush=True)
            urllib.request.urlretrieve(url, target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Checksum mismatch: ' + name)
        notices = vendor / 'licenses' / name
        notices.mkdir(parents=True, exist_ok=True)
        found = set()
        with zipfile.ZipFile(target) as archive:
            for item in archive.infolist():
                path = Path(item.filename)
                destination = None
                if path.name in binaries and len(path.parts) <= 3:
                    destination = vendor / path.name
                    found.add(path.name)
                elif len(path.parts) == 2 and path.name.lower().startswith(('license', 'copying', 'readme')) and not item.is_dir():
                    destination = notices / path.name
                if destination:
                    with archive.open(item) as source, destination.open('wb') as output:
                        shutil.copyfileobj(source, output)
        if found != binaries:
            raise RuntimeError('Missing runtime executables: ' + name)
        manifest.append({'name': name, 'version': version, 'url': url, 'sha256': digest})
    (vendor / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print('Bundled runtimes verified.', flush=True)


if __name__ == '__main__':
    main()
