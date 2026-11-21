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
def pick(mood, rnd, used):
    """mood 장면 중 아직 덜 쓴 것을 골라 (프롬프트, 제목)을 돌려준다. 제목도 겹치지 않게."""
    pool = SCENES.get(mood) or SCENES["ballad90"]; cnt = used.setdefault(mood, {})
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
