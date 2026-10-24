# How these subtitles were made

This document records how the subtitles were produced, what worked, what didn't, and where the results are weakest. It is meant both as an honest account for viewers and as a guide for anyone attempting the same thing for another Sanskrit film.

## 1. Scope

The film mixes three kinds of speech:

1. **Classical texts** recited or chanted: Vedic mantras, Upaniṣads, the Bhagavad-gītā, the Purāṇas, Kālidāsa, and hymns attributed to Śaṅkara and his disciples. These are in the public domain.
2. **The film's own dialogue**, written for the film in Sanskrit, with short passages in Malayalam, Hindi and Kannada or Tulu.
3. **Songs and verses whose source we could not identify.**

This repository transcribes and translates only the first. The dialogue belongs to the film's makers, so we have not published it. When a character *quotes* a classical text in conversation, only the quotation is given. Unidentified recitations are listed by timestamp in [UNIDENTIFIED.md](UNIDENTIFIED.md), without their text.

We did not copy the English subtitles already in circulation. They were consulted only to cross-check meaning and timing, and every translation here was made fresh from the Sanskrit.

## 2. The source video

All timings refer to a release running **2:39:54.58 at 25 fps** (1920×1080, H.264, AAC stereo). One older English subtitle file in circulation is timed for this release. Another runs progressively faster, by a factor of almost exactly 23.976/25, so it was made for a release with a different frame rate. A third fits a shorter cut of about 1 h 24 m. See [RESYNC.md](RESYNC.md) for fitting our subtitles to other releases.

## 3. Speech recognition

The soundtrack was extracted to 16 kHz mono WAV and transcribed with **OpenAI Whisper large-v3**, run through [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 1.2.1 on a single NVIDIA RTX 3090. We used beam size 5, word-level timestamps, and `condition_on_previous_text` turned off to limit runaway repetition. It took three passes:

| Pass | Settings | Result | Why |
|---|---|---|---|
| 1 | Language forced to Sanskrit; Silero voice-activity filter on | 377 segments, about 19 min | The main transcription |
| 2 | Language detected per segment | 275 segments, about 24 min | To catch any speech not in Sanskrit |
| 3 | Only the gaps between pass-1 segments; voice filter **off**; hallucination guard on | 258 segments from 129 gaps (74 min of audio), about 23 min | See below |

**The voice filter drops chanting.** This was the most important lesson. Silero's voice-activity detector treats singing and chanting over music as non-speech, so pass 1 silently skipped much of what we cared about most. Examples include the Gāyatrī under the opening credits, the Ṛgveda hymns at dawn, the Buddhist refuge chant, and the *madhu vātā* hymn. Pass 3 recovered them by re-transcribing only the skipped stretches with the filter off.

**Whisper on Sanskrit is evidence, not text.** Its raw output is often wrong in systematic ways:
- **It writes Sanskrit as if it were Hindi.** For example, *हम* for *वयम्* ("we").
- **It garbles sandhi and drops aspirates and retroflexes.**
- **It hallucinates during music.** It produced phrases like "Thank you for watching", an invented caption "TEN YEARS LATER", and loops that repeat one syllable dozens of times.
- **The language-detection pass doesn't give a language per segment** in this version, and it switched to Telugu, Kannada or Tamil script on Sanskrit audio. Its main use was confirming that the film has no English speech.

Raw recognition output is not published, because it includes the film's dialogue.

## 4. Identifying the recitations

Each stretch of recognised text was read alongside its word timings and the older subtitles, and treated as a puzzle: *which known text would produce these sounds here?* Surviving syllables, metre, context and grammar together are usually enough.

- **From noise to the Gītā.** Recognition produced *पूर्चम्यादालापदप्राणम्… आतितो योदधादनाम्* at 0:06:54. That is *mūrdhnyādhāyātmanaḥ prāṇam āsthito yoga-dhāraṇām*, Bhagavad-gītā 8.12, the verse on the dying yogi who holds his breath at the crown of the head. It is heard just as Śivaguru prepares to leave his body.
- **Grammar overruling the ear.** In the Five Fires (Chāndogya Upaniṣad 5.6.1), recognition heard *puruṣo vāva*, "man is a fire". But the next word is the feminine *tasyāḥ*, which only fits *pṛthivī vāva*, "the earth is a fire", and that is what the Upaniṣad says.
- **Metre as a check.** In the Annapūrṇā Stotram, every reconstructed line was scanned against the śārdūlavikrīḍita metre: 19 syllables, with a break after the twelfth. A reading that doesn't scan is wrong.
- **Following the audio over the edition.** Where the film clearly uses a different reading from the standard text, we keep the film's reading and say so in a note. For example, the film sings *ākāśāt patitaṃ toyaṃ sāgaraṃ pratigacchati*, and its Mitra chant has *śravo… satyam*.

Once a text was identified, its canonical wording was written out in Devanagari, without Vedic accents, and the source was recorded. Where we were unsure of a source or a verse number, we checked it against online editions such as [GRETIL](https://gretil.sub.uni-goettingen.de/), [sanskritdocuments.org](https://sanskritdocuments.org/) and others. If it could not be confirmed, the entry's note says so.

## 4a. Re-checking the doubtful passages

There is no published script of the film to check against. So the passages we were least sure of went through one more test. We extracted them from the original stereo track, ran them through ffmpeg's `dialoguenhance` filter (which pulls a centred voice forward from the music), denoised and band-limited them, and transcribed them again.

This settled several questions, and overturned two of our earlier readings:

| Time | Before | After |
|---|---|---|
| 0:06:19 | guessed as Ṛgveda 1.90.7–8 | actually the Medhā Sūkta (*mayi medhāṃ mayi prajām…*) and the Agni prayer *yat te agne tejas…* |
| 0:06:58 | guessed as Gītā 8.13 | actually 8.14 and 8.15 |
| 0:09:37 | missed | the second half of the Vedasāra verse |
| 0:10:06 | Īśa 17, placement uncertain | confirmed and placed |
| 1:07:27 | Chāndogya 4.4.2, reconstructed | *yadgotras tvam asi* audible; confirmed |
| 2:32:30 | Taittirīya 3.10.5, one phrase | *annamaya, prāṇamaya, manomaya* clearly chanted in sequence |

We also tried giving Whisper our candidate text as a prompt, to see whether it would "agree". It did, even for the two readings that turned out to be wrong. It simply repeats the prompt, so a prompted run proves nothing, and we rely only on the unprompted enhanced pass.

## 5. Translation

- **From the Sanskrit itself,** not from any earlier subtitle.
- **Plain, faithful English** that can be read in the few seconds a subtitle is on screen: at most two lines, ideally under about 50 characters each.
- **Verse by verse:** each subtitle normally carries one half-verse, so the translation runs in step with the chanting.
- **Key terms are kept** where English has no true equivalent (Brahman, the Self, dharma, guṇa), without diacritics in the English track.

The translations are ours, and they are interpretations. Corrections are welcome.

## 6. Transliteration

The IAST track is **generated automatically from the Devanagari** with [indic_transliteration](https://github.com/indic-transliteration/indic_transliteration_py), so the two scripts can never disagree. Dandas are set apart from the word (*svaḥ |*), the candrabindu is written as a tilde over the vowel (*madhumā̃*), and in non-verse quotations a danda becomes a full stop.

## 7. Timing

- Start and end times come from Whisper's **word-level timestamps**. Long segments are split at the half-verse.
- Chanted passages are sometimes held on screen for 20 to 30 seconds, because the chant itself is that slow.
- Where a verse clearly begins before the first audible word, the note says so.
- The build guarantees that no two subtitles overlap.
- Placement was spot-checked by extracting video frames at cue times and by watching a hard-subtitled preview.

## 8. Confidence marks

Every entry is marked `verse`, `sung` or `reconstructed` (see the [README](../README.md#how-accurate-is-it)). Everything marked `reconstructed` is listed in [review-needed.md](../transcript/review-needed.md), with the reason.

## 9. Mistakes we made along the way

We record these because they are instructive.

- **An early timing check went wrong because of our own arithmetic.** We fed the video tool 876 seconds when we meant 1:14:36 (4476 s), and briefly concluded the older subtitles were badly out of sync. They weren't.
- **A first draft of the Kashi scene gave a guessed reconstruction** of the lines Śaṅkara speaks after the Chandāla scene. A later, clearer recognition pass showed they are a real verse, from the **Kāśī Pañcakam** (*kāśyāṃ hi kāśate kāśī…*), and the canonical text replaced our guess.
- **We first labelled the variant Mitra chant "the Yajurveda reading"** before we had confirmed it. It is now described as a variant reading until its source is confirmed.
- **Two reconstructions from fragments were wrong:** the "Ṛgveda 1.90.7–8" at 0:06:19 and the "Gītā 8.13" at 0:07:01. Both looked plausible from context. Cleaner audio showed otherwise (section 4a). This is why everything reconstructed is marked, and why we'd like people to check.

## 10. Known limitations

- Chant timings are approximate, especially where several verses run together.
- A few verses probably begin before the point where we start them, because their opening is drowned by music.
- Some texts were identified from fragments; they are marked `reconstructed`.
- We may have missed recitations entirely where the music is loud.
- The film's dialogue, which is most of its spoken words, is not included.

## 11. Reproducing this work

`tools/build.py` regenerates every file from the transcript. To regenerate the raw recognition for your own copy of the film, you need Python with `faster-whisper` and a CUDA GPU. The settings are in section 3, and the scripts we used are in `tools/asr/`.
