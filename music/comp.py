import random, sys, pretty_midi as pm, numpy as np
SF="/usr/share/sounds/sf2/TimGM6mb.sf2"
def chord(root, kind):
    iv={"M":[0,4,7],"m":[0,3,7],"M7":[0,4,7,11],"m7":[0,3,7,10],"7":[0,4,7,10]}[kind]
    return [root+i for i in iv]
def scale(key, minor=False):
    s=[0,2,4,5,7,9,11] if not minor else [0,2,3,5,7,8,10]
    return [key+12*o+i for o in (4,5) for i in s]
def make(seed, key, bpm, prog, name, swing=0.0, bars_form=("A","A2","B","A")):
    rnd=random.Random(seed); m=pm.PrettyMIDI(initial_tempo=bpm); p=pm.Instrument(0, name="piano")
    beat=60/bpm; bar=4*beat; t=0.0
    sc=scale(key-12+12)  # around C5
    motifs={}
    def motif():
        # 4-note rhythmic-melodic cell as scale-degree steps and lengths
        steps=[rnd.choice([-2,-1,1,2,0,3,-3]) for _ in range(4)]
        lens=rnd.choice([[1,.5,.5,2],[1.5,.5,1,1],[1,1,1,1],[2,1,.5,.5]])
        return steps,lens
    base={}
    for sec in set(bars_form): base[sec]=[motif(),motif()]
    cur=sc.index(min(sc,key=lambda x:abs(x-(key+7))))   # start near 5th
    for sec in bars_form:
        for bi,(rootoff,kind) in enumerate(prog):
            root=key-24+rootoff           # LH root
            ch=chord(key-12+rootoff,kind)  # RH chord tones near C4
            ct=[c+12*k for c in ch for k in (0,1)]
            # left hand arpeggio, eighths
            ar=[root,root+7,root+12,ch[1]+0 if ch[1]>root+12 else ch[1]+12,root+12+7 if False else ch[2]+12 if ch[2]<root+19 else ch[2],ch[1]+12 if ch[1]+12>root+12 else ch[1]+24]
            pat=[0,1,2,3,2,1,2,1]
            for k,i in enumerate(pat):
                n=ar[i] if i<len(ar) else root+12
                st=t+k*beat/2+(beat/6 if (swing and k%2) else 0)
                p.notes.append(pm.Note(velocity=int(46+8*(k%4==0)+rnd.randint(-3,3)),pitch=int(n),start=st,end=st+beat*0.95))
            # melody
            steps,lens=base[sec][bi%2]
            if sec=="A2" and bi%2==1: steps=[-s for s in steps]
            if sec=="B": steps=[s+(1 if bi%2==0 else 0) for s in steps]
            pos=0.0
            for s,l in zip(steps,lens):
                cur=max(2,min(len(sc)-3,cur+s))
                n=sc[cur]
                # pull long notes toward chord tone
                if l>=1: n=min([c for c in ct if 60<=c<=84] or [n],key=lambda c:abs(c-n))
                v=int(70+10*(pos==0)+rnd.randint(-4,4))
                p.notes.append(pm.Note(velocity=v,pitch=int(n),start=t+pos*beat,end=t+(pos+l)*beat*1.1))
                pos+=l
            if bi==len(prog)-1 and sec!="A" or False: pass
            t+=bar
    # final chord ring
    root=key-12+prog[0][0]
    for n in chord(root,"M" if prog[0][1] in("M","M7") else "m"): p.notes.append(pm.Note(velocity=60,pitch=n,start=t,end=t+bar*1.5))
    # sustain pedal each bar
    tt=0.0
    while tt<t:
        p.control_changes.append(pm.ControlChange(64,127,tt)); p.control_changes.append(pm.ControlChange(64,0,tt+bar-0.05)); tt+=bar
    m.instruments.append(p); m.write(f"{name}.mid")
    audio=m.fluidsynth(fs=44100,sf2_path=SF)
    import soundfile as sf
    sf.write(f"{name}.wav",audio/ max(1e-6,np.abs(audio).max())*0.9,44100)
    print(name, round(len(audio)/44100,1),"s")
C=0
# 90s ballad: Fmaj7 G Em7 Am  / Dm7 G C ... (IV V iii vi)
ballad=[(5,"M7"),(7,"7"),(4,"m7"),(9,"m"),(2,"m7"),(7,"7"),(0,"M7"),(9,"m")]
# citypop: Dm7 G7 CM7 Am7 ... ii V I vi
city=[(2,"m7"),(7,"7"),(0,"M7"),(9,"m7"),(2,"m7"),(7,"7"),(0,"M7"),(4,"7")]
make(7,60,70,ballad,"sample_ballad90")
make(11,60,96,city,"sample_citypop80",swing=1)
