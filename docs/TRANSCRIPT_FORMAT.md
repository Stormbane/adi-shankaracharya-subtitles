# The master transcript format

`transcript/transcript.txt` is a plain UTF-8 text file. You can edit it in any text editor and read changes to it easily in a diff. Every subtitle file is generated from it.

## An entry

```
@ 00:18:37.400 --> 00:18:55.500  [verse]  {Shankara}
src: Mundaka Upanishad 3.1.1 (also Rigveda 1.164.20)
note: anything a future editor should know
sa: द्वा सुपर्णा सयुजा सखाया
sa: समानं वृक्षं परिषस्वजाते।
en: Two birds, close companions,
en: cling to the same tree.
```

| Line | Required | Meaning |
|---|---|---|
| `@ START --> END` | yes | When the subtitle shows. Times are `HH:MM:SS.mmm`, timed to the 2:39:54, 25 fps release. |
| `[type]` | no, defaults to `heard` | How the text was established: `verse`, `sung`, `reconstructed`, `heard`, `unclear` |
| `{speaker}` | no | Who recites it, if known |
| `src:` | for verses | The canonical source. This fills [verses.md](../transcript/verses.md). |
| `note:` | no | Doubts, reasoning, anything for the next editor. `reconstructed` and `unclear` entries should always have one. |
| `sa:` | yes | Sanskrit in Devanagari. Each `sa:` line becomes one line on screen. |
| `iast:` | rarely | Only when the automatic IAST needs overriding. Normally IAST is generated from `sa:`. |
| `en:` | yes | English. Each `en:` line becomes one line on screen. |

Lines starting with `#` are comments. Blank lines are ignored. Entries can appear in any order, since the build sorts them by time, but please keep the file in time order for the next reader.

## Conventions

- **Line length.** Keep English lines under about 50 characters and use at most two. The build warns about long lines.
- **Verse layout.** Give one half-verse (two pādas) per entry where the timing allows, so a verse reads line by line in step with the chanting.
- **Punctuation.** End a half-verse with `।` and a full verse with `॥`. In IAST these become `|` and `||`.
- **Sandhi.** Write the text as the edition gives it. Don't split words apart purely for readability.
- **Accents.** Vedic accent marks are omitted.
- **Other languages.** Text recited in Pāli (for example the Buddhist refuges) stays in Pāli, not Sanskritised.

## Building

```bash
python tools/build.py
```

This regenerates everything in `subtitles/`, plus `transcript/transcript.json`, `transcript.tsv`, `verses.md` and `review-needed.md`. If the transcript has a formatting error, the build stops and names the line.
