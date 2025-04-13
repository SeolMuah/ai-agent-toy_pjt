from .llm_factory import create_llm
import json

# GPT 기반 활동 추천 에이전트 구성
llm = create_llm(temperature=0.5, json_format=True)


def recommend_activity(state: dict) -> dict:
    """
    GPT를 사용하여 사용자의 상황과 입력을 기반으로
    추천할 활동 2가지를 생성하는 함수입니다.
    """

    # 입력 상태에서 정보 추출
    user_input = state.get("user_input", "")
    season = state.get("season", "봄")
    weather = state.get("weather", "Clear")
    time_slot = state.get("time_slot", "점심")

    # GPT에게 활동 추천을 요청할 프롬프트 작성
    prompt = f"""# 당신은 상황에 맞는 맞춤형 활동을 추천하는 전문 AI 비서입니다.

    ## 현재 상황
    - 사용자 입력: "{user_input}"
    - 계절: {season}
    - 날씨: {weather} 
    - 시간대: {time_slot}

    ## 추천 기준
    1. 계절, 날씨, 시간대를 고려한 적절한 활동
    2. 사용자 입력에서 언급된 취향이나 제약 사항 반영
    3. 구체적이고 실행 가능한 활동을 추천 (예: "운동하기"보다는 "공원에서 조깅하기" 같이 구체적으로)
    4. 다양성을 위해 실내/실외 활동 각각 하나씩 포함

    ## 추천 예시
    - 봄/맑음/오전: ["벚꽃 구경하기", "루프탑 카페에서 브런치"]
    - 여름/비/저녁: ["실내 영화관 방문", "북카페에서 책 읽기"]
    - 가을/흐림/오후: ["미술관 전시회 관람", "근교 단풍 드라이브"]
    - 겨울/눈/아침: ["실내 온천 즐기기", "크리스마스 마켓 방문"]

    ## 출력 형식
    정확히 2개의 활동을 추천하여 JSON 배열로 반환하세요.
    예: ["세부 활동 1", "세부 활동 2"]
    """  # 안전한 f-string

    # GPT 호출
    response = llm.invoke([{"role": "user", "content": prompt.strip()}])

    # GPT 응답 파싱
    items = json.loads(response.content)

    # dict 형태 응답 → 값만 리스트로 추출
    if isinstance(items, dict):
        items = [i for sub in items.values() for i in (sub if isinstance(sub, list) else [sub])]
    elif not isinstance(items, list):
        items = [str(items)]  # 단일 문자열을 리스트로 감싸기

    # 추천 활동을 상태에 추가하여 반환
    return {**state, "recommended_items": items}
    