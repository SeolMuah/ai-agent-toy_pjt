from .llm_factory import create_llm
import json

# GPT 기반 검색 키워드 생성 에이전트
# 사용자의 음식 또는 활동 추천 결과를 바탕으로 실제 장소 검색에 최적화된 키워드로 변환합니다.

# 키워드 추출용 LLM (명확한 카테고리 변환을 위한 낮은 temperature)
llm = create_llm(temperature=0.3, json_format=True)

def generate_search_keyword(state: dict) -> dict:
    """
    추천된 음식이나 활동을 실제 장소 검색에 적합한 카테고리 키워드로 변환하는 함수
    
    Args:
        state (dict): 현재 대화 상태를 담고 있는 딕셔너리
            - recommended_items: 추천된 음식/활동 항목 (리스트, 딕셔너리, 또는 문자열)
            - user_input: 사용자의 원래 질의 내용
            - intent: 의도 유형 ('food' 또는 'activity')
    
    Returns:
        dict: 업데이트된 state 딕셔너리 (search_keyword 키가 추가됨)
            - search_keyword: 검색에 사용할 카테고리 키워드
    
    Examples:
        - 음식: '김치찌개' → '한식'
        - 활동: '책 읽기' → '북카페', '도서관'
    """

    # 추천 항목 리스트 추출 (음식 또는 활동)
    items = state.get("recommended_items", ["추천"])
    results = []
    if isinstance(items, dict):
        # 딕셔너리인 경우 → 값만 추출 (중첩 flatten)
        items = [i for sub in items.values() for i in (sub if isinstance(sub, list) else [sub])]
    elif not isinstance(items, list):
        items = [str(items)]  # 문자열인 경우 리스트로 변환

    for item in items:
        user_input = state.get("user_input", "")      # 사용자 입력
        intent = state.get("intent", "food")          # food 또는 activity

        # GPT 프롬프트 작성
        prompt = f"""# 장소 검색용 카테고리 키워드 변환
## 입력 정보
- 사용자 원문: "{user_input}"
- 추천 항목: "{item}"
- 의도 유형: "{intent}"

## 작업 설명
당신은 추천된 항목을 지도 앱이나 장소 검색 API에서 실제로 찾을 수 있는 카테고리 키워드로 변환해야 합니다.
중요: 실제 지도 앱에서 검색했을 때 결과가 나오는 실용적인 키워드만 사용하세요.

### 변환 규칙
1. "헬스식", "다이어트식", "저칼로리", "건강식" 같은 추상적 개념은 사용하지 마세요.
2. 실제 음식점이나 장소 유형으로 변환하세요
3. 너무 구체적인 메뉴명보다는 대표 카테고리를 선택하세요.
4. 지도 검색에서 실제로 존재하는 업종 카테고리로 변환하세요.

### 변환 예시
- 음식인 경우:
  - 김치찌개, 된장찌개 → ["한식"]
  - 스테이크, 파스타 → ["양식", "레스토랑"]
  - 초밥, 라멘 → ["일식", "라멘집"]
  - 짜장면, 마라탕 → ["중식"]
  - 치킨, 닭갈비 → ["치킨집", "닭갈비"]
  - 빵, 케이크 → ["베이커리", "카페"]
  - 샐러드, 건강식 → ["샐러드바", "채식전문점"]
  - 다이어트식 → ["샐러드바", "분식"]

- 활동인 경우:
  - 책 읽기 → ["북카페", "도서관"]
  - 영화 보기 → ["영화관", "멀티플렉스"]
  - 커피 마시기 → ["카페"]
  - 산책하기 → ["공원", "산책로"]
  - 쇼핑하기 → ["쇼핑몰", "백화점"]
  - 요가, 필라테스 → ["요가", "필라테스"]
  - 게임하기 → ["PC방"]
  - 운동하기 → ["헬스장", "체육관"]
  - 명상하기 → ["명상원", "요가"]

## 출력 형식
결과는 반드시 JSON 배열 형식으로 출력하세요.
예: ["한식"] 또는 ["북카페", "도서관"]

가장 관련성 높은 카테고리 키워드를 1-2개만 선택하여 반환하세요.
키워드는 실제 지도나 장소 검색 API에서 결과가 나오는 실용적인 업종/장소 카테고리여야 합니다.
"""

        # GPT 호출
        response = llm.invoke([{"role": "user", "content": prompt.strip()}])

        # GPT 응답 파싱
        keywords = json.loads(response.content)

        # dict 형태 응답 → 값 추출
        if isinstance(keywords, dict):
            keywords = [i for sub in keywords.values() for i in (sub if isinstance(sub, list) else [sub])]
        elif not isinstance(keywords, list):
            keywords = [str(keywords)]
        results += keywords
  
    return {**state, "search_keywords": list(set(results))}