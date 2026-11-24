#!/usr/bin/env python3
"""Refuse to publish a release whose manifest does not describe reality.

This exists because of a bug that broke the v144 update. The manifest's
checksums were computed with Python's zlib CRC-32, which is NOT what NVGT's
crc32() computes, so every number was wrong and the updater rejected every
file it downloaded. Nothing in the pipeline compared the manifest against the
engine's own view of the files.

So this does. It runs in one of two modes:

  * With the engine (an nvgt path as the first argument, or nvgt on PATH) it
    checks every checksum the way the game will: the manifest must agree with
    the engine on the size AND crc of every file, and every promised asset
    must be exactly the file the manifest describes. This is the check that
    catches a crc that drifts from what the game computes, and it is run when
    the manifest is built.

  * Without the engine (a CI runner has no nvgt) it does everything that does
    not need the engine: every file in the package is in the manifest and
    vice versa, every size matches, every promised asset is present and the
    right size, and nothing unreferenced was uploaded. It does NOT re-verify
    the crc values, because only the engine can; those were already verified
    against the engine when the manifest was built.

Either way the publish fails if:

  1. The manifest disagrees with the package it describes.
  2. An asset the manifest promises was never uploaded, or is not that file.
  3. An asset is uploaded that nothing refers to.
"""

import json
import os
import pathlib
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from make_manifest import nvgt_checksums, unpack  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent.parent


def file_sizes(root: pathlib.Path) -> dict:
    """{relative path: size} for every file under root, no engine needed."""
    return {
        str(p.relative_to(root)).replace(os.sep, "/"): p.stat().st_size
        for p in root.rglob("*") if p.is_file()
    }


def resolve_engine() -> str | None:
    """An explicit nvgt path wins; otherwise nvgt on PATH; otherwise none."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    return "nvgt" if shutil.which("nvgt") else None


def main() -> int:
    nvgt = resolve_engine()
    rel = HERE / "release"
    manifest = json.loads((rel / "latest.json").read_text(encoding="utf-8"))
    assets = rel / "assets"
    package = assets / "ZulSimulator.zip"
    if not package.exists():
        print("FAIL: release/assets/ZulSimulator.zip is missing")
        return 1

    problems = []
    tmp = pathlib.Path(tempfile.mkdtemp())
    root = unpack(str(package), tmp / "pkg")
    listed = {e["path"]: e for e in manifest["files"]}
    promised = {e["asset"]: e for e in manifest["files"] if e["asset"]}

    if nvgt:
        inside = nvgt_checksums(nvgt, root)
        for path, (size, crc) in sorted(inside.items()):
            e = listed.get(path)
            if e is None:
                problems.append(f"in the package but not in the manifest: {path}")
            elif e["size"] != size or e["crc"] != crc:
                problems.append(f"manifest disagrees with the package for {path}: "
                                f"says {e['size']}/{e['crc']}, nvgt says {size}/{crc}")
        for path in sorted(set(listed) - set(inside)):
            problems.append(f"in the manifest but not in the package: {path}")

        asset_crcs = nvgt_checksums(nvgt, assets)
        for name, e in sorted(promised.items()):
            got = asset_crcs.get(name)
            if got is None:
                problems.append(f"manifest promises asset {name} but it was not uploaded")
            elif got != (e["size"], e["crc"]):
                problems.append(f"asset {name} is not the file the manifest describes "
                                f"(asset {got[0]}/{got[1]}, manifest {e['size']}/{e['crc']})")
    else:
        inside = file_sizes(root)
        for path, size in sorted(inside.items()):
            e = listed.get(path)
            if e is None:
                problems.append(f"in the package but not in the manifest: {path}")
            elif e["size"] != size:
                problems.append(f"manifest disagrees with the package for {path}: "
                                f"says {e['size']} bytes, package has {size}")
        for path in sorted(set(listed) - set(inside)):
            problems.append(f"in the manifest but not in the package: {path}")

        asset_sizes = file_sizes(assets)
        for name, e in sorted(promised.items()):
            got = asset_sizes.get(name)
            if got is None:
                problems.append(f"manifest promises asset {name} but it was not uploaded")
            elif got != e["size"]:
                problems.append(f"asset {name} is {got} bytes, manifest says {e['size']}")

    present = [f for f in assets.iterdir() if f.is_file()]
    for f in sorted(present):
        if f.name in promised or f.name == "ZulSimulator.zip":
            continue
        if f.name.startswith("DEV_source_snapshot_") and f.name.endswith(".zip"):
            continue
        problems.append(f"asset {f.name} is uploaded but nothing refers to it")

    if problems:
        print(f"FAIL: {len(problems)} problem(s) with this release")
        for p in problems:
            print("  -", p)
        return 1
    if nvgt:
        print(f"OK: manifest describes {len(listed)} files, {len(promised)} to download, "
              f"nvgt agrees on every one")
    else:
        print(f"OK (structural, no engine): manifest describes {len(listed)} files, "
              f"{len(promised)} to download; every path and size matches, and every "
              f"promised asset is present and the right size. Checksums were verified "
              f"against the engine when the manifest was built.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
