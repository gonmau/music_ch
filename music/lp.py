import numpy as np, soundfile as sf
from scipy import signal
def lp(inp, out, seed=1, crackle=0.55, noise_db=-50, lpf=11500):
    x, sr = sf.read(inp, dtype="float32"); rnd = np.random.RandomState(seed); n = len(x); t = np.arange(n)/sr
    # 음정은 안정적으로: 회전 편심(33rpm=0.55Hz)에 의한 아주 미세한 흔들림만
    d = 0.00018*np.sin(2*np.pi*.555*t + rnd.rand()*6)
    idx = np.clip(np.arange(n) - d*sr, 0, n-1)
    y = np.stack([np.interp(idx, np.arange(n), x[:, c]) for c in range(2)], 1)
    # LP 톤: 초저음 럼블 제거, 약간의 따뜻함(저음 살짝 +), 고음은 카세트보다 넓게
    y = signal.sosfilt(signal.butter(2, [32, lpf], "bandpass", fs=sr, output="sos"), y, axis=0)
    lo = signal.sosfilt(signal.butter(1, 220, "low", fs=sr, output="sos"), y, axis=0); y = y + lo*.18
    # 저음은 모노로 (LP 특성), 부드러운 포화
    mid = y.mean(1, keepdims=True); lo2 = signal.sosfilt(signal.butter(2, 160, "low", fs=sr, output="sos"), mid, axis=0)
    y = y - signal.sosfilt(signal.butter(2, 160, "low", fs=sr, output="sos"), y, axis=0) + lo2
    y = np.tanh(y*1.25)/np.tanh(1.25)
    # 표면 소음(지글거림) + 먼지 틱 + 가끔 큰 팝 (자연음 아님, 레코드 잡음)
    sn = signal.sosfilt(signal.butter(2, [600, 9000], "bandpass", fs=sr, output="sos"), rnd.randn(n, 2), axis=0)*10**(noise_db/20)
    ck = np.zeros((n, 2), np.float32)
    for _ in range(int(crackle*n/sr*2.2)):          # 초당 약 1.2회 틱
        p = rnd.randint(0, n-200); a = (rnd.rand()**3)*.05*(1+4*(rnd.rand() < .06))
        w = rnd.randn(rnd.randint(30, 120))*np.hanning(rnd.randint(30, 120)) if False else (rnd.randn(80)*np.hanning(80))
        ck[p:p+80, rnd.randint(0, 2)] += w*a*crackle
    sh = signal.sosfilt(signal.butter(2, 2500, "high", fs=sr, output="sos"), ck, axis=0)
    y = y + sn + sh
    y = y/np.abs(y).max()*.88; sf.write(out, y, sr)
