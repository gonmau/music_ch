# -*- coding: utf-8 -*-
"""곡마다 한 줄 서사(장면 속 한 컷). 제목 첫 항목(장면 대표 제목)을 키로, (한글, 영문)."""
_C = {
 # ── 기본 분위기 장면 ──
 "거실 불빛 아래 피아노": ("아무도 치지 않는 피아노 위로, 불빛만 오래 앉아 있었다.", "Only the lamplight sat on the piano, which no one played."),
 "창가에 번지는 불빛": ("커튼 너머 불빛이 번지는 걸 보다가, 오늘도 연락을 하지 않았다.", "I watched the light bleed past the curtain, and again I didn't call."),
 "식어 가는 커피와 편지": ("커피가 식도록 첫 줄을 쓰지 못했다.", "The coffee went cold before I could write the first line."),
 "창가 턴테이블의 밤": ("바늘이 내려앉자, 방 안의 공기가 천천히 옛날로 돌아갔다.", "When the needle dropped, the room slowly drifted back in time."),
 "카세트를 감던 밤": ("되감던 테이프의 그 구간에서, 우리는 아직 웃고 있었다.", "In that stretch of rewound tape, we were still laughing."),
 "커튼에 스민 가로등": ("가로등 빛이 방 안까지 걸어 들어온 밤이었다.", "The streetlamp walked all the way into the room that night."),
 "꺼지지 않은 텔레비전": ("누구도 보지 않는 화면이, 혼자 밤을 지키고 있었다.", "A screen no one watched kept the night company by itself."),
 "촛불 곁의 오래된 꽃": ("마른 꽃도 한때는 향기로 기억되던 사람이었다.", "Even a dried flower was once remembered for its scent."),
 "비 내리는 창가": ("빗소리가 하려던 말을 대신 해 주었다.", "The rain said what I was about to say."),
 "베란다의 안개 낀 밤": ("안개 속 불빛 몇 개가, 아직 깨어 있는 사람들 같았다.", "A few lights in the fog, like people still awake."),
 "빈 방의 달빛": ("달빛만이 비워 둔 자리를 알아봐 주었다.", "Only the moonlight noticed the place I had left empty."),
 "젖은 골목의 가로등": ("비 그친 골목이 오래 들고 있던 이름 하나.", "A name the wet alley held on to long after the rain."),
 "가로등 아래 빈 벤치": ("기다리던 사람은 오지 않았고, 벤치는 끝까지 자리를 지켜 주었다.", "The one I waited for never came; the bench kept the seat to the end."),
 "안개 낀 밤길": ("앞이 흐려도 걸었다. 어딘가 불빛이 하나쯤은 있을 테니.", "Even blurred, I kept walking, sure there'd be one light somewhere."),
 "유리창에 맺힌 빗방울": ("맺혔다가 흘러내리는 건, 빗방울만은 아니었다.", "It wasn't only the raindrops that gathered and then ran down."),
 "계단 끝의 전구": ("계단 끝 전구 하나가, 올라오는 발소리를 기다린다.", "One bulb at the top of the stairs waits for footsteps."),
 "야간 드라이브": ("목적지를 정하지 않은 밤에는 도시가 더 길어 보인다.", "On a night with no destination, the city looks longer."),
 "노을 진 옥상": ("하루가 지고, 옥상엔 말하지 못한 것들만 남았다.", "The day set, and only the unsaid stayed on the rooftop."),
 "젖은 도로 위의 불빛": ("번진 불빛 속에서, 모든 게 조금은 용서가 됐다.", "In the smeared lights, everything felt a little forgiven."),
 "창밖의 야경": ("저 많은 창마다 누군가의 오늘이 켜져 있다.", "Behind every one of those windows, someone's today is lit."),
 "해 질 무렵의 고가도로": ("저녁 하늘 아래, 집으로 가는 길이 가장 느리게 흘렀다.", "Under the evening sky, the way home flowed slowest."),
 "밤의 수영장": ("물빛이 가만히 흔들리자, 낮의 소란이 가라앉았다.", "As the water-light swayed, the noise of the day settled."),
 "해 질 녘 바닷길": ("바다는 오늘도 아무 질문 없이 나를 보내 주었다.", "The sea let me go today without asking a thing."),
 "저녁 발코니": ("저녁 바람이 하루치 숨을 돌려주었다.", "The evening breeze gave me back a day's worth of breath."),
 "아침 햇살이 닿는 방": ("밤을 지난 햇살이 마룻바닥에 조용히 앉았다.", "Sunlight that survived the night settled quietly on the floor."),
 "창가의 오래된 피아노": ("먼지 앉은 건반에도, 아직 누르면 나오는 소리가 있었다.", "Even dusty keys still answered when pressed."),
 "서재의 낮은 불빛": ("책장 사이에서, 시간이 잠깐 걸음을 멈췄다.", "Between the shelves, time stopped walking for a moment."),
 "안개 낀 호숫가의 새벽": ("아직 아무도 깨우지 않은 물결 위로, 새벽이 번졌다.", "Dawn spread across water no one had woken yet."),
 "커튼 사이로 든 빛": ("바람이 커튼을 열자, 하루가 슬쩍 들어왔다.", "The wind parted the curtain and the day slipped in."),
 "긴 그림자의 복도": ("긴 그림자 끝에서, 오래전 발소리가 지나갔다.", "At the end of the long shadows, old footsteps passed."),
 "찻잔 위의 아침": ("김이 오르는 동안만큼은 아무것도 서두르지 않았다.", "For as long as the steam rose, nothing was in a hurry."),
 "눈 내리는 창가": ("눈이 쌓이는 소리는 들리지 않지만, 마음엔 쌓였다.", "You can't hear snow settle, but it settled in me."),
 # ── 겨울 ──
 "눈 내리는 창가의 불빛": ("눈이 내리자, 창가 불빛이 더 따뜻해졌다.", "As the snow fell, the window light grew warmer."),
 "서리 낀 창문 너머": ("서리 너머의 세상은 모두 조금씩 다정해 보였다.", "Beyond the frost, the whole world looked a little kinder."),
 "김 서린 머그잔": ("두 손으로 감싼 온기가, 오늘 하루의 전부였다.", "The warmth held in both hands was the whole of today."),
 "눈 덮인 지붕 위의 밤": ("지붕 위에 눈이 쌓이는 밤, 멀리 창문이 하나씩 꺼졌다.", "Snow on the roofs, and far windows going dark one by one."),
 "담요 속의 겨울": ("담요 속으로 들어가면, 겨울도 꽤 괜찮은 계절이었다.", "Under a blanket, winter wasn't such a bad season."),
 # ── 비 ──
 "비 내리는 밤 창가": ("비는 밤새 같은 얘기를 창문에 적고 있었다.", "All night the rain kept writing the same story on the glass."),
 "젖은 아스팔트의 불빛": ("젖은 길 위로 불빛이 누워, 나를 따라왔다.", "The lights lay on the wet road and followed me home."),
 "비 맞는 버스 정류장": ("막차는 늦었고, 정류장엔 빗소리만 먼저 도착했다.", "The last bus was late; only the sound of rain arrived first."),
 "현관 앞의 우산": ("우산 끝에 매달린 빗방울이 한참 떨어지지 않았다.", "A raindrop clung to the umbrella tip and wouldn't fall."),
 "창문을 두드리는 빗방울": ("누가 두드리는 줄 알고, 한 번 돌아봤다.", "I turned around once, thinking someone was knocking."),
 # ── 행복 ──
 "작은 전구가 켜진 방": ("작은 불빛 몇 개로도 방이 한결 웃는 것 같았다.", "A few small lights, and the room seemed to smile."),
 "노을빛 옥상의 저녁": ("하늘이 분홍으로 물들던 날, 아무 걱정이 없었다.", "The sky turned pink, and I had no worries at all."),
 "불빛 환한 골목": ("골목 끝까지 웃음이 번져 있던 밤이었다.", "Laughter reached all the way down the alley that night."),
 "바닷길 드라이브": ("창문을 내리자 바다 냄새가 먼저 노래를 시작했다.", "I rolled down the window and the sea smell began the song."),
 "불꽃이 번지던 강가": ("불꽃이 터지는 순간, 모두가 같은 하늘을 보고 있었다.", "When the fireworks burst, everyone looked at the same sky."),
 # ── 기대 ──
 "싸 둔 여행 가방": ("가방은 이미 문 앞에서, 내일을 먼저 떠나 있었다.", "The bag by the door had already left for tomorrow."),
 "새벽 기차역 플랫폼": ("첫차를 기다리는 새벽 공기가 이상하게 설렜다.", "The dawn air waiting for the first train was oddly thrilling."),
 "비행기 창밖의 도시": ("작아지는 도시 불빛이 새로운 시작처럼 보였다.", "The shrinking city lights looked like a beginning."),
 "불이 하나둘 켜지는 도시": ("도시에 불이 켜질 때마다 내일이 한 걸음 가까워졌다.", "Each light that came on brought tomorrow a step closer."),
 "바람이 드는 창가": ("창을 열어 둔 건, 내일을 맞을 준비였다.", "I left the window open to be ready for tomorrow."),
 # ── 설렘 ──
 "머리맡에서 빛나는 화면": ("화면이 켜질 때마다 숨을 멈췄다.", "Every time the screen lit up, I held my breath."),
 "탁자 위의 꽃다발": ("받은 꽃이 시들기 전에, 마음을 먼저 전하고 싶었다.", "I wanted to tell my heart before the flowers wilted."),
 "거울 앞의 저녁": ("몇 번이나 옷매무새를 고치고서야 집을 나섰다.", "I fixed my collar a dozen times before I stepped out."),
 "마주 놓인 두 잔": ("마주 놓인 두 잔 사이로, 말보다 먼저 온기가 건너갔다.", "Between two cups, warmth crossed before words did."),
 "가로등 아래 걷던 길": ("같이 걷는 길이, 오늘따라 너무 짧았다.", "The road we walked together was far too short that night."),
 # ── 힘든 밤 ──
 "꺼지지 않는 책상 등": ("모두 퇴근한 뒤에도 책상 등은 끝까지 남아 있었다.", "After everyone left, the desk lamp stayed to the end."),
 "불 꺼진 사무실 복도": ("불 꺼진 복도에, 내 발소리만 늦게 따라왔다.", "In the dark corridor, only my footsteps trailed behind."),
 "막차 안의 빈자리": ("빈자리가 많은데도, 앉을 힘이 남아 있지 않았다.", "So many empty seats, yet no strength left to sit."),
 "무거운 걸음의 퇴근길": ("오늘의 무게는 가방이 아니라 어깨에 있었다.", "Today's weight was not in the bag but on my shoulders."),
 "골목 끝의 불빛": ("골목 끝 불빛 하나가, 오늘은 그걸로 충분했다.", "One light at the end of the alley was enough tonight."),
 # ── 지친 밤 ──
 "현관에 벗어 둔 구두": ("구두를 벗자, 하루가 한꺼번에 내려앉았다.", "When I slipped off my shoes, the whole day settled at once."),
 "소파 위의 외투": ("외투를 걸 힘도 없이, 소파에 잠시 맡겨 두었다.", "Too tired to hang my coat, I left it on the sofa."),
 "옥상의 의자 하나": ("의자 하나, 도시 하나, 숨 한 번이면 충분했다.", "One chair, one city, one long breath was enough."),
 "난간 위의 컵 하나": ("난간 위 컵이 식는 동안, 나도 천천히 식어 갔다.", "As the cup cooled on the railing, so did I."),
 "머리맡의 안경": ("안경을 내려놓자, 세상이 부드럽게 흐려졌다.", "When I set down my glasses, the world softly blurred."),
 # ── 우울 ──
 "회색빛 창가": ("회색 창가에서는 시간이 아주 천천히 지나갔다.", "At the gray window, time passed very slowly."),
 "비어 있는 의자": ("비어 있는 의자는 누구보다 오래 기억하고 있었다.", "The empty chair remembered longer than anyone."),
 "안개 속의 밤길": ("멀어지는 불빛을 끝내 부르지 못했다.", "I never called out to the lights that drifted away."),
 "하나만 켜진 창": ("어두운 건물 속 창 하나, 그곳에도 누군가의 밤이 있다.", "One lit window in a dark building; someone's night is there too."),
 # ── 불멍 ──
 "타오르는 벽난로": ("장작이 타는 동안은, 아무 생각도 하지 않아도 되었다.", "While the logs burned, I didn't have to think about anything."),
 "모닥불 앞의 밤": ("불씨가 하늘로 오를 때마다 걱정도 하나씩 따라갔다.", "Each spark that rose carried one worry up with it."),
 "난로 속 불씨": ("꺼져 가는 불씨에도 한참을 쬘 만한 온기가 있었다.", "Even dying embers had warmth worth lingering for."),
 "촛불이 흔들리는 밤": ("촛불이 흔들릴 때마다 그림자도 함께 숨을 쉬었다.", "Each time the candle flickered, the shadows breathed too."),
 "해변의 모닥불": ("파도 소리와 불꽃 소리가 번갈아 밤을 채웠다.", "Waves and crackling fire took turns filling the night."),
}
def cap(title):
    """제목(뒤에 ' 2' 같은 번호가 붙을 수 있음)에서 (한글, 영문) 한 줄. 없으면 ('','')."""
    import scenes as SC
    base, _, num = title.rpartition(" ")
    t = base if num.isdigit() and base in SC.EN else title
    if t in _C: return _C[t]
    for sc in list(SC.SCENES.values()) + [v["scenes"] for v in SC.THEMES.values()]:
        for _, ts in (sc if isinstance(sc, list) else []):
            if t in ts and ts[0] in _C: return _C[ts[0]]
    return ("", "")
