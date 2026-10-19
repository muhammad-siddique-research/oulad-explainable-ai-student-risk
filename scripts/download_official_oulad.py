"""Download the authors' official OULAD release with deposit checksums.

Metadata: https://api.figshare.com/v2/articles/5081998
Deposit DOI: https://doi.org/10.6084/m9.figshare.5081998
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
import requests

API = "https://api.figshare.com/v2/articles/5081998"
EXPECTED = {
    "studentInfo.csv", "studentRegistration.csv", "studentVle.csv",
    "studentAssessment.csv", "assessments.csv", "courses.csv", "vle.csv",
}


def digest(path: Path, algorithm: str = "sha256") -> str:
    checksum = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(data)
    return checksum.hexdigest()


def safe_extract(archive: Path, destination: Path) -> list[str]:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with zipfile.ZipFile(archive) as handle:
        for member in handle.infolist():
            destination_path = (root / member.filename).resolve()
            if not destination_path.is_relative_to(root):
                raise ValueError(f"Unsafe ZIP path: {member.filename}")
        handle.extractall(root)
    candidates = {p.name: p for p in destination.rglob("*.csv") if p.is_file()}
    missing = EXPECTED - candidates.keys()
    if missing:
        raise RuntimeError(f"Original archive missing CSVs: {sorted(missing)}")
    for filename in EXPECTED:
        source, target = candidates[filename], destination / filename
        if source != target:
            if target.exists():
                raise FileExistsError(f"Duplicate original table: {filename}")
            source.replace(target)
    return sorted(EXPECTED)


def download(destination: Path, *, timeout: int = 90, overwrite: bool = False) -> dict:
    destination.mkdir(parents=True, exist_ok=True)
    response = requests.get(API, timeout=timeout)
    response.raise_for_status()
    files = response.json().get("files", [])
    if not files:
        raise RuntimeError("The official Figshare metadata contains no downloadable files")
    archives = []
    for info in files:
        name = Path(info["name"]).name
        if not name.lower().endswith(".zip"):
            continue
        final = destination / name
        if not final.exists() or overwrite:
            url = info.get("download_url") or f"https://ndownloader.figshare.com/files/{info['id']}"
            if not url.startswith(("https://ndownloader.figshare.com/", "https://figshare.com/ndownloader/")):
                raise ValueError("Refusing a download URL outside the approved deposit domain")
            temporary = final.with_name(name + ".part")
            with requests.get(url, timeout=timeout, stream=True) as download_response:
                download_response.raise_for_status()
                with temporary.open("wb") as out:
                    for block in download_response.iter_content(chunk_size=1024 * 1024):
                        if block:
                            out.write(block)
            temporary.replace(final)
        claimed_md5 = info.get("supplied_md5") or info.get("computed_md5")
        if claimed_md5 and digest(final, "md5").lower() != claimed_md5.lower():
            raise ValueError(f"Deposit digest does not match: {name}")
        tables = safe_extract(final, destination)
        archives.append({
            "filename": name, "figshare_id": info["id"],
            "download_url": info.get("download_url"), "size": final.stat().st_size,
            "archive_sha256": digest(final), "deposit_md5": claimed_md5,
            "tables": tables,
        })
    if not archives:
        raise RuntimeError("No ZIP found in the official Figshare record")
    audit = {
        "source": "Official OULAD Figshare deposit",
        "dataset_doi": "https://doi.org/10.6084/m9.figshare.5081998",
        "data_descriptor": "https://doi.org/10.1038/sdata.2017.171",
        "license": "CC BY 4.0", "archives": archives,
        "extracted_tables": [
            {"filename": name, "sha256": digest(destination / name),
             "bytes": (destination / name).stat().st_size}
            for name in sorted(EXPECTED)
        ],
    }
    (destination / "dataset_provenance.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    return audit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", default="data/raw")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    print(json.dumps(download(Path(args.destination), overwrite=args.overwrite), indent=2))
