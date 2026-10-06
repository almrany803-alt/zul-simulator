#!/usr/bin/env python3
"""Generate update/latest.json for a Zul Simulator release.

The updater compares every file it has, and every file it downloads, against
the size and checksum recorded here. A file that disagrees is re-downloaded,
and a download that disagrees is rejected outright.

So the checksums MUST be the numbers the game itself computes. They were once
reimplemented here in Python with zlib's CRC-32. NVGT's crc32() is not zlib's,
so every number was wrong, and the resulting manifest made the updater refuse
every file it fetched: "could not fetch changes.txt after three tries". The
checksums now come from NVGT itself, by running it over the files, because the
engine that will later check them is the only honest source of them.

Usage:
  make_manifest.py --package ZulSimulator.zip \
                   --previous-package prev_ZulSimulator.zip \
                   --previous update/latest.json \
                   --version v144 \
                   --notes-file NOTES.md \
                   --out latest.json \
                   --assets-dir release/assets \
                   --nvgt /path/to/nvgt
"""

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import zipfile

REPO = "almrany803-alt/zul-simulator"
CRC_SCRIPT = pathlib.Path(__file__).resolve().parent / "nvgt_crc.nvgt"


def asset_name(path: str) -> str:
    """Release assets are one flat namespace, so a path becomes a name.

    chars/grazyna.char is uploaded as chars__grazyna.char. The updater reverses
    this, so the separator must stay exactly two underscores.
    """
    return path.replace("/", "__")


def unpack(package: str, where: pathlib.Path) -> pathlib.Path:
    with zipfile.ZipFile(package) as z:
        roots = {n.split("/", 1)[0] for n in z.namelist()}
        if len(roots) != 1:
            raise SystemExit(f"expected one top-level folder, found {sorted(roots)}")
        z.extractall(where)
    return where / roots.pop()


def nvgt_checksums(nvgt: str, root: pathlib.Path) -> dict:
    """{relative path: (size, crc)} with the crc computed BY NVGT."""
    paths = sorted(
        str(p.relative_to(root)).replace(os.sep, "/")
        for p in root.rglob("*") if p.is_file()
    )
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as lf:
        for rel in paths:
            lf.write(f"{root / rel}\n")
        listfile = lf.name
    try:
        out = subprocess.run([nvgt, str(CRC_SCRIPT), listfile],
                             capture_output=True, text=True, check=True).stdout
    finally:
        os.unlink(listfile)

    result = {}
    errors = []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("ERROR"):
            errors.append(line)
            continue
        if "|" not in line:
            continue
        full, size, crc = line.rsplit("|", 2)
        rel = str(pathlib.Path(full).relative_to(root)).replace(os.sep, "/")
        result[rel] = (int(size), int(crc))
    if errors:
        raise SystemExit("nvgt could not read:\n  " + "\n  ".join(errors))
    missing = set(paths) - set(result)
    if missing:
        raise SystemExit(f"nvgt returned nothing for {len(missing)} files, e.g. {sorted(missing)[:3]}")
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--package", required=True)
    p.add_argument("--previous-package", required=True,
                   help="the previous release's ZulSimulator.zip, as ground truth")
    p.add_argument("--previous", required=True, help="previous latest.json, for feedback_key")
    p.add_argument("--version", required=True)
    p.add_argument("--notes-file", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--assets-dir")
    p.add_argument("--nvgt", default="nvgt", help="the nvgt interpreter")
    a = p.parse_args()

    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        cur_root = unpack(a.package, tmp / "cur")
        prev_root = unpack(a.previous_package, tmp / "prev")
        current = nvgt_checksums(a.nvgt, cur_root)
        previous = nvgt_checksums(a.nvgt, prev_root)

        prev_manifest = json.load(open(a.previous, encoding="utf-8"))

        files, changed, added = [], [], []
        for path in sorted(current):
            size, crc = current[path]
            was = previous.get(path)
            if was is None:
                added.append(path); fresh = True
            elif was != (size, crc):
                changed.append(path); fresh = True
            else:
                fresh = False
            files.append({"path": path, "size": size, "crc": crc,
                          "asset": asset_name(path) if fresh else ""})

        removed = sorted(set(previous) - set(current))

        manifest = {
            "version": a.version,
            "notes": open(a.notes_file, encoding="utf-8").read().strip(),
            "base": f"https://github.com/{REPO}/releases/download/{a.version}/",
            "full_download":
                f"https://github.com/{REPO}/releases/latest/download/ZulSimulator.zip",
            "feedback_key": prev_manifest["feedback_key"],
            "files": files,
            "remove": removed,
        }
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, ensure_ascii=False, indent=1)
            fh.write("\n")

        if a.assets_dir:
            os.makedirs(a.assets_dir, exist_ok=True)
            for e in files:
                if e["asset"]:
                    shutil.copyfile(cur_root / e["path"],
                                    pathlib.Path(a.assets_dir, e["asset"]))

        # The check that matters: an unchanged file's checksum must still equal
        # what the PREVIOUS manifest published for it. If the generator's idea
        # of a checksum ever drifts from the game's again, this disagrees.
        prev_published = {e["path"]: e["crc"] for e in prev_manifest["files"]}
        agree = disagree = absent = 0
        for e in files:
            if e["asset"]:
                continue
            was = prev_published.get(e["path"])
            if was is None: absent += 1
            elif was == e["crc"]: agree += 1
            else:
                disagree += 1
                print(f"  DRIFT: {e['path']} was published as {was}, now computed {e['crc']}")
        print(f"  version   : {a.version}")
        print(f"  files     : {len(files)}   changed {len(changed)}   added {len(added)}   removed {len(removed)}")
        print(f"  unchanged files agreeing with the previous manifest: {agree}")
        if absent:
            print(f"  unchanged files the previous manifest never listed : {absent}")
        if disagree:
            raise SystemExit(f"  {disagree} unchanged file(s) disagree with what was already published; refusing")
        for path in changed: print(f"    changed  {path}")
        for path in added:   print(f"    added    {path}")
        for path in removed: print(f"    removed  {path}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
