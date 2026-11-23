# -*- coding: utf-8 -*-
"""분위기별 배경 장면. 곡 제목을 장면에 맞춰 붙여서 제목과 이미지가 어긋나지 않게 한다.
간판·표지판·글자가 생기기 쉬운 장면(거리 가게, 네온 간판, 버스정류장, 지하철역, 극장 등)은 일부러 뺐다: 이미지 AI가 글자를 깨뜨려 그린다."""
STYLE = ("analog 35mm film photograph, heavy film grain, soft focus, slightly out of focus, warm tungsten light, muted faded colors, "
         "nostalgic 1990s atmosphere, cinematic wide composition, dark moody night, empty, quiet")
# (영어 프롬프트, [그 장면에 어울리는 한글 제목들])
SCENES = {
    "ballad90": [
        ("a dim living room at night with an old upright piano and a warm lamp glowing", ["거실 불빛 아래 피아노", "오래된 피아노의 밤"]),
        ("a night window with soft glowing city lights outside, sheer curtain", ["창가에 번지는 불빛", "불 꺼진 창가의 안부"]),
        ("a wooden desk with a handwritten letter, a cup of coffee and a small lamp at night", ["식어 가는 커피와 편지", "오래된 편지의 온도"]),
        ("a vintage record player on a wooden shelf beside a dark window at night, warm lamp", ["창가 턴테이블의 밤", "돌아가는 레코드"]),
        ("a cassette player and old headphones on a table beside a warm lamp", ["카세트를 감던 밤", "낡은 이어폰의 노래"]),
        ("a quiet bedroom at night, sheer curtains with soft streetlight glow, empty bed", ["커튼에 스민 가로등", "가로등이 드는 방"]),
        ("an old television glowing softly in a dark living room, empty sofa", ["꺼지지 않은 텔레비전", "새벽 TV의 푸른빛"]),
        ("a warm candle and a vase of dried flowers on a night table near a window", ["촛불 곁의 오래된 꽃", "마른 꽃의 여운"]),
    ],
    "minor80": [
        ("a rainy window at night with blurred city lights behind the glass", ["비 내리는 창가", "빗방울 너머의 불빛"]),
        ("a balcony railing at night overlooking quiet apartment blocks, light mist", ["베란다의 안개 낀 밤", "아파트 불빛 사이로"]),
        ("an empty room with a single lamp and cold moonlight through the window", ["빈 방의 달빛", "불 하나 켜 둔 방"]),
        ("a narrow wet alley at night with a single streetlamp, glistening asphalt", ["젖은 골목의 가로등", "비 그친 골목"]),
        ("an empty wooden bench under a streetlamp at night, wet pavement, mist", ["가로등 아래 빈 벤치", "기다리던 자리"]),
        ("a foggy empty road at night with a row of soft streetlights", ["안개 낀 밤길", "멀어지는 가로등"]),
        ("a window with raindrops and a dim table lamp reflection at night", ["유리창에 맺힌 빗방울", "혼자 켜 둔 스탠드"]),
        ("a dark empty staircase with a warm bulb light at night, quiet", ["계단 끝의 전구", "아무도 없는 계단"]),
    ],
    "citypop80": [
        ("a car interior at night driving through blurred city lights, dashboard glow, out of focus", ["야간 드라이브", "흐려지는 도시의 불빛"]),
        ("a rooftop at dusk with a faded pink and purple sky and a distant skyline", ["노을 진 옥상", "해 질 녘의 옥상"]),
        ("abstract blurred neon bokeh lights reflected on wet asphalt at night, out of focus", ["젖은 도로 위의 불빛", "번지는 도시의 밤"]),
        ("a city skyline seen from a high apartment window at night, soft glow", ["창밖의 야경", "높은 창가의 도시"]),
        ("an empty highway overpass at dusk with a purple-orange sky", ["해 질 무렵의 고가도로", "저녁 하늘 아래 도로"]),
        ("a quiet swimming pool at night with soft blue underwater light and palm shadows", ["밤의 수영장", "푸른 물빛의 밤"]),
        ("a seaside road at twilight with soft lights and a calm hazy sea", ["해 질 녘 바닷길", "노을 속 해안도로"]),
        ("a balcony at dusk with a warm sky and potted plants, blurred city behind", ["저녁 발코니", "노을이 번지는 베란다"]),
    ],
    "newage": [
        ("morning sunlight falling on a wooden floor in a quiet empty room, soft white curtains", ["아침 햇살이 닿는 방", "고요한 방의 오후"]),
        ("an open piano with a little dust in soft window light, empty room", ["창가의 오래된 피아노", "먼지 위로 내린 빛"]),
        ("a quiet library corner with a warm reading lamp and old books", ["서재의 낮은 불빛", "책장 사이의 고요"]),
        ("a calm lake at dawn with soft mist and a pastel sky", ["안개 낀 호숫가의 새벽", "잔잔한 물결 위의 아침"]),
        ("white curtains gently moving at a sunlit window, quiet room", ["커튼 사이로 든 빛", "바람이 지나간 창가"]),
        ("a sunlit empty hallway with long soft shadows", ["긴 그림자의 복도", "빈 복도의 오후"]),
        ("a teacup and a small plant on a wooden table in soft morning light", ["찻잔 위의 아침", "작은 화분 옆의 시간"]),
        ("a snowy window with a warm interior glow, quiet winter evening", ["눈 내리는 창가", "겨울 저녁의 온기"]),
    ],
}
def pick(mood, rnd, used, theme=None):
    """mood 장면 중 아직 덜 쓴 것을 골라 (프롬프트, 제목)을 돌려준다. 제목도 겹치지 않게."""
    pool = (THEMES[theme]["scenes"] if theme else None) or SCENES.get(mood) or SCENES["ballad90"]; cnt = used.setdefault(theme or mood, {})
    idx = min(range(len(pool)), key=lambda k: (cnt.get(k, 0), rnd.random())); n = cnt.get(idx, 0); cnt[idx] = n + 1
    prompt, titles = pool[idx]; return prompt, titles[n % len(titles)] + ("" if n < len(titles) else f" {n // len(titles) + 1}")

# 곡 제목 영문 (영상 화면·설명란에 병기)
EN = {'거실 불빛 아래 피아노': 'Piano Under the Living Room Light',
    '오래된 피아노의 밤': 'Night of the Old Piano',
    '창가에 번지는 불빛': 'Light Spreading by the Window',
    '불 꺼진 창가의 안부': 'Regards from a Dark Window',
    '식어 가는 커피와 편지': 'Cooling Coffee and a Letter',
    '오래된 편지의 온도': 'Warmth of an Old Letter',
    '창가 턴테이블의 밤': 'Night at the Window Turntable',
    '돌아가는 레코드': 'The Spinning Record',
    '카세트를 감던 밤': 'The Night I Rewound the Tape',
    '낡은 이어폰의 노래': 'Song from Worn Earphones',
    '커튼에 스민 가로등': 'Streetlight Through the Curtain',
    '가로등이 드는 방': 'A Room Lit by the Streetlamp',
    '꺼지지 않은 텔레비전': 'The Television Left On',
    '새벽 TV의 푸른빛': 'Blue Glow of Dawn TV',
    '촛불 곁의 오래된 꽃': 'Old Flowers by the Candle',
    '마른 꽃의 여운': 'Lingering of a Dried Flower',
    '비 내리는 창가': 'Rainy Window',
    '빗방울 너머의 불빛': 'Lights Beyond the Raindrops',
    '베란다의 안개 낀 밤': 'Foggy Night on the Balcony',
    '아파트 불빛 사이로': 'Among the Apartment Lights',
    '빈 방의 달빛': 'Moonlight in an Empty Room',
    '불 하나 켜 둔 방': 'A Room with One Light On',
    '젖은 골목의 가로등': 'Streetlamp in a Wet Alley',
    '비 그친 골목': 'Alley After the Rain',
    '가로등 아래 빈 벤치': 'Empty Bench Under the Streetlamp',
    '기다리던 자리': 'The Place I Waited',
    '안개 낀 밤길': 'Foggy Night Road',
    '멀어지는 가로등': 'Fading Streetlights',
    '유리창에 맺힌 빗방울': 'Raindrops on the Glass',
    '혼자 켜 둔 스탠드': 'A Lamp Left On Alone',
    '계단 끝의 전구': 'Bulb at the End of the Stairs',
    '아무도 없는 계단': 'Stairway with No One',
    '야간 드라이브': 'Night Drive',
    '흐려지는 도시의 불빛': 'Fading City Lights',
    '노을 진 옥상': 'Sunset Rooftop',
    '해 질 녘의 옥상': 'Rooftop at Dusk',
    '젖은 도로 위의 불빛': 'Lights on the Wet Road',
    '번지는 도시의 밤': 'Spreading City Night',
    '창밖의 야경': 'Night View Outside the Window',
    '높은 창가의 도시': 'City from a High Window',
    '해 질 무렵의 고가도로': 'Overpass at Dusk',
    '저녁 하늘 아래 도로': 'Road Under the Evening Sky',
    '밤의 수영장': 'Night Pool',
    '푸른 물빛의 밤': 'Night of Blue Water',
    '해 질 녘 바닷길': 'Seaside Road at Dusk',
    '노을 속 해안도로': 'Coastal Road in the Sunset',
    '저녁 발코니': 'Evening Balcony',
    '노을이 번지는 베란다': 'Balcony Bathed in Sunset',
    '아침 햇살이 닿는 방': 'Room Touched by Morning Sun',
    '고요한 방의 오후': 'Afternoon in a Quiet Room',
    '창가의 오래된 피아노': 'Old Piano by the Window',
    '먼지 위로 내린 빛': 'Light on the Dust',
    '서재의 낮은 불빛': 'Low Light in the Study',
    '책장 사이의 고요': 'Stillness Between the Shelves',
    '안개 낀 호숫가의 새벽': 'Dawn at a Misty Lake',
    '잔잔한 물결 위의 아침': 'Morning on Calm Water',
    '커튼 사이로 든 빛': 'Light Through the Curtains',
    '바람이 지나간 창가': 'Window the Wind Passed',
    '긴 그림자의 복도': 'Hallway of Long Shadows',
    '빈 복도의 오후': 'Afternoon in an Empty Hallway',
    '찻잔 위의 아침': 'Morning Over a Teacup',
    '작은 화분 옆의 시간': 'Time by a Small Plant',
    '눈 내리는 창가': 'Snowy Window',
    '겨울 저녁의 온기': 'Warmth of a Winter Evening'}
def en_title(ko):
    """한글 제목의 영문. 같은 제목이 반복돼 뒤에 숫자가 붙은 경우(" 2")도 처리."""
    base, _, num = ko.rpartition(" ")
    if num.isdigit() and base in EN: return f"{EN[base]} {num}"
    return EN.get(ko, "")


# ── 밤의 서사(테마): 앨범 하나를 한 가지 "밤"으로 묶는다. 곡 분위기·배경 장면·제목·소개문이 함께 정해진다 ──
def _T(key, line1, head_en, moods, intro_ko, intro_en, scenes):
    return key, dict(line1=line1, line2="80~90년대 피아노 발라드", head_en=head_en, moods=moods, intro_ko=intro_ko, intro_en=intro_en, scenes=scenes)
_RAW = [
 _T("winter", "겨울 밤에 듣는", "Winter Night 80s & 90s Piano Ballads", ["newage", "minor80", "ballad90"],
    "눈 내리는 창밖을 바라보던 겨울 밤의 고요함", "the hush of a winter night watching snow fall outside the window", [
    ("snow falling outside a dark apartment window, warm lamp glow reflected on the glass, blurred", [("눈 내리는 창가의 불빛", "Lamplight by the Snowy Window"), ("첫눈이 쌓이는 밤", "The Night the First Snow Settled")]),
    ("frosted window with warm yellow streetlights outside, snowy empty street, blurred bokeh", [("서리 낀 창문 너머", "Beyond the Frosted Window"), ("눈 덮인 골목의 가로등", "Streetlamp in the Snowy Alley")]),
    ("a steaming mug on a wooden table by a window at night, snow outside, soft lamp", [("김 서린 머그잔", "A Steaming Mug"), ("따뜻한 차 한 잔의 밤", "A Night with a Cup of Tea")]),
    ("snow covered rooftops under a dark blue night sky, distant warm windows", [("눈 덮인 지붕 위의 밤", "Night over Snowy Rooftops"), ("멀리 켜진 창문들", "Distant Lit Windows")]),
    ("a wool blanket and a small lamp in a dim living room, winter night, snow on the window", [("담요 속의 겨울", "Winter Under a Blanket"), ("눈 오는 밤의 거실", "Living Room on a Snowy Night")])]),
 _T("rainy", "비 오는 밤에 듣는", "Rainy Night 80s & 90s Piano Ballads", ["minor80", "ballad90"],
    "빗방울이 유리창을 타고 흐르던 밤의 쓸쓸한 여운", "the lonely afterglow of a night when raindrops ran down the window", [
    ("rain streaking a dark window, blurred city lights outside", [("비 내리는 밤 창가", "Rainy Night Window"), ("빗물이 흐르는 유리창", "Rain Running Down the Glass")]),
    ("wet empty street at night with reflections of streetlights, rain, blurred", [("젖은 아스팔트의 불빛", "Lights on Wet Asphalt"), ("비 오는 골목 끝", "End of the Rainy Alley")]),
    ("bus stop shelter at night in the rain, empty bench, blurred glow", [("비 맞는 버스 정류장", "Bus Stop in the Rain"), ("막차를 기다리던 밤", "The Night I Waited for the Last Bus")]),
    ("an umbrella resting by a door, rainy night, warm porch light", [("현관 앞의 우산", "Umbrella by the Door"), ("빗속 너머의 불빛", "Light Beyond the Rain")]),
    ("an open window with a curtain moving, rain outside at night, dim lamp", [("창문을 두드리는 빗방울", "Raindrops on the Window"), ("비 그친 뒤의 새벽", "Dawn After the Rain")])]),
 _T("happy", "행복한 밤에 듣는", "Happy Night 80s & 90s Piano Ballads", ["citypop80", "ballad90"],
    "마음이 가벼웠던 어느 밤의 밝고 따뜻한 스윙감", "the bright, warm swing of a night when everything felt light", [
    ("a warm lamp-lit living room at night with string lights, cozy", [("작은 전구가 켜진 방", "A Room of Small Lights"), ("따뜻한 조명 아래", "Under Warm Lights")]),
    ("a city rooftop at dusk, pink and orange sky, string lights, blurred", [("노을빛 옥상의 저녁", "Sunset Rooftop Evening"), ("분홍빛 하늘 아래", "Under the Pink Sky")]),
    ("a night street with warm shop glow, blurred bokeh, festive", [("불빛 환한 골목", "A Brightly Lit Alley"), ("웃음이 번지던 밤", "A Night of Spreading Laughter")]),
    ("a vintage car driving on a coastal road at night with warm headlights, blurred", [("바닷길 드라이브", "Coastal Drive"), ("창문을 내린 밤길", "Night Road with the Window Down")]),
    ("fireworks bokeh over a calm river at night, blurred", [("불꽃이 번지던 강가", "By the River of Fireworks"), ("행복했던 어느 밤", "A Happy Night Once")])]),
 _T("anticipation", "기대되는 밤에 듣는", "Night of Anticipation 80s & 90s Piano Ballads", ["citypop80", "ballad90"],
    "내일을 기다리며 들뜨던 밤의 설렘", "the quiet excitement of a night spent waiting for tomorrow", [
    ("a packed suitcase beside a door in a lamp-lit room at night, travel anticipation", [("싸 둔 여행 가방", "The Packed Suitcase"), ("떠나기 전날 밤", "The Night Before Leaving")]),
    ("an empty train platform at dawn in blue light, blurred", [("새벽 기차역 플랫폼", "Dawn Train Platform"), ("첫차를 기다리며", "Waiting for the First Train")]),
    ("an airplane window at night with city lights below, wing visible", [("비행기 창밖의 도시", "City Below the Plane Window"), ("구름 위의 밤", "Night Above the Clouds")]),
    ("a city skyline at blue hour with the first lights turning on, hopeful, blurred", [("불이 하나둘 켜지는 도시", "The City Lights Turning On"), ("내일을 기다리는 밤", "The Night Waiting for Tomorrow")]),
    ("a window open to a warm summer night breeze, curtains lifting, lamp", [("바람이 드는 창가", "Window Full of Breeze"), ("기대로 켜 둔 불", "A Light Left On with Hope")])]),
 _T("flutter", "설레는 밤에 듣는", "Fluttering Night 80s & 90s Piano Ballads", ["citypop80", "ballad90"],
    "가슴이 두근거리던 밤의 가볍고 달콤한 떨림", "the light, sweet flutter of a night when your heart raced", [
    ("a phone glowing on a bed in a dark room, soft pink light, blurred", [("머리맡에서 빛나는 화면", "A Glowing Screen at the Bedside"), ("답장을 기다리던 밤", "The Night I Waited for a Reply")]),
    ("a bouquet of flowers in a vase on a table in a lamp-lit room at night", [("탁자 위의 꽃다발", "Bouquet on the Table"), ("받은 꽃 한 송이", "A Single Flower I Received")]),
    ("a mirror reflecting a warm lit room with a jacket hanging, evening getting ready, blurred", [("거울 앞의 저녁", "Evening in Front of the Mirror"), ("약속 시간 전", "Before the Appointed Time")]),
    ("two cups of coffee on a small cafe table by a window at night, warm glow, empty", [("마주 놓인 두 잔", "Two Cups Across the Table"), ("창가 카페의 밤", "Night at the Window Cafe")]),
    ("a night street walk with warm streetlights and falling petals, blurred, romantic", [("가로등 아래 걷던 길", "The Road Walked Under Streetlamps"), ("떨리는 걸음", "Trembling Steps")])]),
 _T("hard", "힘든 밤에 듣는", "Hard Night 80s & 90s Piano Ballads", ["minor80", "ballad90"],
    "무겁게 하루를 마친 밤의 깊고 쓸쓸한 여운", "the deep, lonely afterglow of a night after a heavy day", [
    ("a single desk lamp on a cluttered desk in a dark room at night", [("꺼지지 않는 책상 등", "The Desk Lamp That Stays On"), ("늦도록 켜 둔 스탠드", "A Lamp Kept On Late")]),
    ("an empty office corridor at night, fluorescent lights dimmed, blurred", [("불 꺼진 사무실 복도", "Hallway of a Dark Office"), ("아무도 없는 층", "A Floor with No One")]),
    ("the last subway car at night, empty seats, blurred motion", [("막차 안의 빈자리", "Empty Seats on the Last Ride"), ("덜컹이는 밤 열차", "The Rattling Night Train")]),
    ("a rainy night city street, walking home, distant lights, heavy atmosphere", [("무거운 걸음의 퇴근길", "The Heavy Walk Home"), ("집으로 가는 먼 길", "The Long Way Home")]),
    ("a lone shop glow at a dark street corner, blurred", [("골목 끝의 불빛", "Glow at the Alley's End"), ("늦은 밤 혼자 걷던 길", "The Road I Walked Alone Late")])]),
 _T("tired", "지친 밤에 듣는", "Worn-Out Night 80s & 90s Piano Ballads", ["ballad90", "newage"],
    "긴 하루 끝에 겨우 도착한 밤의 느린 숨결", "the slow breath of a night reached at the end of a long day", [
    ("work shoes left by the door in a dim entrance with a warm lamp, end of day", [("현관에 벗어 둔 구두", "Shoes Left at the Door"), ("하루가 끝난 현관", "The Entryway After the Day")]),
    ("a sofa with a coat thrown over it, dim lamp, night, quiet room", [("소파 위의 외투", "Coat on the Sofa"), ("불을 켜지 못한 거실", "A Living Room Without the Light On")]),
    ("a quiet rooftop at night with city lights in the distance, a single chair", [("옥상의 의자 하나", "A Single Chair on the Rooftop"), ("멀리 보이는 도시", "The City Far Away")]),
    ("an apartment balcony at night, a cup on the railing, city blurred", [("난간 위의 컵 하나", "A Cup on the Railing"), ("숨 돌리는 베란다", "A Breath on the Balcony")]),
    ("a bedside lamp and a pair of glasses on a nightstand, dim", [("머리맡의 안경", "Glasses at the Bedside"), ("조용히 꺼져 가는 불", "Lights Quietly Going Out")])]),
 _T("blue", "우울한 밤에 듣는", "Blue Night 80s & 90s Piano Ballads", ["minor80"],
    "잿빛으로 가라앉은 밤의 깊고 느린 여운", "the deep, slow afterglow of a night that sank into gray", [
    ("a gray rainy window with fog, empty room, cold blue tones", [("회색빛 창가", "A Gray Windowsill"), ("안개 낀 유리창", "Fogged Glass")]),
    ("an empty park bench under a dim streetlamp at night, fog", [("가로등 아래 빈 벤치", "Empty Bench Under the Streetlamp"), ("아무도 없는 공원", "A Park with No One")]),
    ("an empty chair at a table in a dim room, moonlight", [("비어 있는 의자", "An Empty Chair"), ("달빛이 든 빈 방", "An Empty Room with Moonlight")]),
    ("a dark road with fog and distant headlights, cold", [("안개 속의 밤길", "Night Road in the Fog"), ("멀어지는 불빛", "Fading Lights")]),
    ("a single lit window on a dark apartment building at night, rain", [("하나만 켜진 창", "The One Lit Window"), ("불 꺼진 건물 사이", "Between the Darkened Buildings")])]),
 _T("fire", "불멍 하는 밤에 듣는", "Fireside Night 80s & 90s Piano Ballads", ["newage", "ballad90"],
    "타오르는 불빛을 바라보며 시간을 흘려보내던 밤", "a night spent watching the flames and letting time pass", [
    ("a crackling fireplace in a dark cozy room, warm orange glow, no people", [("타오르는 벽난로", "The Burning Fireplace"), ("장작이 타는 밤", "The Night the Logs Burned")]),
    ("a campfire in a forest clearing at night, sparks rising, blurred trees", [("모닥불 앞의 밤", "Night by the Campfire"), ("불씨가 오르는 하늘", "Sparks Rising to the Sky")]),
    ("a wood stove with glowing embers inside a cabin, dim", [("난로 속 불씨", "Embers in the Stove"), ("오두막의 온기", "Warmth of the Cabin")]),
    ("candles burning on a table in a dark room, warm light, blurred", [("촛불이 흔들리는 밤", "The Night the Candles Flickered"), ("작은 불꽃 하나", "A Single Small Flame")]),
    ("a bonfire on a beach at night, waves in the distance, blurred", [("해변의 모닥불", "Beach Bonfire"), ("불빛에 비친 바다", "Sea in the Firelight")])]),
]
THEMES = {}
for _k, _v in _RAW:
    _sc = []
    for _p, _ts in _v["scenes"]:
        for _ko, _en in _ts: EN[_ko] = _en
        _sc.append((_p, [k for k, _ in _ts]))
    _v["scenes"] = _sc; THEMES[_k] = _v

# 테마 장면별 추가 제목 (제목 중복·번호 방지) — titles_extra.py
try:
    from titles_extra import X as _X
    for _pool in list(SCENES.values()) + [_t["scenes"] for _t in THEMES.values()]:
        for _p, _ts in _pool:
            for _ko, _en in _X.get(_ts[0], []):
                if _ko not in _ts: _ts.append(_ko)
                EN.setdefault(_ko, _en)
except Exception as _e:
    print("[scenes] titles_extra 불러오기 실패:", _e)
