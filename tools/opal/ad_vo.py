"""Opal weekly creative ad with a British female voiceover (Kokoro bf_emma — Jakub's choice, always).

  python3 ad_vo.py ad.json out.mp4

ad.json = {"slug": "...", "music": "opal_theme_d.m4a", "scenes": [
   {"template": "statement"|"listing"|"stat"|"myth"|"offer"|"cta", "args": {...as daily_opal.py...}, "vo": "Line spoken over this scene."},
   ... 6-8 scenes, ~25-35 s total; hook first, logo/CTA scene last ("DM “OPAL”") ]}
Each scene lasts as long as its line (+0.7 s, min 2.6 s); text animates in fast on the beat. Navy theme.
Needs the Kokoro model files in $KOKORO_DIR (default ./tts): kokoro-v1.0.onnx + voices-v1.0.bin from
https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/ ; pip install kokoro-onnx soundfile.
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
KDIR = os.environ.get("KOKORO_DIR", os.path.join(ROOT, "tts"))
VOICE = "bf_emma"
SR = 24000


def tts_lines(lines):
    from kokoro_onnx import Kokoro
    k = Kokoro(os.path.join(KDIR, "kokoro-v1.0.onnx"), os.path.join(KDIR, "voices-v1.0.bin"))
    out = []
    for t in lines:
        a, _ = k.create(t, voice=VOICE, speed=1.0, lang="en-gb")
        a = a.astype(np.float32)
        idx = np.where(np.abs(a) > 0.01)[0]
        out.append(a[max(idx[0] - 240, 0): idx[-1] + 1200] if len(idx) else a)
    return out


def main(spec_path, out):
    spec = json.load(open(spec_path))
    os.environ["OPAL_THEME"] = "navy"
    sys.path.insert(0, ROOT)
    import opal, templates as T
    from animate import frames, encode
    clips = tts_lines([s["vo"] for s in spec["scenes"]])
    durs = [max(2.6, len(c) / SR + 0.7) for c in clips]
    total = sum(durs)
    # voice track
    track = np.zeros(int((total + 1) * SR), np.float32)
    t = 0.0
    for c, d in zip(clips, durs):
        i = int((t + 0.15) * SR); track[i:i + len(c)] += c; t += d
    track = track[:int(total * SR)]
    track /= max(np.abs(track).max(), 1e-6) / 0.9
    vo = out + ".vo.wav"
    with wave.open(vo, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((track * 32767).astype(np.int16).tobytes())
    # picture
    def it():
        for s, d in zip(spec["scenes"], durs):
            getattr(T, s["template"])(**s["args"])
            st = list(opal.STAGES)
            yield from frames(st, d, intro=0.05, span=min(1.2, d * 0.45), anim=0.35, dy=60, zoom=0.06, fade_in=False)
    silent = out + ".pic.mp4"
    encode(it(), (1080, 1920), silent, total, music_offset=10.0, music=os.path.join(ROOT, "music", spec.get("music", "opal_theme_d.m4a")),
           afade=1.5, vfade_out=0.5)
    fc = ("[1:a]highpass=f=90,equalizer=f=180:t=q:w=1:g=2,equalizer=f=6500:t=q:w=1.5:g=-2,"
          "acompressor=threshold=-22dB:ratio=2.5:attack=10:release=150,aecho=0.8:0.5:28|46:0.10|0.06,"
          "loudnorm=I=-14:TP=-1.5:LRA=7,aresample=44100,asplit=2[v1][v2];"
          "[0:a]volume=0.55[m];[m][v1]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[md];"
          "[md][v2]amix=inputs=2:normalize=0:weights=1 1,alimiter=limit=0.95[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", vo, "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    os.remove(silent); os.remove(vo)
    # cover = middle of the last scene (logo + CTA fully revealed)
    json.dump({"duration": total, "cover_ms": int((total - durs[-1] / 2) * 1000)}, open(out + ".json", "w"))
    print(out, f"{total:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
