import streamlit as st
from run_graph import graph
from current_location import *



# Streamlit 웹 앱 페이지 설정
st.set_page_config(page_title="뭐 먹지? 뭐 하지?", page_icon="🍽", layout="wide")

# 페이지 제목
st.title("🍽 오늘은 뭐 먹고 뭐 할까요?")
st.markdown("현재 날씨, 계절, 시간대, 위치와 사용자의 상황에 맞춰 맞춤형 음식과 활동을 추천해드립니다!")


# --- 입력 영역: 왼쪽 사이드바에 사용자 입력 폼 구성 ---
with st.sidebar:
    ip_info = get_location_by_ip()
    local_info = search_place_by_coordinates(ip_info["lon"], ip_info["lat"])

    st.header("📝 입력 정보")
    location = st.text_input("지역 (예: 홍대, 강남) 미 입력시 현재 위치 기반 정보 제공", placeholder=local_info['place_keyword'], value="")  # 사용자의 지역 입력
    user_input = st.text_input("지금 기분이나 상황을 말해주세요", value="몸이 찌뿌둥 한데 뭘 하면 좋을까?")  # 자연어 입력
    submitted = st.button("추천 받기")  # 추천 실행 버튼
    search_radius = st.slider("검색 반경 (km)", 
                                 min_value=1, 
                                 max_value=20, 
                                 value=10,
                                 step=1)
    search_radius = search_radius * 1000  # km를 m로 변환
# --- 추천 실행 및 결과 출력 영역 ---
if submitted:
    # LangGraph에 전달할 상태 구성
    
    if location :
        local_info = search_place_by_keyword(location)

    
    print("📍 현재 위치 정보:", local_info)

    
    state = {
        "user_input": user_input,
        "location": location,
        "lat": local_info.get("lat", 37.5665),  # 서울의 위도
        "lon": local_info.get("lon", 126.978),  # 서울의 경도
        "location": local_info.get("place_keyword", "서울"),  # 서울
        "search_radius": search_radius,  # 검색 반경
    }

    # 실행 중 표시
    with st.spinner("추천을 생성 중입니다..."):
        try:
            # LangGraph 실행: 상태를 기반으로 에이전트 흐름 수행
            events = list(graph.stream(state))


            # 최종 상태 추출 (마지막 단계의 결과)
            final_state = events[-1].get("__end__") or events[-1].get("summarize_message", {})
            final_message = final_state.get("final_message", "추천 결과가 생성되지 않았습니다.")

            # 결과를 세션에 저장 (재사용 목적)
            st.session_state["last_result"] = final_state

            # 결과 영역: 추천 메시지 출력
            st.subheader("📦 최종 추천 결과")
            st.markdown(final_message)
            

            # 디버깅 영역: 각 단계별 상태 출력
            st.divider()
            st.subheader("🔍 디버깅 정보")
            # 디버깅 로그 출력
            st.write("✅ LangGraph 실행 완료")
            for i, e in enumerate(events):
                st.markdown(f"**Step {i+1}:** `{list(e.keys())[0]}`")  # 각 노드 이름
                st.json(e)  # 상태 출력

        except Exception as e:
            # 예외 발생 시 오류 메시지 출력
            st.error(f"❌ 실행 중 오류 발생: {str(e)}")
            
            