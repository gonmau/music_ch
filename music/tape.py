import numpy as np, soundfile as sf
from scipy import signal
def tape(inp, out, seed=1, drive=1.7, lp=8500, hiss_db=-54, wet=.16):
    x, sr = sf.read(inp, dtype="float32"); rnd = np.random.RandomState(seed)
    n = len(x); t = np.arange(n) / sr
    # 와우·플러터: 재생 속도가 미세하게 흔들림
    d = 0.0022*np.sin(2*np.pi*.45*t+rnd.rand()*6) + 0.0007*np.sin(2*np.pi*5.8*t+rnd.rand()*6) + np.cumsum(rnd.randn(n))*1e-7
    idx = np.clip(np.arange(n) - d*sr, 0, n-1)
    y = np.stack([np.interp(idx, np.arange(n), x[:, c]) for c in range(2)], 1)
    # 테이프 톤: 저음 정리, 고음 감쇠, 부드러운 포화
    sos = signal.butter(2, [45, lp], "bandpass", fs=sr, output="sos"); y = signal.sosfilt(sos, y, axis=0)
    y = np.tanh(y*drive)/np.tanh(drive)
    # 작은 룸 리버브
    L = int(1.3*sr); ir = rnd.randn(L)*np.exp(-np.arange(L)/(0.32*sr)); ir = signal.sosfilt(signal.butter(2, 4500, "low", fs=sr, output="sos"), ir)
    ir /= np.abs(ir).max()*12
    wetsig = np.stack([signal.fftconvolve(y[:, c], ir)[:n] for c in range(2)], 1); y = y*(1-wet*.5) + wetsig*wet
    # 아주 약한 테이프 히스
    h = signal.sosfilt(signal.butter(2, [900, 7000], "bandpass", fs=sr, output="sos"), rnd.randn(n, 2), axis=0)
    y = y + h*10**(hiss_db/20)
    y = y/np.abs(y).max()*.88; sf.write(out, y, sr)
