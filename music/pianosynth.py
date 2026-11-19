# -*- coding: utf-8 -*-
"""Salamander Grand Piano(CC-BY 3.0, Alexander Holm) 샘플로 MIDI를 렌더링하는 간단한 샘플러. 3반음 간격 샘플을 리샘플링으로 음높이 이동."""
import numpy as np, soundfile as sf, pretty_midi as pm
from pathlib import Path
import os
SAMP = Path(os.environ.get("SALAMANDER_DIR", "salamander/Samples"))   # Salamander Grand Piano 샘플 폴더 (저장소에는 넣지 않음)
SR = 48000
NAMES = {"A": 9, "C": 0, "D#": 3, "F#": 6}
ROOTS = {}
for oc in range(0, 9):
    for nm, off in NAMES.items():
        midi = 12 * (oc + 1) + off
        if (SAMP / f"{nm}{oc}v1.flac").exists():
            ROOTS[midi] = f"{nm}{oc}"
_cache = {}
def sample(name, layer):
    k = (name, layer)
    if k not in _cache:
        d, sr = sf.read(SAMP / f"{name}v{layer}.flac", dtype="float32")
        assert sr == SR
        _cache[k] = d
        if len(_cache) > 400: _cache.pop(next(iter(_cache)))
    return _cache[k]
def shifted(midi, vel):
    root = min(ROOTS, key=lambda r: abs(r - midi))
    layer = int(np.clip(round(vel / 127 * 15) + 1, 1, 16))
    d = sample(ROOTS[root], layer)
    ratio = 2 ** ((midi - root) / 12)
    if abs(ratio - 1) < 1e-4: return d
    n = int(len(d) / ratio)
    x = np.arange(n) * ratio
    return np.stack([np.interp(x, np.arange(len(d)), d[:, c]) for c in (0, 1)], 1).astype(np.float32)
def render(midi_path, out_wav, gain=1.0, tail=4.0):
    m = pm.PrettyMIDI(str(midi_path)); inst = m.instruments[0]
    ped = sorted((c.time, c.value >= 64) for c in inst.control_changes if c.number == 64)
    ups = [t for t, on in ped if not on]
    def release(end):
        down = False
        for t, on in ped:
            if t <= end: down = on
        if down:
            nxt = [u for u in ups if u > end]
            return nxt[0] if nxt else end
        return end
    total = max(n.end for n in inst.notes) + tail
    buf = np.zeros((int(total * SR) + SR, 2), np.float32)
    for n in inst.notes:
        s = shifted(int(n.pitch), n.velocity)
        i0 = int(n.start * SR)
        rel = release(n.end); fade = int(0.35 * SR)
        ln = min(len(s), int((rel - n.start) * SR) + fade)
        seg = s[:ln].copy()
        if ln > fade: seg[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
        buf[i0:i0 + len(seg)] += seg * 0.5
    peak = np.abs(buf).max()
    sf.write(out_wav, buf / peak * 0.9 * gain, SR)
    return len(buf) / SR
if __name__ == "__main__":
    import sys
    print(sys.argv[1], round(render(sys.argv[1], sys.argv[2]), 1), "s")
