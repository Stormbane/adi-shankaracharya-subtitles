#!/usr/bin/env python3
"""Build every subtitle track from the master transcript.

The master transcript (transcript/transcript.txt) is the single source of truth.
This script turns it into:

  subtitles/Adi.Shankaracharya.1983.en.srt         English
  subtitles/Adi.Shankaracharya.1983.sa-Latn.srt    Sanskrit, IAST transliteration
  subtitles/Adi.Shankaracharya.1983.sa-Deva.srt    Sanskrit, Devanagari
  subtitles/combined/*.srt and *.ass                IAST + English, Devanagari + English
  transcript/transcript.json, transcript.tsv        machine-readable exports

The IAST is generated from the Devanagari, so the two scripts can never disagree.

Retiming for a different release of the film (output goes to retimed/):

  python tools/build.py --offset 2.5               # everything 2.5 s later
  python tools/build.py --fps 25:23.976            # release runs at 23.976 fps instead of 25
  python tools/build.py --anchor 00:01:22.16=00:01:19.90 --anchor 02:30:05=02:24:12
                                                   # two matching moments -> exact linear fit

See docs/RESYNC.md for how to find those numbers.
"""
import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

try:
    from indic_transliteration import sanscript
except ImportError:
    sys.exit("Missing dependency. Run:  pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "transcript" / "transcript.txt"
REPO_URL = "https://github.com/Stormbane/adi-shankaracharya-subtitles"
BASENAME = "Adi.Shankaracharya.1983"
TAGS = {"verse", "heard", "reconstructed", "unclear", "english", "sung"}
MIN_GAP = 0.04      # seconds kept between consecutive cues
EN_LINE_WARN = 50   # characters

HEADER = re.compile(
    r"^@\s*(?P<start>\S+)\s*-->\s*(?P<end>\S+)"
    r"(?:\s*\[(?P<tag>[\w-]+)\])?"
    r"(?:\s*\{(?P<speaker>[^}]*)\})?\s*$")


@dataclass
class Cue:
    start: float
    end: float
    tag: str
    speaker: str
    line: int
    sa: list = field(default_factory=list)
    iast: list = field(default_factory=list)
    en: list = field(default_factory=list)
    src: str = ""
    note: str = ""
    section: str = ""


def parse_time(text):
    """Accepts HH:MM:SS.mmm, HH:MM:SS,mmm, MM:SS or plain seconds."""
    secs = 0.0
    for part in text.replace(",", ".").split(":"):
        secs = secs * 60 + float(part)
    return secs


def fmt_srt(t):
    ms = max(0, round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def fmt_ass(t):
    cs = max(0, round(t * 100))
    h, cs = divmod(cs, 360_000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def fmt_plain(t):
    return fmt_srt(t).replace(",", ".")


def parse(path):
    cues, cur, errors = [], None, []
    section, after_rule = "", False
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if line.startswith("#"):
            # A comment line sandwiched under a "# -----" rule names the scene.
            text = line.lstrip("#").strip()
            is_rule = bool(text) and set(text) <= {"-"}
            if after_rule and text and not is_rule:
                section = text
            after_rule = is_rule
            continue
        if not line:
            continue
        if line.startswith("@"):
            m = HEADER.match(line)
            if not m:
                errors.append(f"line {n}: bad cue header: {raw}")
                cur = None
                continue
            tag = (m["tag"] or "heard").lower()
            if tag not in TAGS:
                errors.append(f"line {n}: unknown tag [{tag}] (use one of {sorted(TAGS)})")
            cur = Cue(parse_time(m["start"]), parse_time(m["end"]), tag,
                      (m["speaker"] or "").strip(), n, section=section)
            if cur.end <= cur.start:
                errors.append(f"line {n}: cue ends before it starts")
            cues.append(cur)
            continue
        key, sep, value = line.partition(":")
        key = key.strip().lower()
        if not sep or key not in {"sa", "iast", "en", "src", "note"}:
            errors.append(f"line {n}: expected 'sa:', 'iast:', 'en:', 'src:' or 'note:' -> {raw}")
            continue
        if cur is None:
            errors.append(f"line {n}: text before any '@' cue header")
            continue
        value = value.strip()
        if key in ("src", "note"):
            setattr(cur, key, (getattr(cur, key) + " " + value).strip())
        else:
            getattr(cur, key).append(value)
    if errors:
        sys.exit("Transcript errors:\n  " + "\n  ".join(errors))
    return sorted(cues, key=lambda c: c.start)


def to_iast(cue):
    """IAST lines for a cue: explicit 'iast:' lines win, otherwise transliterate the Devanagari."""
    if cue.iast:
        return cue.iast
    out = []
    for line in cue.sa:
        t = sanscript.transliterate(line, sanscript.DEVANAGARI, sanscript.IAST)
        t = t.replace("~", "̃")                    # candrabindu: madhumā~ -> madhumā̃
        t = re.sub(r"\s*(\|\|?)", r" \1", t).strip()    # set dandas apart: svaḥ| -> svaḥ |
        if not cue.src and cue.tag not in ("verse", "sung"):
            # In prose, a danda is just a full stop.
            t = t.replace("||", ".").replace("|", ".")
        out.append(t)
    return out


def retime(cues, scale, offset):
    for c in cues:
        c.start = c.start * scale + offset
        c.end = c.end * scale + offset
    # Never let one cue run into the next.
    for a, b in zip(cues, cues[1:]):
        if a.end > b.start - MIN_GAP:
            a.end = max(a.start + 0.3, b.start - MIN_GAP)


def write_srt(path, entries):
    blocks = [f"{i}\n{fmt_srt(s)} --> {fmt_srt(e)}\n{text}\n"
              for i, (s, e, text) in enumerate(entries, 1)]
    path.write_text("\n".join(blocks), encoding="utf-8")


ASS_HEADER = """[Script Info]
Title: {title}
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: English,Noto Sans,58,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2.6,1,2,120,120,48,1
Style: Sanskrit,{sa_font},50,&H00B4E6FF,&H00B4E6FF,&H00000000,&H64000000,0,{sa_italic},0,0,100,100,0,0,1,2.4,1,2,120,120,48,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def write_ass(path, title, entries, sa_font, sa_italic):
    lines = [ASS_HEADER.format(title=title, sa_font=sa_font, sa_italic=-1 if sa_italic else 0)]
    for s, e, top, bottom in entries:
        parts = []
        if top:
            parts.append("{\\rSanskrit}" + "\\N".join(top))
        if bottom:
            parts.append("{\\rEnglish}" + "\\N".join(bottom))
        text = "\\N".join(parts)
        lines.append(f"Dialogue: 0,{fmt_ass(s)},{fmt_ass(e)},English,,0,0,0,,{text}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(cues, out):
    sub = out / "subtitles"
    comb = sub / "combined"
    comb.mkdir(parents=True, exist_ok=True)

    en, latn, deva, latn_en, deva_en, ass_latn, ass_deva = [], [], [], [], [], [], []
    for c in cues:
        iast = to_iast(c)
        if c.en:
            en.append((c.start, c.end, "\n".join(c.en)))
        if iast:
            latn.append((c.start, c.end, "\n".join(iast)))
        if c.sa:
            deva.append((c.start, c.end, "\n".join(c.sa)))
        if iast or c.en:
            latn_en.append((c.start, c.end, "\n".join([f"<i>{x}</i>" for x in iast] + c.en)))
            ass_latn.append((c.start, c.end, iast, c.en))
        if c.sa or c.en:
            deva_en.append((c.start, c.end, "\n".join(c.sa + c.en)))
            ass_deva.append((c.start, c.end, c.sa, c.en))

    write_srt(sub / f"{BASENAME}.en.srt", en)
    write_srt(sub / f"{BASENAME}.sa-Latn.srt", latn)
    write_srt(sub / f"{BASENAME}.sa-Deva.srt", deva)
    write_srt(comb / f"{BASENAME}.sa-Latn+en.srt", latn_en)
    write_srt(comb / f"{BASENAME}.sa-Deva+en.srt", deva_en)
    write_ass(comb / f"{BASENAME}.sa-Latn+en.ass", "Adi Shankaracharya (1983) - IAST + English",
              ass_latn, "Noto Sans", True)
    write_ass(comb / f"{BASENAME}.sa-Deva+en.ass", "Adi Shankaracharya (1983) - Devanagari + English",
              ass_deva, "Noto Sans Devanagari", False)
    return {"en": len(en), "sa-Latn": len(latn), "sa-Deva": len(deva)}


def export(cues, out):
    """Machine-readable copies of the transcript, for anyone building their own tools."""
    tdir = out / "transcript"
    tdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, c in enumerate(cues, 1):
        rows.append({
            "id": i, "start": fmt_plain(c.start), "end": fmt_plain(c.end),
            "start_seconds": round(c.start, 3), "end_seconds": round(c.end, 3),
            "type": c.tag, "speaker": c.speaker, "source": c.src,
            "devanagari": c.sa, "iast": to_iast(c), "english": c.en, "note": c.note})
    (tdir / "transcript.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    cols = ["id", "start", "end", "type", "speaker", "source", "devanagari", "iast", "english", "note"]
    tsv = ["\t".join(cols)]
    for r in rows:
        tsv.append("\t".join(" / ".join(r[k]) if isinstance(r[k], list) else str(r[k]) for k in cols))
    (tdir / "transcript.tsv").write_text("\n".join(tsv) + "\n", encoding="utf-8")


def tshort(t):
    s = fmt_plain(t)[:8]
    return s[1:] if s.startswith("0") else s


def cell(text):
    """Make text safe inside a markdown table cell (IAST dandas are pipes)."""
    return text.replace("|", "\\|").replace("\n", " ")


def doubts(c):
    """Why an entry deserves a second look: any of 'text', 'source', 'timing'."""
    out, note = [], c.note.lower()
    if c.tag in ("reconstructed", "unclear"):
        out.append("text")
    if re.search(r"to be confirmed|not (yet )?(been able to )?confirm", note):
        out.append("source")
    if any(w in note for w in ("approximate", "start time", "begin")):
        out.append("timing")
    return out


def status(found):
    return "solid" if not found else "**check " + " and ".join(dict.fromkeys(found)) + "**"


def flag_url(c):
    """A pre-filled 'Correction' issue for this cue (see .github/ISSUE_TEMPLATE)."""
    t = tshort(c.start)
    ours = "\n".join(c.sa + [""] + to_iast(c) + [""] + c.en)
    title = f"Check {t}: {c.src or c.section}"
    return (f"{REPO_URL}/issues/new?template=correction.yml"
            f"&title={quote(title)}&time={quote(t)}&ours={quote(ours)}")


def base_src(src):
    s = re.sub(r"\s*\((continued|quoted|repeated|refrain|the refrain|phrases|condensed in the film)[^)]*\)", "", src)
    s = re.sub(r",\s*((first|second) half|(last|opening|closing) (line|words|verse)|line \d+).*$", "", s)
    return s.strip()


def passages(cues):
    """Consecutive cues of the same text in the same scene, grouped."""
    out = []
    for c in cues:
        key = (c.section, base_src(c.src))
        if out and out[-1][0] == key:
            out[-1][1].append(c)
        else:
            out.append((key, [c]))
    return out


def inject(path, name, content):
    """Replace the generated block between <!-- BEGIN name --> and <!-- END name -->."""
    text = path.read_text(encoding="utf-8")
    pat = re.compile(rf"(<!-- BEGIN {name} -->\n).*?(<!-- END {name} -->)", re.S)
    if pat.search(text):
        path.write_text(pat.sub(lambda m: m.group(1) + content + m.group(2), text), encoding="utf-8")


def reports(cues, out):
    """Indexes of every text and every doubt, each line with a one-click 'flag' link."""
    tdir = out / "transcript"
    verses = [c for c in cues if c.src]
    doubtful = [c for c in cues if doubts(c)]

    lines = ["# Every recited text, line by line", "",
             "Generated by `tools/build.py` from `transcript.txt`. Spot a problem? Click **flag** on that line.", "",
             "| Time | Scene | Source | Opens with (IAST) | Status | |", "|---|---|---|---|---|---|"]
    for c in verses:
        first = (to_iast(c) or [""])[0].rstrip(" |")
        lines.append(f"| {tshort(c.start)} | {cell(c.section)} | {cell(c.src)} | {cell(first)} | "
                     f"{status(doubts(c))} | [flag]({flag_url(c)}) |")
    (tdir / "verses.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    check_rows = ["| Time | Text | What to check | Why | |", "|---|---|---|---|---|"]
    for c in doubtful:
        check_rows.append(f"| {tshort(c.start)} | {cell(c.src)} | {', '.join(doubts(c))} | {cell(c.note)} | "
                          f"[flag]({flag_url(c)}) |")
    lines = ["# What needs checking", "",
             "These entries are the ones we are least sure of. **text**: only fragments are audible and the "
             "reading is partly reconstructed. **source**: the text is clear but we have not confirmed where it "
             "comes from. **timing**: the words are right but the subtitle may start too late or too early.", "",
             "If you can help with any of them, click **flag** and tell us what you hear or know.", ""] + check_rows
    (tdir / "review-needed.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if out == ROOT:
        readme = ROOT / "README.md"
        inject(readme, "needs-checking", "\n".join(check_rows) + "\n")
        blocks, scene = [], None
        for (sec, src), group in passages(cues):
            if sec != scene:
                blocks += ["", f"**{sec}**", "", "| Time | Text | Opens with | Status | |", "|---|---|---|---|---|"]
                scene = sec
            first, last = group[0], group[-1]
            when = tshort(first.start) if len(group) == 1 else f"{tshort(first.start)} to {tshort(last.end)}"
            found = [d for c in group for d in doubts(c)]
            opening = (to_iast(first) or [""])[0].rstrip(" |")
            flagged = next((c for c in group if doubts(c)), first)
            blocks.append(f"| {when} | {cell(src)} | {cell(opening)} | {status(found)} | [flag]({flag_url(flagged)}) |")
        inject(readme, "texts", "\n".join(blocks).lstrip("\n") + "\n")
    return len(verses), len(doubtful)


def read_srt(path):
    """Minimal SRT reader: [(start, end, text), ...]."""
    raw = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    out = []
    for block in re.split(r"\n\s*\n", raw.replace("\r", "")):
        lines = [x for x in block.strip().splitlines() if x.strip()]
        for i, line in enumerate(lines):
            m = re.match(r"\s*(\S+)\s*-->\s*(\S+)", line)
            if m:
                out.append((parse_time(m[1]), parse_time(m[2]), "\n".join(lines[i + 1:])))
                break
    return out


def merge(cues, dialogue_srt, out):
    """Combine the viewer's own dialogue subtitles with our verse cues, for personal viewing.

    Wherever one of our cues is on screen, overlapping lines from the viewer's file are
    dropped, so the exact text replaces the old paraphrase; everything else is kept.
    """
    theirs = read_srt(dialogue_srt)
    ours = [(c.start, c.end, c) for c in cues]

    def covered(s, e):
        return any(min(e, oe) - max(s, os_) > 0.3 * (e - s) for os_, oe, _ in ours)

    kept = [(s, e, t) for s, e, t in theirs if not covered(s, e)]
    mdir = out / "merged"
    mdir.mkdir(parents=True, exist_ok=True)
    stem = Path(dialogue_srt).stem
    variants = {
        "en": lambda c: c.en,
        "sa-Latn+en": lambda c: [f"<i>{x}</i>" for x in to_iast(c)] + c.en,
        "sa-Deva+en": lambda c: c.sa + c.en,
    }
    for tag, lines_for in variants.items():
        entries = kept + [(s, e, "\n".join(lines_for(c))) for s, e, c in ours if lines_for(c)]
        write_srt(mdir / f"{stem}.merged.{tag}.srt", sorted(entries))
    return len(theirs) - len(kept), len(kept)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--merge", metavar="YOUR_DIALOGUE.srt",
                    help="combine your own dialogue subtitles with these verse cues (output in merged/)")
    ap.add_argument("--offset", type=float, default=0.0, help="seconds to add to every timestamp")
    ap.add_argument("--fps", help="FROM:TO, e.g. 25:23.976, when your copy plays at a different frame rate")
    ap.add_argument("--anchor", action="append", default=[],
                    help="OLD=NEW timestamp pair (give two for an exact fit); OLD is our time, NEW is yours")
    ap.add_argument("--out", help="output directory (default: repo root, or retimed/ when retiming)")
    args = ap.parse_args()

    scale, offset = 1.0, args.offset
    if args.fps:
        a, b = (float(x) for x in args.fps.split(":"))
        scale = a / b
    if args.anchor:
        pairs = [tuple(parse_time(x) for x in p.split("=")) for p in args.anchor]
        if len(pairs) == 1:
            (o1, n1), = pairs
            offset = n1 - o1 * scale
        else:
            (o1, n1), (o2, n2) = pairs[0], pairs[-1]
            scale = (n2 - n1) / (o2 - o1)
            offset = n1 - o1 * scale
    retiming = scale != 1.0 or offset != 0.0
    out = Path(args.out) if args.out else (ROOT / "retimed" if retiming else ROOT)

    cues = parse(SRC)
    retime(cues, scale, offset)
    if args.merge:
        replaced, kept = merge(cues, args.merge, out)
        print(f"merged {len(cues)} verse cues with {kept} lines of {args.merge} "
              f"({replaced} overlapping lines replaced) -> {out / 'merged'}")
        return
    counts = build(cues, out)
    if not retiming:
        export(cues, out)
        n_verses, n_doubtful = reports(cues, out)
        counts["verses"], counts["needs review"] = n_verses, n_doubtful

    long_lines = [(c.line, x) for c in cues for x in c.en if len(x) > EN_LINE_WARN]
    print(f"{len(cues)} cues -> {out}")
    print("  " + ", ".join(f"{k}: {v}" for k, v in counts.items()))
    if retiming:
        print(f"  retimed with scale={scale:.6f} offset={offset:+.3f}s")
    for n, x in long_lines:
        print(f"  note: long English line (transcript line {n}): {x}")


if __name__ == "__main__":
    main()
