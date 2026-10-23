# Fitting the subtitles to your copy of the film

These subtitles are timed to the **2 h 39 m 54 s, 25 fps** release. Other copies circulate, so here is how to make a set that fits yours. Everything below uses `tools/build.py`. The retimed files go to `retimed/`, and the originals are left alone.

## 1. Work out what kind of mismatch you have

Play a few minutes near the start and near the end, and compare against the timestamps in [transcript/verses.md](../transcript/verses.md).

| What you see | What it means | Fix |
|---|---|---|
| Everything is early or late by the same amount | A constant offset | [Step 2](#2-constant-offset) |
| Fine at the start, gets worse and worse | A different frame rate | [Step 3](#3-different-frame-rate) |
| Fine in places, badly wrong in others | A different cut, with scenes removed | [Step 4](#4-a-different-cut) |

## 2. Constant offset

If a verse appears 3.2 seconds before you hear it, shift everything 3.2 seconds later:

```bash
python tools/build.py --offset 3.2
```

Use a negative number to shift earlier.

## 3. Different frame rate

The most common cause of drift is a copy made at 23.976 frames per second instead of 25. The whole film then runs about 4% slower or faster.

| Your copy's running time | Command |
|---|---|
| about **2 h 46 m** (slower) | `python tools/build.py --fps 25:23.976` |
| about **2 h 33 m** (faster) | `python tools/build.py --fps 23.976:25` |

If that isn't quite right, use two anchors instead (next section). They fit any combination of offset and speed exactly.

## Two anchors: the general fix

Pick two easily recognised moments, one early in the film and one late. Note the time each happens in **your** copy, and give the pairs as `our time=your time`:

```bash
python tools/build.py --anchor 00:18:37.4=00:18:31.0 --anchor 01:19:26.4=01:17:02.7
```

The tool works out the exact offset and speed from the two pairs. Good landmarks:

| Our time | What happens |
|---|---|
| 00:00:53.9 | The Gāyatrī mantra begins over the opening credits |
| 00:18:37.4 | *"dvā suparṇā sayujā sakhāyā"*: the verse of the two birds begins |
| 01:18:45.5 | Śaṅkara begins *"brahmaivāham idaṃ jagacca"* in reply to the Chandāla |
| 01:19:26.4 | The refrain *"caṇḍālo'stu sa tu dvijo'stu"* |

Anchors far apart give the most accurate fit.

## 4. A different cut

Some copies have scenes removed. One in circulation runs about 1 h 24 m. A single linear fit can't fix that, because the gap opens up at each cut. Two options:

- **Retime section by section.** Use two anchors inside the part you are watching, build, and repeat for the next section. This is tedious, but exact.
- **Use [alass](https://github.com/kaegi/alass),** which is designed for subtitles split by cuts. It works best on a dense subtitle file, so first merge these verse cues with a dialogue subtitle that already fits your copy (see the README), then run alass on the merged file.

[ffsubsync](https://github.com/smacke/ffsubsync) is also excellent for offset and speed problems on full dialogue subtitles. Our verse-only tracks are too sparse, and too full of chanting over music, for it to lock on reliably by themselves.
