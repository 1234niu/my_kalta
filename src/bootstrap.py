"""Restore pinned author assets and macOS ARM64 Java 24 from recorded provenance."""
import hashlib
import json
from pathlib import Path
import platform
import tarfile
import urllib.request
from katia import ROOT, digest


def download(url,path,expected,algorithm):
    if path.exists() and hashlib.new(algorithm,path.read_bytes()).hexdigest()==expected:
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    part=path.with_suffix('.partial')
    with urllib.request.urlopen(url,timeout=240) as response,part.open('wb') as f:
        while chunk:=response.read(1024*1024): f.write(chunk)
    if hashlib.new(algorithm,part.read_bytes()).hexdigest()!=expected:
        raise ValueError('Checksum mismatch: '+str(path))
    part.replace(path)


def main():
    metadata=json.loads((ROOT/'vendor/katia/figshare-metadata.json').read_text())
    for f in metadata['files']:
        path=ROOT/'dataset/raw/constantinople.csv' if f['name']=='final_dataset.csv' else ROOT/'vendor/katia'/f['name']
        download(f['download_url'],path,f['computed_md5'],'md5')
    if platform.system()!='Darwin' or platform.machine()!='arm64':
        print('Author assets verified. Install Java 24+ and set KATIA_JAVA on this platform.');return
    m=json.loads((ROOT/'dataset/provenance/jdk24.json').read_text())
    archive=ROOT/'.tools/jdk24.tar.gz'
    download(m['download_url'],archive,m['sha256_hash'],'sha256')
    dest=ROOT/'.tools'/m['name'].removesuffix('.tar.gz')
    if not dest.exists():
        with tarfile.open(archive) as tar:
            base=(ROOT/'.tools').resolve()
            for e in tar.getmembers():
                if not (base/e.name).resolve().is_relative_to(base): raise ValueError('Archive traversal')
                if e.issym() and not (base/e.name).parent.joinpath(e.linkname).resolve().is_relative_to(base):
                    raise ValueError('Unsafe symlink')
                if e.islnk() and not (base/e.linkname).resolve().is_relative_to(base): raise ValueError('Unsafe hard link')
                if not (e.isdir() or e.isfile() or e.issym() or e.islnk()): raise ValueError('Unsupported entry')
            tar.extractall(base)
    print('Author assets and Java 24 verified')

if __name__=='__main__':main()
