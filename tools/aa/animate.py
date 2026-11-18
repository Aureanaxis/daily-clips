"""Turn captured stages into an animated MP4 with music: each element fades + slides up in sequence,
background slowly zooms. Cuts land on bar lines of the 96 BPM track (bar = 2.5 s)."""
import numpy as np
import cv2
import subprocess
from scipy import ndimage

FPS = 30
BAR = 2.5
MUSIC = "out/music/opal_theme.wav"


def prep(stages):
    S = [np.asarray(s.convert("RGB")).astype(np.float32) for s in stages]
    layers = []
    for k in range(1, len(S)):
        d = np.abs(S[k] - S[k - 1]).max(2)
        m = np.clip(d / 14.0, 0, 1)
        if m.max() < 0.05:
            continue
        m = ndimage.maximum_filter(m, 3)
        m = cv2.GaussianBlur(m, (0, 0), 1.0)
        ys, xs = np.where(m > 0.02)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        layers.append((S[k][y0:y1, x0:x1], m[y0:y1, x0:x1, None], (y0, y1, x0, x1)))
    return S[0], layers


def ease(p):
    p = min(max(p, 0.0), 1.0)
    return 1 - (1 - p) ** 3


def frames(stages, duration, intro=0.35, span=None, anim=0.65, dy=46, zoom=0.045, fade_in=True):
    bg, layers = prep(stages)
    H, W = bg.shape[:2]
    n = len(layers)
    span = span if span is not None else min(0.32 * n, duration - intro - anim - 2.2)
    stagger = span / max(n - 1, 1)
    total = int(round(duration * FPS))
    for fi in range(total):
        t = fi / FPS
        z = 1 + zoom * (t / duration)
        Mx = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
        frame = cv2.warpAffine(bg, Mx, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        for k, (src, m, (y0, y1, x0, x1)) in enumerate(layers):
            p = ease((t - intro - k * stagger) / anim)
            if p <= 0:
                continue
            off = int(round(dy * (1 - p)))
            yy0, yy1 = y0 + off, min(y1 + off, H)
            h = yy1 - yy0
            a = m[:h] * p
            reg = frame[yy0:yy1, x0:x1]
            frame[yy0:yy1, x0:x1] = reg * (1 - a) + src[:h] * a
        # quick fade-in from black on the very first frames
        if fade_in and t < 0.2:
            frame *= t / 0.2
        yield np.clip(frame, 0, 255).astype(np.uint8)


def encode(frame_iter, size, out, duration, music_offset=0.0, afade=0.8, vfade_out=0.0, music=None):
    W, H = size
    af = f"afade=t=in:st=0:d=0.15,afade=t=out:st={duration - afade:.2f}:d={afade}"
    vf = "format=yuv420p"
    if vfade_out:
        vf = f"fade=t=out:st={duration - vfade_out:.2f}:d={vfade_out},format=yuv420p"
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-ss", f"{music_offset:.3f}", "-i", music or MUSIC,
           "-t", f"{duration:.3f}", "-map", "0:v", "-map", "1:a",
           "-vf", vf, "-af", af,
           "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-profile:v", "high",
           "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in frame_iter:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg failed for " + out)
