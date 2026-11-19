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
        ("a quiet bedroom at night, sheer curtains with soft streetlight glow, empty bed", ["커튼에 스민 가로등", "잠들지 못한 방"]),
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
}
def pick(mood, rnd, used):
    """mood 장면 중 아직 덜 쓴 것을 골라 (프롬프트, 제목)을 돌려준다. 제목도 겹치지 않게."""
    pool = SCENES.get(mood) or SCENES["ballad90"]; cnt = used.setdefault(mood, {})
    idx = min(range(len(pool)), key=lambda k: (cnt.get(k, 0), rnd.random())); n = cnt.get(idx, 0); cnt[idx] = n + 1
    prompt, titles = pool[idx]; return prompt, titles[n % len(titles)] + ("" if n < len(titles) else f" {n // len(titles) + 1}")
