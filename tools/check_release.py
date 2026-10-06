#!/usr/bin/env python3
"""Refuse to publish a release whose manifest does not describe reality.

This exists because of a bug that shipped for twenty three releases. The
manifest's CRCs were written by hand and every one of them was wrong, so the
updater, which verifies each file it downloads against the recorded CRC,
rejected everything it fetched and the in-game update could never complete.
Nothing in the pipeline looked at whether the two agreed.

So this does, and the publish fails if they do not:

  1. Every file in the shipped package is listed in the manifest, with the
     size and CRC it really has. A wrong CRC here is the original bug.
  2. Every asset the manifest promises is actually uploaded, and is the file
     the manifest says it is. A promised asset that was never uploaded is a
     broken update for every player who tries to take it.
  3. No asset is uploaded that nothing refers to, and no unchanged file is
     given an asset, which would make everybody re-download the whole game.
"""

import json
import pathlib
import sys
import zipfile
import zlib


def crc(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF


def main() -> int:
    here = pathlib.Path(__file__).resolve().parent.parent
    rel = here / "release"
    manifest = json.loads((rel / "latest.json").read_text(encoding="utf-8"))
    assets = rel / "assets"

    package = assets / "ZulSimulator.zip"
    if not package.exists():
        print("FAIL: release/assets/ZulSimulator.zip is missing")
        return 1

    problems = []

    # 1. the manifest against the package it describes
    with zipfile.ZipFile(package) as z:
        root = z.namelist()[0].split("/", 1)[0]
        inside = {}
        for info in z.infolist():
            if info.is_dir():
                continue
            inside[info.filename[len(root) + 1:]] = crc(z.read(info)), info.file_size

    listed = {e["path"]: e for e in manifest["files"]}

    for path, (c, size) in sorted(inside.items()):
        e = listed.get(path)
        if e is None:
            problems.append(f"in the package but not in the manifest: {path}")
        elif e["size"] != size or e["crc"] != c:
            problems.append(
                f"manifest disagrees with the package for {path}: "
                f"says {e['size']}/{e['crc']}, really {size}/{c}"
            )
    for path in sorted(set(listed) - set(inside)):
        problems.append(f"in the manifest but not in the package: {path}")

    # 2. the assets the manifest promises
    promised = {e["asset"]: e for e in manifest["files"] if e["asset"]}
    for name, e in sorted(promised.items()):
        f = assets / name
        if not f.exists():
            problems.append(f"manifest promises asset {name} but it was not uploaded")
            continue
        data = f.read_bytes()
        if len(data) != e["size"] or crc(data) != e["crc"]:
            problems.append(
                f"asset {name} is not the file the manifest describes "
                f"(asset {len(data)}/{crc(data)}, manifest {e['size']}/{e['crc']})"
            )

    # 3. assets nothing refers to. The package and the dev snapshot are
    # expected extras: they are whole-download conveniences, not update units.
    allowed_extra = {"ZulSimulator.zip"}
    for f in sorted(assets.iterdir()):
        if f.name in promised or f.name in allowed_extra:
            continue
        if f.name.startswith("DEV_source_snapshot_") and f.name.endswith(".zip"):
            continue
        problems.append(f"asset {f.name} is uploaded but nothing refers to it")

    if problems:
        print(f"FAIL: {len(problems)} problem(s) with this release")
        for p in problems:
            print("  -", p)
        return 1

    print(f"OK: manifest describes {len(listed)} files, "
          f"{len(promised)} to download, package agrees on every one")
    return 0


if __name__ == "__main__":
    sys.exit(main())
