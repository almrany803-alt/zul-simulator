# Testing Zul Simulator: what we have, and where it is thin

Written 7 October 2026, after a run of bugs that the suite did not catch. The
short version: the suite is strong where it looks, and it does not look at one
whole layer. That layer is where the recent faults lived.

## What the suite already does, and does well

This is not a thin suite. It runs on every build through `build.sh`, it refuses
to package if a single check fails, and it is genuinely beta-tester shaped.

- **A robot that plays, not a list of asserts.** Five personas (achiever,
  socialiser, killer, explorer, fumbler) each score the available actions and
  play emergently, with a novelty bonus so they fan out instead of grooving.
  The fumbler exists on purpose: it reaches for the awkward thing (give to
  nobody, cash in an empty bag) more than any real person would, so the game
  is poked where a polite tester would not poke.
- **It drives the real menus.** `rb_try` and the scripted-input section press
  down, down, enter, escape through the actual menu functions, and flag any
  option that answers with silence. A player pressing a thing and hearing
  nothing is a bug, and the suite hears it.
- **It listens for stolen speech.** If a line starts before the last one has
  been heard, that is counted.
- **It checks the sounds exist.** `rb_check_asset` opens every sound path the
  play touched and reports the ones that are not on disk.
- **Common-sense rules, written by hand, checked by machine.** `rb_preconditions`
  encodes things a person takes for granted (you cannot hand something to
  somebody across the area; people should not appear in the place-tracking
  menu) and reports MAKES NO SENSE when the game breaks one.
- **An invariant fuzzer.** 2000 random operations, and after each one it checks
  that money, energy, the clock, the map position and a dozen other values are
  all inside their legal range.
- **Coverage is enforced.** `tools/check_coverage.py` fails the build if any
  game function is never exercised by a test. `tools/check_script_keys.py`
  fails if the game reads a key the harness cannot press. These stop a feature,
  or a whole control, from shipping with no test behind it.
- **Content completeness.** Every language is checked key for key, with no
  MISSING markers, and the two shipped languages are held level.

If the question is "does the suite test the game," the answer is yes, and
better than most.

## The blind spot: the distribution layer

Everything above tests the game **running from source on Linux**. None of it
tests the game **as a player receives it**: a compiled Windows build, updating
itself from a published manifest, fetching a sound pack from a published list.
Every serious fault of the last few sessions lived in exactly that gap.

1. **The update manifest checksums were wrong for twenty-three releases, and
   then wrong again in a new way.** The updater's own tests set the expected
   checksum with the same `crc32()` they then verify against:

       upd_crc[0] = crc32("hello");
       check("an unchanged file is not downloaded again", upd_changed_files().length() == 0);

   That is self-consistent. It passes whatever `crc32` actually computes, so it
   can never notice that the *generator* that wrote the manifest used a
   different checksum (standard zlib) than the game does. The v144 manifest was
   generated with zlib and the game rejected every file. No test could see it,
   because no test compared a real published file against a real published
   manifest using the real engine.

2. **The sound pack had the same wrong checksums, plus a second fault.** The
   pack tests unpack a pack file made locally, in the same run, so again the
   numbers agree with themselves. Nothing fetched the real parts and checked
   them against the real `pack.txt`. On top of that, the game parsed each
   checksum with `uint(parse_double(...))`, which clamps anything at or above
   2^31 down to one fixed number; three of the eight real parts land there and
   could never have verified. That line had no test at all until now.

3. **Two checks silently passed in every packaged release.** They read
   `zul.nvgt` off disk to prove wiring. The player has no source, so on a real
   build they could not run, and `check_src` quietly skipped them. A contributor
   found this, not us, because we only ever ran the suite from the source
   folder.

The pattern is the same one the first law in PROJECT_STATE.md already names,
pointed at a part we had not pointed it at: **test the artefact the player gets,
with the engine they run, not the code on our disk.**

## The improvements, in priority order

### 1. Verify every release against itself, on the real engine (highest value)

After a build, and again after publishing, download the actual assets and check
every one against the manifest using a checksum from NVGT itself, not from a
Python reimplementation. This single gate would have caught faults 1 and 2 the
moment they were made.

- `tools/make_manifest.py --nvgt` now takes the checksums from the engine by
  running it over the files, so the manifest is correct by construction.
- `tools/check_release.py` re-checks the manifest against the package. Given an
  NVGT binary it checks real checksums; without one (on a plain CI runner) it
  falls back to sizes and file lists. It is run with the engine before every
  push.
- **Still to add:** a post-publish step that downloads the live assets and
  verifies them, so a corruption in upload is caught too, not just a mistake in
  generation.

### 2. Run the suite on real Windows, not only Linux (now possible)

NVGT's `crc32` is not the same between the 0.89.1 engine the game ships with and
the 0.90.0 development engine, and it is not standard zlib in 0.89.1. The game is
only ever run by players on Windows. We can now cross-compile a probe, or the
whole game, with the exact `stub/nvgt_windows.bin` that builds `zul.exe`, and run
it on a GitHub Windows runner. The suite should run there as well as on Linux, so
an engine difference between the two surfaces as a failure rather than as a live
bug. The soundpack fix was proven this way before it shipped.

### 3. Check that a quest's words match what it counts

VanTrung2807's bugs were all one shape: the description promised a result and the
code counted an attempt (beg for ten zloty, counted asks; talk to three people,
counted sentences). The fixes are in, with permanent checks, but the general
guard is worth building: for each daily job, assert that the thing it counts is
the thing its description names. A small table of (job, described goal, counter)
with a test that walks it would stop the next one.

### 4. Test interruption and recovery as a matter of course

The updater retries three times; the pack refuses a part under 64 bytes and
retries; saves survive a changed layout. These exist and some are tested. What is
not systematic: a test that hands each downloader a truncated or empty response
and asserts the player is told the truth and left with a working game. Worth
making a section of its own rather than scattered checks.

### 5. A nonsense-speech judge (speculative, lower priority)

The suite proves speech keys exist and that something is said. It cannot tell
whether what is said makes sense in context; only a person can, today. If it is
ever worth it, the play log of spoken lines could be read by a language model in
CI and flagged for lines that do not fit their situation. This is a maybe, not a
plan.

## The standing habit, unchanged

None of the above replaces the first law. A machine check catches forgetting and
drift in the numbers; it cannot catch prose gone stale or a feature a player can
reach but no persona thought to try. Before any release, the game still goes in
front of an imagined Kevin or Longshoot, and the question is still what THEY would
do, with the engine and the build they actually have.
