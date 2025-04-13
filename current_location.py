import requests
from config import KAKAO_API_KEY

def get_location_by_ip(ip_address=None):
    """
    IP 주소를 기반으로 지리적 위치 정보를 반환합니다.
    ip_address가 None이면 현재 사용자의 IP를 사용합니다.
    """
    # IP 주소가 제공되지 않은 경우 현재 IP 조회
    if ip_address is None:
        ip_info = requests.get('https://api.ipify.org?format=json').json()
        ip_address = ip_info["ip"]

    # IP 지오로케이션 API 사용 (무료 API)
    response = requests.get(f'http://ip-api.com/json/{ip_address}')
    
    # API 응답이 정상인지 확인
    if response.status_code == 200:
        location_data = response.json()
        
        if location_data["status"] == "success":
            # 결과 출력
            # IP 주소: 210.181.145.109
            # 국가: South Korea
            # 지역: Chungcheongnam-do
            # 도시: Cheonan-si
            # 위도: 36.7667
            # 경도: 127.282
            # ISP: Korea University Of Technology And Education
            
        
            # 위치 데이터 반환
            return {
                "ip": ip_address,
                "country": location_data.get('country'),
                "region": location_data.get('regionName'),
                "city": location_data.get('city'),
                "lat": location_data.get('lat'),
                "lon": location_data.get('lon'),
            }
        else:
            print("위치 정보를 찾을 수 없습니다.")
            return None
    else:
        print(f"API 요청 실패: {response.status_code}")
        return None


#%%
def search_place_by_coordinates(x, y) -> dict:
    """
    좌표(경도, 위도)를 이용하여 해당 위치의 주소 정보를 Kakao Local API로부터 조회합니다.
    
    Args:
        x (float): 경도(longitude) 좌표값
        y (float): 위도(latitude) 좌표값
        
    Returns:
        dict: 조회된 도로명 주소 정보. 결과가 없을 경우 None 반환
        
    Raises:
        HTTPError: API 요청 실패 시 발생
    """
    # Kakao Local API 엔드포인트 설정
    url = "https://dapi.kakao.com/v2/local/geo/coord2address.json"
    
    # API 호출을 위한 헤더 설정
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }
    
    # API 요청 파라미터 설정
    params = {
        "x": x,                # 경도(longitude)
        "y": y,                # 위도(latitude)
        "input_coord": "WGS84" # 좌표계: WGS84(세계 표준 좌표계)
    }

    # API 요청 전송 및 응답 받기
    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()  # 요청 실패 시 예외 발생
    
    # 응답 데이터에서 문서 목록 추출
    docs = res.json()["documents"]
    
    # 결과가 있으면 첫 번째 항목의 도로명 주소 반환, 없으면 None 반환
    if docs:
        place_info = docs[0]['road_address']  # 첫 번째 문서의 도로명 주소 정보
        region_1depth_name = place_info.get('region_1depth_name')
        region_2depth_name = place_info.get('region_2depth_name')
        region_3depth_name  = place_info.get('region_3depth_name')
        keyword = [region_1depth_name, region_2depth_name,region_3depth_name]
        keyword = [name for name in keyword if name]  # None 값 제거
        keyword = ' '.join(keyword)
        return  {   
                "lat": round(y, 5),  # 위도
                "lon": round(x, 5),  # 경도
                "place_keyword": keyword
                }
    else:
        return None

def search_place_by_keyword(keyword) -> dict:
    """
    키워드를 이용하여 장소 정보를 Kakao Local API로부터 검색합니다.
    
    Args:
        keyword (str): 검색할 장소 키워드
        
    Returns:
        dict: 검색된 장소의 위도, 경도, 도로명 주소, 장소명을 포함한 딕셔너리.
              결과가 없을 경우 None 반환
              
    Raises:
        HTTPError: API 요청 실패 시 발생
    """
    # Kakao Local API 엔드포인트 설정
    url = "https://dapi.kakao.com/v2/local/search/address.json?analyze_type=similar"
    
    # API 호출을 위한 헤더 설정
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }
    
    # API 요청 파라미터 설정
    params = {
        "query": keyword,  # 검색 키워드
        "size": 1,         # 반환할 결과 개수 (1개만 요청)
    }

    # API 요청 전송 및 응답 받기
    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()  # 요청 실패 시 예외 발생
    
    # 응답 데이터에서 문서 목록 추출
    docs = res.json()["documents"]
    
    # 결과가 있으면 필요한 정보를 딕셔너리로 구성하여 반환, 없으면 None 반환
    if docs:
        place_info = docs[0]
        x = place_info.get('x')
        y = place_info.get('y')
        return {
            "lat": round(float(y), 5),                    # 위도
            "lon": round(float(x), 5),                    # 경도
            "place_keyword": place_info['address_name'],       # 장소명
        }
    else:
        return None

# 함수 실행 (현재 IP 사용)
if __name__ == "__main__":
    location = get_location_by_ip()
    print(location)
    print(search_place_by_coordinates(126.978, 37.5665))  # 서울역 검색 예시
    print(search_place_by_keyword("대전 산성동"))  # 서울역 검색 예시
# %%
