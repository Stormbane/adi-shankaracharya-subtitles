# Adi Shankaracharya (1983): the recited Sanskrit texts, subtitled

Subtitles for the classical texts recited and chanted in **G. V. Iyer's *Adi Shankaracharya* (1983)**, the first feature film made in Sanskrit. Each text is given exactly, in **IAST transliteration** and **Devanagari**, with a new **English translation**, timed to the film.

The film is woven through with classical texts: Vedic hymns and mantras, the Upaniṣads, the Bhagavad-gītā, and hymns traditionally attributed to Śaṅkara himself. Automatic captioning tools mishear chanted Sanskrit badly, and the English subtitles in circulation paraphrase these passages or skip them. This project identifies each recitation, sets down its canonical text, and translates it line by line.

> **What is not here: the film's own dialogue.** The conversations between characters were written for the film and belong to its makers, so they are not transcribed in this repository. We hope to add them with the rights holders' permission. Until then, `tools/build.py --merge` can combine these subtitles with any English dialogue subtitles you already have, for your own viewing. See [Watching with the dialogue too](#watching-with-the-dialogue-too).

## What's in it

**186 subtitles covering about 70 classical texts**, from the Gāyatrī under the opening credits to the *pūrṇam adaḥ* peace chant that closes the film. Among them:

- **Hymns attributed to Śaṅkara:** Bhaja Govindam (with the old grammarian at Kashi), the Annapūrṇā Stotram, the Kanakadhārā Stotram (the gooseberry episode), Nirvāṇa Ṣaṭkam, Manīṣā Pañcakam (the Chandāla at Kashi), Kāśī Pañcakam, Saundarya Laharī, and the Prapañcasāra's verse to Śāradā
- **Hymns by his disciples:** Toṭaka's Toṭakāṣṭakam and Hastāmalaka's verse on the Self
- **The Upaniṣads:** a Kūḍiyāṭṭam performance of the Kaṭha Upaniṣad (Naciketas and Death), the story of Satyakāma Jābāla and the doctrine of the Five Fires from the Chāndogya, the two birds of the Muṇḍaka, the Bṛhadāraṇyaka, Īśa and Taittirīya
- **The Bhagavad-gītā:** a dozen verses, including the vision of the cosmic form and the last verses chanted on the ascent into the Himalayas
- **Vedic mantras:** the Gāyatrī, hymns to Mitra, the *madhu vātā* hymn, the Mantrapuṣpam, and a mantra to Agni
- **Others:** Śaṅkara's own commentary on the Brahma Sūtras, Kālidāsa's Raghuvaṃśa, the Bhāgavata Purāṇa, the Mahābhārata, the Avadhūta Gītā, the Buddhist Three Refuges and the Jain Navkār Mantra

A few recitations could not be identified and are listed in [docs/UNIDENTIFIED.md](docs/UNIDENTIFIED.md). If you recognise one, please tell us.

## Downloads

| File | What you see on screen | Good for |
|---|---|---|
| [`subtitles/combined/Adi.Shankaracharya.1983.sa-Latn+en.srt`](subtitles/combined/) | IAST transliteration above English | **Most viewers.** Hear the Sanskrit, follow its sound, understand it. |
| [`subtitles/combined/Adi.Shankaracharya.1983.sa-Deva+en.srt`](subtitles/combined/) | Devanagari above English | Readers of Devanagari |
| [`subtitles/Adi.Shankaracharya.1983.en.srt`](subtitles/) | English only | Just the meaning |
| [`subtitles/Adi.Shankaracharya.1983.sa-Latn.srt`](subtitles/) | IAST only | Following the Sanskrit closely |
| [`subtitles/Adi.Shankaracharya.1983.sa-Deva.srt`](subtitles/) | Devanagari only | Sanskrit readers |

The combined tracks also come as styled `.ass` files (the Sanskrit line in a softer colour) for players that support them, such as VLC and mpv. Any player can show the `.srt` versions.

## Watching with the dialogue too

These tracks appear only while a classical text is being recited. To follow the conversations as well, you have two options:

- **Merge with your own dialogue subtitles (recommended).** If you have an English subtitle file that fits your copy, run
  ```bash
  python tools/build.py --merge "path/to/your-english.srt"
  ```
  This writes merged files to `merged/`: your dialogue lines plus our verse cues. Wherever a verse is recited, our exact text replaces the line that paraphrased it.
- **Show two tracks at once in mpv.**
  ```bash
  mpv movie.mp4 --sub-files="dialogue.srt;Adi.Shankaracharya.1983.sa-Latn+en.srt" --sid=1 --secondary-sid=2
  ```
  On Linux and macOS, separate the two files with `:` instead of `;`.

## Which version of the film these fit

The timings match the **2 h 39 m 54 s, 25 fps** release (1080p, the full-length cut).

**Quick check:** just after the Kashi scene with the Chandāla, Śaṅkara's refrain *"caṇḍālo'stu sa tu dvijo'stu…"* should appear at **1:19:26**.

If your copy is a different length or the subtitles drift, see **[docs/RESYNC.md](docs/RESYNC.md)**. It covers frame-rate differences, offsets, and the shorter cuts in circulation.

## Using the files

- **VLC:** *Subtitle → Add Subtitle File…*, or rename the file to match your video (`MyCopy.en.srt` next to `MyCopy.mp4`) and it loads automatically.
- **Jellyfin, Plex, Kodi:** put the files next to the movie, named after it with a language code before `.srt`, for example `Adi Shankaracharya (1983).sa.srt`.
- **Devanagari** needs a font with Devanagari glyphs. Windows has one built in (Nirmala UI). Elsewhere, install *Noto Sans Devanagari*.

## How accurate is it?

Every entry in the master transcript carries a mark saying how it was established:

| Mark | Meaning |
|---|---|
| `verse` | Recited clearly; identified and written out from its canonical text |
| `sung` | Chanted or sung over music; the text is identified, the timing follows the chant |
| `reconstructed` | Only fragments are audible; identified from those fragments and the context |

**[transcript/verses.md](transcript/verses.md)** lists every text with its timestamp and source. **[transcript/review-needed.md](transcript/review-needed.md)** lists the identifications we are least sure of, and why. If you can hear a passage better than we could, a correction is very welcome.

## How it was made

The soundtrack was run through the Whisper speech-recognition model three times. On its own, Whisper gets chanted Sanskrit badly wrong. Its output was used as evidence rather than as text: each recitation was identified from the syllables that survive, the canonical text was written out, and the English was translated fresh from that text. The work was AI-assisted (Whisper for recognition, Claude for identification and translation) and reviewed by a human.

The full method, including what went wrong along the way, is in **[docs/METHODOLOGY.md](docs/METHODOLOGY.md)**.

## The master transcript

Every subtitle file is generated from one source, **[transcript/transcript.txt](transcript/transcript.txt)**. It holds each recited text with its timestamps, Devanagari, English, source and confidence mark. Machine-readable copies are in `transcript/transcript.json` and `transcript/transcript.tsv`.

```bash
pip install -r requirements.txt
python tools/build.py                       # rebuild everything after a correction
python tools/build.py --fps 25:23.976       # make a set for a copy that runs at 23.976 fps
python tools/build.py --anchor 00:18:37.4=00:18:31.0 --anchor 01:19:26.4=01:17:02.7
                                            # fit to your copy using two matching moments
```

The file format is described in [docs/TRANSCRIPT_FORMAT.md](docs/TRANSCRIPT_FORMAT.md).

## Contributing

Spotted a misidentified verse, a wrong word, or a clumsy translation? See **[CONTRIBUTING.md](CONTRIBUTING.md)**. Corrections from Sanskrit readers are especially valuable. Even an issue that just says *"at 0:41:12 the verse is X, not Y"* helps.

## License and copyright

- Our transcription choices, translations and notes are released under **[CC BY-SA 4.0](LICENSE-CONTENT)**. The classical texts themselves are in the public domain.
- The code in `tools/` is under the **[MIT License](LICENSE)**.
- The film *Adi Shankaracharya* (1983) is the work of its makers and of the National Film Development Corporation of India, which produced it. This is an independent, non-commercial project and is not affiliated with them. If you hold rights in the film and have concerns, please open an issue.

## Credits

- Identification, transcription and translation: **Stormbane**, working with Claude (Anthropic)
- Speech recognition: OpenAI Whisper large-v3, through [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- Transliteration: [indic_transliteration](https://github.com/indic-transliteration/indic_transliteration_py)
- The scholars and volunteers behind the online editions of these texts, especially [GRETIL](https://gretil.sub.uni-goettingen.de/) and [sanskritdocuments.org](https://sanskritdocuments.org/)
