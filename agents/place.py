import requests
from config import KAKAO_API_KEY

#%%
def search_place(state: dict) -> dict:
    """
    사용자의 지역 정보(location)와 검색 키워드(search_keyword)를 바탕으로
    Kakao Local API를 호출하여 근처 장소 정보를 가져오는 함수입니다.
    """

    # 상태에서 검색 키워드 및 지역 정보 추출
    x = state.get("lon")           
    y = state.get("lat")           

    keywords = state.get("search_keywords", [])          # 예: "한식", "북카페"
    recommended_places = []
    for keyword in keywords :
        # 검색어는 '지역 + 키워드' 조합으로 구성
        query = f"{keyword}"
        print(">>> GPT 생성 키워드 검색:", query)  # 디버깅용 로그


        # Kakao Local Search API endpoint
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {
            "Authorization": f"KakaoAK {KAKAO_API_KEY}"  # API 키 인증
        }
        params = {
            "query": query,   # 검색어
            "size": 5,         # 최대 5개의 결과 요청
            "x": x,         # 경도
            "y": y,          # 위도  
            "radius": state.get("search_radius", 2000)  # 검색 반경 (기본값: 2000m)
            
        }

        # API 요청 전송
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()  # 요청 실패 시 예외 발생

        # 응답 결과 중 첫 번째 장소만 사용
        docs = res.json()["documents"]

        if docs:
            for doc in docs[:2]: 
                place = {
                    "name": doc["place_name"],               # 장소 이름
                    "address": doc["road_address_name"],     # 도로명 주소
                    "url": doc["place_url"]                  # 지도 링크
                }

                recommended_places.append(place)

    # 추천 장소 정보를 상태에 추가하여 반환
    return {**state, "recommended_places": recommended_places}

if __name__ == "__main__":
    # 테스트용 상태
    test_state = {
        "location": "천안시",  # 예: "Cheonan"
        "search_keyword": "한식"
    }
    result = search_place(test_state)
    print(result)