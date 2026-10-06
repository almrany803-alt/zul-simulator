#!/usr/bin/env python3
"""Generate update/latest.json for a Zul Simulator release.

The updater reads this manifest and compares, for every file it has on disk,
the size and CRC recorded here. A file whose size or CRC differs, or that the
player does not have at all, is re-downloaded from the release, which is why a
changed file needs an `asset` name: that is the release asset to fetch. An
unchanged file carries an empty `asset`, so nobody downloads it again.

This used to be worked out by hand every release. Doing it by hand is how you
ship a manifest that says a file is unchanged when it is not, and then nobody
gets the fix and nothing looks wrong.

Usage:
  make_manifest.py --package ZulSimulator.zip \
                   --previous update/latest.json \
                   --version v144 \
                   --notes-file NOTES.md \
                   --out latest.json \
                   --assets-dir release/assets
"""

import argparse
import json
import os
import pathlib
import zipfile
import zlib

REPO = "almrany803-alt/zul-simulator"

# Files that live in the package but are not part of what the updater manages.
# Nothing right now; kept so the reason is written down if that ever changes.
SKIP = set()


def asset_name(path: str) -> str:
    """Release assets live in one flat namespace, so a path becomes a name.

    GitHub has no folders in a release, so chars/grazyna.char is uploaded as
    chars__grazyna.char. The updater reverses this, so the separator must stay
    exactly two underscores.
    """
    return path.replace("/", "__")


def read_package(package: str):
    """Return {path: (size, crc)} for every file in the package.

    Paths in the manifest are relative to the game folder, so the leading
    "Zul Simulator/" is stripped. Directory entries are skipped: the updater
    creates directories as it writes files.
    """
    out = {}
    with zipfile.ZipFile(package) as z:
        names = z.namelist()
        roots = {n.split("/", 1)[0] for n in names}
        if len(roots) != 1:
            raise SystemExit(
                f"expected one top-level folder in the package, found {sorted(roots)}"
            )
        root = roots.pop()
        for info in z.infolist():
            if info.is_dir():
                continue
            rel = info.filename[len(root) + 1:]
            if not rel or rel in SKIP:
                continue
            data = z.read(info)
            if len(data) != info.file_size:
                raise SystemExit(f"short read on {rel}")
            out[rel] = (info.file_size, zlib.crc32(data) & 0xFFFFFFFF)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--package", required=True)
    p.add_argument("--previous", required=True,
                   help="previous update/latest.json, for feedback_key only")
    p.add_argument("--previous-package", required=True,
                   help="the previous release's ZulSimulator.zip, as ground truth")
    p.add_argument("--version", required=True)
    p.add_argument("--notes-file", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--assets-dir")
    p.add_argument("--extract-root", help="folder holding the loose game files")
    a = p.parse_args()

    current = read_package(a.package)
    prev = json.load(open(a.previous, encoding="utf-8"))

    # Deliberately NOT prev["files"] crcs. Those were hand-made and are wrong:
    # measured against the real v143 assets they disagree, which is why the
    # updater rejected every file it downloaded. The previous PACKAGE is the
    # only honest statement of what players actually have, so diff against it.
    prev_files = read_package(a.previous_package)

    files, changed, added = [], [], []
    for path in sorted(current):
        size, crc = current[path]
        was = prev_files.get(path)
        if was is None:
            added.append(path)
            is_new = True
        elif was != (size, crc):
            changed.append(path)
            is_new = True
        else:
            is_new = False
        files.append({
            "path": path,
            "size": size,
            "crc": crc,
            "asset": asset_name(path) if is_new else "",
        })

    removed = sorted(set(prev_files) - set(current))

    manifest = {
        "version": a.version,
        "notes": open(a.notes_file, encoding="utf-8").read().strip(),
        "base": f"https://github.com/{REPO}/releases/download/{a.version}/",
        "full_download":
            f"https://github.com/{REPO}/releases/latest/download/ZulSimulator.zip",
        "feedback_key": prev["feedback_key"],
        "files": files,
        "remove": removed,
    }

    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    # Write out exactly the assets the manifest promises, so the two can never
    # disagree: a manifest naming an asset that was never uploaded is a broken
    # update for every player.
    if a.assets_dir:
        os.makedirs(a.assets_dir, exist_ok=True)
        with zipfile.ZipFile(a.package) as z:
            root = z.namelist()[0].split("/", 1)[0]
            for e in files:
                if not e["asset"]:
                    continue
                data = z.read(f"{root}/{e['path']}")
                pathlib.Path(a.assets_dir, e["asset"]).write_bytes(data)

    print(f"  version    : {a.version}")
    print(f"  files      : {len(files)}")
    print(f"  changed    : {len(changed)}")
    print(f"  added      : {len(added)}")
    print(f"  removed    : {len(removed)}")
    print(f"  unchanged  : {len(files) - len(changed) - len(added)}")
    for path in changed:
        print(f"    changed  {path}")
    for path in added:
        print(f"    added    {path}")
    for path in removed:
        print(f"    removed  {path}")


if __name__ == "__main__":
    main()
