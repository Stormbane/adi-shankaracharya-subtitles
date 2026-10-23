#!/usr/bin/env python3
"""Run the three speech-recognition passes described in docs/METHODOLOGY.md.

Needs a CUDA GPU and:  pip install faster-whisper
Extract the soundtrack first, e.g.:
    ffmpeg -i movie.mp4 -vn -ac 1 -ar 16000 full.wav

    python tools/asr/transcribe.py full.wav --out asr/

Writes asr_sa.json, asr_multi.json and asr_gaps.json (plus readable .txt copies).
The output contains the film's dialogue as well as its recitations, so keep it
for your own use; don't publish it.
"""
import argparse
import inspect
import io
import json
import time
from pathlib import Path

from faster_whisper import WhisperModel

COMMON = dict(task="transcribe", beam_size=5, word_timestamps=True, condition_on_previous_text=False)


def hms(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def save(out, tag, segments, info=None):
    rows = []
    with io.open(out / f"asr_{tag}.txt", "w", encoding="utf-8") as txt:
        for s in segments:
            rows.append(dict(start=round(s.start, 3), end=round(s.end, 3), text=s.text.strip(),
                             avg_logprob=round(s.avg_logprob, 3), no_speech=round(s.no_speech_prob, 3),
                             comp=round(s.compression_ratio, 2),
                             words=[dict(w=w.word, s=round(w.start, 3), e=round(w.end, 3), p=round(w.probability, 2))
                                    for w in (s.words or [])]))
            txt.write(f"{hms(s.start)} --> {hms(s.end)}  [lp={s.avg_logprob:.2f}]  {s.text.strip()}\n")
    meta = dict(lang=info.language, p=info.language_probability, dur=info.duration) if info else {}
    (out / f"asr_{tag}.json").write_text(json.dumps(dict(info=meta, segments=rows), ensure_ascii=False, indent=1),
                                         encoding="utf-8")
    print(f"[{tag}] {len(rows)} segments")
    return rows, meta


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("wav", help="16 kHz mono WAV of the soundtrack")
    ap.add_argument("--out", default="asr", help="output directory")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--compute-type", default="float16")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    t = time.time()
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)
    print(f"model loaded in {time.time() - t:.0f}s")

    # Pass 1: Sanskrit, with the voice-activity filter.
    segs, info = model.transcribe(args.wav, language="sa", vad_filter=True,
                                  vad_parameters=dict(min_silence_duration_ms=500), **COMMON)
    rows, meta = save(out, "sa", segs, info)

    # Pass 2: per-segment language detection, to catch non-Sanskrit speech.
    if "multilingual" in inspect.signature(model.transcribe).parameters:
        segs, info = model.transcribe(args.wav, multilingual=True, vad_filter=True,
                                      vad_parameters=dict(min_silence_duration_ms=500), **COMMON)
        save(out, "multi", segs, info)

    # Pass 3: the gaps pass 1 skipped, with the filter OFF. The voice filter
    # treats chanting over music as non-speech, so this is where most verses are recovered.
    edges = [0.0] + [x for r in rows for x in (r["start"], r["end"])] + [meta["dur"]]
    clips = []
    for a, b in zip(edges[0::2], edges[1::2]):
        if b - a >= 4.0:
            clips += [max(0.0, a - 0.5), min(meta["dur"], b + 0.5)]
    segs, _ = model.transcribe(args.wav, language="sa", vad_filter=False, clip_timestamps=clips,
                               hallucination_silence_threshold=2.0, **COMMON)
    save(out, "gaps", segs)


if __name__ == "__main__":
    main()
