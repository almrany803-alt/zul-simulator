# Zul Simulator

A comedic audio game for blind and visually impaired players, set on the streets
of a Polish town.

## Table of contents

- [What is this?](#what-is-this)
- [What you need](#what-you-need)
- [Downloading and installing](#downloading-and-installing)
- [Starting to play](#starting-to-play)
- [The controls](#the-controls)
- [Updating](#updating)
- [If your antivirus complains](#if-your-antivirus-complains)
- [Languages](#languages)
- [Saving](#saving)
- [Reporting bugs](#reporting-bugs)
- [Parental advisory](#parental-advisory)
- [Credits](#credits)

## What is this?

A *żul* (roughly, "zhool") is a Polish word for a street drinker. One of the men
you walk past on your way to work, sitting on a bench with a carrier bag of
empties, who has a whole life going on that you never see.

Zul Simulator is a game about being one of them for a while. You wake up on
ulica Wesoła, which translates as Cheerful Street and is not, and you get on with
your day. You collect bottles and cash them in at the deposit machine. You cadge
change off passers-by, some of whom are kind and some of whom are not. You buy
food you should eat and drink you should not. You keep an eye on the police, who
keep an eye on you. You try to get to a bed by nightfall, and if you cannot, you
find a bench.

There are people out there with lives of their own, in the same places at the
same times each day, who form opinions about you based on how you behave. There
is a bar, a church, a park, a station and a police station. There is a line you
can cross that the town will not forgive.

It is funny, it is fairly rude, and it is played entirely by ear. There is
nothing on the screen worth looking at.

You can play as one of four men, and it genuinely changes the game: how people
treat you, what you are good at, and what you do when you have had too much.

## What you need

A Windows PC and a screen reader. NVDA, JAWS and the built-in Windows voice all
work. Headphones are strongly recommended, because the game tells you where
things are by where the sound comes from, and that does not work through a laptop
speaker.

You do not need to install anything else. Everything the game needs comes in the
download.

## Downloading and installing

There is no installer. You unzip it and run it.

1. Go to the [latest release](../../releases/latest).
2. Under "Assets", download the file whose name ends in `_windows.zip`. It is
   about 43 MB. Ignore the one that says `DEV_source_snapshot`, that is for
   development and is not the game.
3. Unzip it somewhere you can write to. Your Documents folder is ideal. **Do not
   unzip it into Program Files**, because Windows protects that folder and the
   game will not be able to update itself later.
4. Open the folder that comes out and run **zul.exe**.

That is it. Nothing to install and nothing to configure.

## Starting to play

The first thing it asks is which language you want, English or Polish. After that
you pick a character, and it reads you a short piece about who he is before you
commit.

Then press **H** for how to play. It is written for someone who has never played
this before, and it covers a good deal more than this page does.

## The controls

The full list is under H in the game. The essentials:

- **Arrow keys** walk you around.
- **Enter** interacts with whatever you are standing at or beside.
- **T** picks somewhere to track, and the game beeps towards it until you arrive.
- **P** lists the people nearby.
- **C**, **R** and **H** read out your cash, your standing and your health.
- **Escape** backs out of anything.

Sounds behind you play slightly lower than sounds ahead of you, which is how you
tell what you have already walked past.

## Updating

The game looks after this itself. When you start it, it quietly checks whether
anything is new. If there is, it reads out what has changed and asks whether you
want it. Say yes and it downloads only the parts that actually changed, which is
usually a few megabytes rather than the whole thing.

If you are offline, it says nothing at all and simply starts.

You can also read [what's new](CHANGELOG.md) here at any time.

Because the game updates itself, it needs to live somewhere it can write to. That
is the reason for not putting it in Program Files.

## If your antivirus complains

It might, and it is a false alarm.

Antivirus software partly judges a program by how many people have run it before.
A newly built game that almost nobody has downloaded yet has no such history, so
it sometimes gets flagged purely for being new. This happens to plenty of small
games and to some large commercial ones too.

If Windows Defender blocks it, open Windows Security, go to Protection history,
find the item and choose to allow it. You can also add the game's folder to the
exclusion list.

If you would rather satisfy yourself first, upload the file to virustotal.com,
which checks it against about seventy scanners at once.

Please do not switch your antivirus off altogether. Allowing this one folder is
enough.

## Languages

The game is fully playable in English and Polish, and you choose when it starts.
The Polish is written by a Polish speaker, not run through a machine.

## Saving

The game saves automatically, and your saves live in your AppData folder rather
than the game folder. Updating the game, or even deleting it and unzipping a
fresh copy, will not lose your progress.

## Reporting bugs

Please open an issue on the [issues page](../../issues), or send them to whoever
gave you the game.

The more specific the better: what you were doing, what you expected, and what
happened instead. If something sounded wrong, say what it sounded like. The game
can also write a log file from the test menu, which is genuinely useful.

## Parental advisory

Zul Simulator is about drinking, poverty and the police, and the language is what
you would actually hear on that street. There is a great deal of swearing. It is
not suitable for children.

Nothing in it encourages drinking. If anything it is fairly clear-eyed about
where that road goes.

## Credits

Built with [NVGT](https://nvgt.gg), the Nonvisual Gaming Toolkit.

Polish translation and a great deal of steering by Longshoot. Testing by Kevin
and the lads, who find things nobody meant to leave in.
