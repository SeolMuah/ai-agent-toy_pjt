import requests
from config import WEATHER_API_KEY

def get_weather(state: dict) -> dict:
    """OpenWeather API를 통해 현재 날씨 정보를 가져와서 상태에 추가합니다.

    현재는 location이 '서울' 기준으로 고정되어 있으며,
    반환되는 날씨 상태는 'Clear', 'Clouds', 'Rain', 'Snow' 등입니다.
    """
    lon = state.get("lon")         
    lat = state.get("lat")             

    # OpenWeather API 호출 URL과 파라미터 설정
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        # "q": "Seoul",  # 서울 기준으로 변경
        "appid": WEATHER_API_KEY,
        "lang": "kr",
        "units": "metric",
        "lat": lat,  # 위도
        "lon": lon   # 경도
    }

    # API 요청 전 로그 출력
    print(">>> OpenWeather API 호출 시작 (서울 기준)")

    # GET 요청을 통해 날씨 정보 요청
    response = requests.get(url, params=params)
    # 응답 코드가 실패일 경우 예외 발생
    response.raise_for_status()

    # 응답에서 날씨 상태 추출
    weather_data = response.json()
    weather = weather_data["weather"][0]["main"]  # 예: 'Clear', 'Rain', 'Clouds'
    # print(weather_data)
    # 상태에 날씨 정보 추가 후 반환
    return {**state, "weather": weather}
    