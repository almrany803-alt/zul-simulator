# What's new in Zul Simulator

The newest changes are at the top. The game reads these out to you when an update
is ready, so you do not need to come here unless you want to.

## 15 November 2026

**The Vietnamese is complete.** VanTrung2807, who translated the game, has added
the last line that was still falling back to English and brought the Vietnamese
notes fully up to date.

## 7 October 2026

**The extra sound pack downloads.** If you went looking for it before, the game
tried, failed on the very first piece, and told you nothing had changed. It was
checking each piece it pulled down against the wrong fingerprint, so every piece
looked broken when it was perfectly fine. Two faults sat behind it: the list of
fingerprints was written with the wrong kind of checksum, and the game clamped
any fingerprint past a certain size down to one fixed number, which three of the
eight pieces happened to land on. Both fixed, and proven on the real engine:
all eight pieces come down and install.

---

## 6 October 2026

**The game speaks Vietnamese.** VanTrung2807 found the repository, translated the
whole thing, and sent it in: every line of the game, the map names, and the notes
you are reading now. It is the first contribution Zul Simulator has had from
anybody outside the two of us. Pick it in Options, or when you first start.

It is listed as "Vietnamese" rather than "Tiếng Việt", which is the more
courteous way to write it, because the list is read aloud and an English screen
reader voice makes a mess of the diacritics. The person who most needs to find
that line is the one least likely to recognise what came out of it.

**The daily jobs now mean what they say.** Every one of these was the same
mistake: the words promised a result and the code counted an attempt.

Begging for ten złoty counts the złoty people actually put in your hand. It used
to count how many times you asked, and count it before seeing whether anybody
gave you anything, so ten refusals in a row finished the job with nothing in your
pocket. Talking to three people counts three people, once each a day, rather than
three sentences at the same long-suffering person. Having three drinks counts
bottles you finish rather than mouthfuls, so three pulls on the same bottle is no
longer a day's drinking. The earning job counts what comes in over the day, which
is what it always did, and now says so instead of promising what is in your
pocket. Patching things up only counts people you were actually on bad terms
with.

Two of them got harder and both were measured rather than guessed at: ten złoty
now takes about eighteen asks, roughly two thirds of a tank of energy, and three
beers over a day costs six złoty and leaves you merry rather than on the floor.

**Behind it.** Two tests had been passing for twenty three releases without doing
anything, because they only worked when run from the source folder rather than
from the game as players have it. VanTrung2807 found those too. They now run
inside the game like everything else.

---

## 6 August 2026

**A night in the cell.** Getting nicked is no longer a hole in your day. You now
get four turns inside, and what you manage to do with them depends on how much
you have had and on who you are.

You say what you mean to do. Sober, you do it. Drunk, it gets away from you, and
the drink only pulls one way: losing your temper never takes any effort, while
sitting quiet, listening at the door or talking sense through the wall all take
composure you might not have. Choosing to hold it together is always worth
something, even when you are legless, but by then it is a long shot.

What you do when you lose it depends on who you are. Krzysztof apologises to
everyone, including the door. Marcin gets onto the subject of Darek. Sebastian
attempts to do business with a police officer through a locked door. Tom recites
poetry at a wall in a language nobody here reads.

While you are drunk, what the game tells you at the time is what you *think*
happened, and you are being generous with yourself. The morning tells you the
truth, and then the desk decides how much of your property you are getting back.

Crossing the line still means the town is finished with you. Nothing you do in a
cell buys any of that back.

**The game updates itself now.** When you start it, it quietly checks whether
there is anything new, tells you what has changed, and asks whether you want it.
It only downloads the parts that actually changed, so most updates are small. If
you are offline it says nothing at all and just starts.

---

## 5 August 2026

**You can tell what is in front of you.** Anything behind you now sounds slightly
lower, and returns to normal when it is ahead of you again. That goes for people
and for the world around you, so you can tell what you have already walked past.

**The tracking beeper.** Press T, pick somewhere, and a beep pulses towards it
until you arrive. It goes quiet with a sound when you get there. It follows the
same rule as everything else, lower when it is behind you.

**The beeper knows when you have arrived.** Somewhere like the park bench is a
spot you walk up to rather than a single exact step, so the beeping now stops as
soon as you are close enough to actually use the thing, instead of carrying on
while you stand right next to it.

**Sleep.** Turning in now takes eight seconds and you snore through it. In your
own bed it is a contented snore. Dozing rough it is a broken, restless one.

**Benches tell you what they are for.** Every bench now says whether pressing
enter will sit you down for a rest or bed you down for the night, so the two
benches in the park are no longer a guessing game.

**Better sounds.** Being sick actually sounds like being sick now. Sitting on a
bench to let time pass ticks like a clock instead of whatever it was doing
before.
