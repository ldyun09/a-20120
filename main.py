import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정 (넓은 화면 레이아웃 적용)
st.set_page_config(page_title="영화 박스오피스 분석", layout="wide")


# 1. 데이터 불러오기 (캐싱을 적용하여 앱 재실행 시 데이터 다시 다운로드 방지)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # 2. 데이터 전처리
    # 결측치(빈 값)가 포함된 행 삭제
    df = df.dropna()

    # '기준일자' 컬럼을 날짜(datetime) 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 전체 데이터를 기준일자 오름차순으로 정렬
    df = df.sort_values(by="기준일자")

    return df


# 데이터 로드 실행
df = load_data()

# 메인 화면 타이틀
st.title("🎬 영화 박스오피스 데이터 분석")

# 3. 영화 선택 기능
# 영화별 누적관객수의 최대값을 구한 뒤, 내림차순으로 영화명 목록 정렬
movie_order = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사이드바에서 관객수가 많은 순서대로 나열된 영화 선택박스 생성
selected_movie = st.sidebar.selectbox(
    "분석할 영화를 선택하세요", options=movie_order
)

# 5. 그래프 구역 나누기 (구역 1: 선택한 영화의 관객수 추이)
st.subheader("📈 일별 관객수 변화 추이")

with st.container():
    # 사용자가 선택한 영화의 데이터만 추출
    filtered_df = df[df["영화명"] == selected_movie]

    # 4. Plotly를 활용한 선그래프 생성
    fig = px.line(
        filtered_df,
        x="기준일자",
        y="해당일관객수",
        title=f"[{selected_movie}] 일별 관객수 변화",
        labels={"기준일자": "날짜", "해당일관객수": "관객수(명)"},
        markers=True,  # 데이터 지점에 점 표시
    )

    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

    # 그래프 하단 설명 공간
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'의 개봉 초기 관객 집중도와 주말/평일 관객수 변동 주기를 확인할 수 있습니다."
    )

st.divider()

# 구역 2: 추후 추가할 그래프를 위한 예시 공간
st.subheader("📊 추가 분석 구역 (예정)")

with st.container():
    st.write("이곳에 향후 다른 시각화 그래프나 요약 통계 지표를 추가할 수 있습니다.")

    # 추가 그래프 설명 문구 작성 공간예시
    st.caption("💡 **이 그래프로 알 수 있는 것:** (추가 분석 내용이 입력될 자리입니다.)")
