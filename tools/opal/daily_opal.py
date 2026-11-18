"""Opal Marketing daily renderer.

  python3 daily_opal.py day.json out_dir

day.json = {"posts": [ {"slug": "o_2026-11-19_a", "theme": "light"|"navy", "template": "statement"|"listing"|"stat"|"myth"|"offer"|"cta",
                        "args": {...keyword args for templates.<template>...}}, ... ]}
Template args (see templates.py; a head line starting with "*" renders in the opal gradient):
  statement: seed, kicker_txt, head[list], body, sub, size(=104)
  listing:   seed, kicker_txt, head[list], items[[title, desc], ...] (3-4 items), numbered(bool)
  stat:      seed, kicker_txt, number, label, body, source
  myth:      seed, myth_txt, fact_head[list], fact_body
  offer:     seed
  cta:       seed, head[list], sub
Each post -> out_dir/<slug>.mp4 (7.5 s, music) + <slug>.png (final frame). Theme is per process, so each post renders in a
subprocess with OPAL_THEME set. Cover: use videoCoverMilliseconds 7000 (videos fade in from black).
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TRACKS = sorted(f for f in os.listdir(os.path.join(ROOT, "music")) if f.endswith((".m4a", ".wav")))


def render_one(post, out_dir, idx):
    import opal, templates as T
    from animate import frames, encode, BAR
    img = getattr(T, post["template"])(**post["args"])
    st = list(opal.STAGES)
    opal.save(img, os.path.join(out_dir, post["slug"] + ".png"))
    encode(frames(st, 3 * BAR), (1080, 1920), os.path.join(out_dir, post["slug"] + ".mp4"), 3 * BAR,
           music_offset=(4 + 3 * (idx % 5)) * BAR, music=os.path.join(ROOT, "music", TRACKS[idx % len(TRACKS)]))


if __name__ == "__main__":
    if sys.argv[1] == "--one":
        post = json.loads(sys.argv[2]); render_one(post, sys.argv[3], int(sys.argv[4])); sys.exit()
    day = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    procs = []
    for i, p in enumerate(day["posts"]):
        env = dict(os.environ, OPAL_THEME="light" if p.get("theme") == "light" else "navy")
        procs.append(subprocess.Popen([sys.executable, os.path.abspath(__file__), "--one", json.dumps(p), out, str(i + int(day.get("offset", 0)))],
                                      env=env, cwd=ROOT))
    bad = [p.wait() for p in procs]
    for p, rc in zip(day["posts"], bad):
        print(("OK   " if rc == 0 else "FAIL ") + p["slug"])
