# Contributing

Corrections make these subtitles better for everyone who watches the film. The most useful help:

1. **A better hearing of a doubtful passage.** Start with [transcript/review-needed.md](transcript/review-needed.md). Those are the identifications we are least sure of.
2. **A misidentified or mis-transcribed verse.** Tell us the timestamp, what you hear, and if possible the source.
3. **A verse we missed.** If something is recited in the film and no subtitle appears, tell us the timestamp.
4. **A better translation.** Clearer, more faithful, or shorter on screen.
5. **A fit for another release.** If you have made the subtitles fit a different copy of the film, say which copy and what `--anchor` or `--fps` values worked, and we'll add them to [docs/RESYNC.md](docs/RESYNC.md).

## The easy way: open an issue

You don't need to know git. An issue like this is perfect:

> At **0:41:12** the second line is *X*, not *Y*. The verse is Kaṭha Upaniṣad 1.2.18.

## The direct way: a pull request

1. Edit [transcript/transcript.txt](transcript/transcript.txt). Its format is in [docs/TRANSCRIPT_FORMAT.md](docs/TRANSCRIPT_FORMAT.md).
2. Run `python tools/build.py` and check it builds without errors.
3. Commit both the transcript and the regenerated files, and open a pull request explaining the change.

When you change a doubtful entry, update its type: `reconstructed` becomes `verse` or `sung` once the text is certain. Also update its `note:` to say how you established it.

## Scope

This repository covers the **classical texts** recited in the film, which are all in the public domain. Please don't contribute transcriptions or translations of the film's own dialogue. It belongs to the film's makers, and we won't publish it without their permission.

## Translation style

- Translate the Sanskrit in front of you, not the meaning someone else's subtitle gave it.
- Keep it plain, faithful and quick to read. A subtitle is on screen for a few seconds.
- Keep key terms where English has no real equivalent (Brahman, Ātman, dharma). In the English track, write them without diacritics.
