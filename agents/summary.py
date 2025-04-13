from .llm_factory import create_llm
# GPT 기반 최종 요약 메시지 생성 에이전트 구성

# 요약 메시지용 LLM (일반 텍스트 형식, 적절한 temperature)
llm = create_llm(temperature=0.6, json_format=False)

def summarize_message(state: dict) -> dict:
    """
    추천된 음식/활동, 장소, 시간대 정보를 바탕으로
    사용자에게 보여줄 감성적인 요약 문장과 장소 정보를 마크다운 형식으로 생성하는 함수입니다.
    
    장소가 검색되지 않은 경우 적절한 안내 메시지를 생성합니다.
    """

    # 추천 항목 리스트에서 첫 항목 추출
    items = state.get("recommended_items", ["추천 항목 없음"])
    if isinstance(items, dict):
        items = list(items.values())
    elif not isinstance(items, list):
        items = [str(items)]
    item = items[0]  # 요약 문장에 사용할 대표 항목

    # 상태에서 필요한 정보 추출
    season = state.get("season", "")
    weather = state.get("weather", "")
    time_slot = state.get("time_slot", "")
    intent = state.get("intent", "food")
    places = state.get("recommended_places", [])
    search_keywords = state.get("search_keywords", "")
    user_location = state.get("location", "현재 위치")

    # food 또는 activity에 따라 안내 메시지 스타일 조정
    category = "음식" if intent == "food" else "활동"
    
    # 장소가 있는지 확인
    has_place = bool(places and any(place.get("name") for place in places))
    
    # GPT 시스템 프롬프트
    system_prompt = """너는 음식 또는 활동을 추천하는 친절한 AI 에이전트입니다.
직접 장소를 검색해서 추천하고, 정보를 마크다운 형식으로 명확하게 정리해 제공합니다.
감성적인 메시지와 함께 실용적인 정보를 함께 제공하세요."""
    
    # 장소가 있는 경우와 없는 경우에 따라 다른 프롬프트 구성
    if has_place:
        # 마크다운 형식 예시 추가
        markdown_example = """
예시 포맷:
[감성적인 인트로 문장]

#### 추천 정보
- **추천 항목**: [항목 이름]
- **장소 유형**: [키워드]

#### 추천 장소 목록
1. **[장소명]**
   - 주소: [주소]
   - 거리: [거리]km
   - [링크가 있는 경우] [지도 링크](URL)

2. **[장소명]**
   - 주소: [주소]
   - 거리: [거리]km
   - [링크가 있는 경우] [지도 링크](URL)

[마무리 메시지]
"""
        
        # 장소 정보 포맷팅 (최대 3개)
        formatted_places = []
        for i, place in enumerate(places, 1):
            name = place.get("name", "")
            address = place.get("address", "")
            distance = place.get("distance", "")
            url = place.get("url", "")
            
            place_info = f"{i}. **{name}**"
            if address:
                place_info += f"\n   - 주소: {address}"
            if distance:
                place_info += f"\n   - 거리: {distance}km"
            if url:
                place_info += f"\n   - [지도에서 보기]({url})"
            
            formatted_places.append(place_info)
        
        # 장소 정보 문자열로 변환
        places_str = "\n\n".join(formatted_places)
        
        # 장소가 있는 경우의 프롬프트
        prompt = f"""
사용자의 의도는 '{category}'입니다.
현재는 {season}이고, 날씨는 {weather}, 시간대는 {time_slot}입니다.
추천 {category}: {item}
검색 키워드: {search_keywords}

다음 장소 정보를 바탕으로 사용자에게 추천 메시지를 작성해 주세요:

{places_str}

다음 형식으로 마크다운 포맷으로 출력해 주세요:
1. 감성적이고 따뜻한 인트로 문장 (1-2문장)
2. 추천 정보 섹션 (추천 항목 및 키워드 요약)
3. 추천 장소 목록 (이미 포맷팅된 정보 활용)
4. 짧은 마무리 문장

{markdown_example}
"""
    else:
        # 장소가 없는 경우의 프롬프트
        prompt = f"""
사용자의 의도는 '{category}'입니다.
현재는 {season}이고, 날씨는 {weather}, 시간대는 {time_slot}입니다.
추천 {category}: {item}
검색 키워드: {search_keywords}
검색 위치: {user_location}

'{user_location}' 주변에서 '{search_keywords}'에 해당하는 장소를 검색했지만 찾지 못했습니다.

다음 내용이 포함된 마크다운 형식의 메시지를 작성해 주세요:

## 메시지 구성
1. 감성적이고 따뜻한 인트로 문장 (1-2문장)
2. 검색 결과 없음을 안내하는 섹션 (마크다운 형식)
3. 검색 반경을 높이는 시도하거나 다른 키워드로 재검색 하라고 요구
4. 현재 추천된 {category}({item})의 가치/장점에 대한 언급
5. 짧은 마무리 문장

## 주의사항
- 사용자에게 직접 검색하라고 안내하지 마세요. 에이전트가 검색을 수행합니다.
- "조금만 기다려 주세요"와 같은 대기 문구는 사용하지 마세요.
- 마크다운 헤딩, 굵은 글씨 등을 활용해 시각적으로 구분되게 작성하세요.
"""

    # GPT 호출
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt.strip()}
    ])

    # 최종 문장을 상태에 추가하여 반환
    return {**state, "final_message": response.content.strip()}