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

# 사용자가 선택한 영화의 데이터만 추출
filtered_df = df[df["영화명"] == selected_movie]

# ---------------------------------------------------------
# [구역 1] 선택한 영화의 일별 관객수 선 그래프
# ---------------------------------------------------------
st.subheader("📈 선택한 영화의 일별 관객수 변화 추이")

with st.container():
    # Plotly를 활용한 선 그래프 생성
    fig_line = px.line(
        filtered_df,
        x="기준일자",
        y="해당일관객수",
        title=f"[{selected_movie}] 일별 관객수 변화",
        labels={"기준일자": "날짜", "해당일관객수": "관객수(명)"},
        markers=True,  # 데이터 지점에 점 표시
    )

    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig_line, use_container_width=True)

    # 그래프 하단 설명 공간
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'의 개봉 초기 관객 집중도와 주말/평일 관객수 변동 주기를 확인할 수 있습니다."
    )

st.divider()

# ---------------------------------------------------------
# [구역 2] 선택한 영화의 누적 관객수 영역 차트
# ---------------------------------------------------------
st.subheader("📊 선택한 영화의 누적 관객수 증가 추이 (영역 차트)")

with st.container():
    # Plotly를 활용한 영역 차트(area chart) 생성
    fig_area = px.area(
        filtered_df,
        x="기준일자",
        y="누적관객수",
        title=f"[{selected_movie}] 누적 관객수 변화",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)"},
    )

    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig_area, use_container_width=True)

    # 그래프 하단 설명 공간
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** 시간 흐름에 따른 '{selected_movie}'의 총 관객 수 성장 곡선과 흥행 누적 가속도를 한눈에 파악할 수 있습니다."
    )

st.divider()

# ---------------------------------------------------------
# [구역 3] TOP 10 등장 20일 이상 영화 중 누적 관객수 TOP 5 비교 (다중 선 그래프)
# ---------------------------------------------------------
st.subheader("🏆 주요 장기 흥행작(20일 이상 유지) TOP 5 누적 관객수 비교")

with st.container():
    # 1. 영화별 TOP 10 차트 등장 일수(행 개수 또는 날짜 수) 계산
    movie_days = df.groupby("영화명")["기준일자"].nunique()

    # 2. 등장 일수가 20일 이상인 영화 목록만 추출 (20일 미만 제외)
    movies_over_20days = movie_days[movie_days >= 20].index

    # 3. 20일 이상 등장한 영화들 중 최대 누적관객수 기준 상위 5개 영화 추출
    top5_movies = (
        df[df["영화명"].isin(movies_over_20days)]
        .groupby("영화명")["누적관객수"]
        .max()
        .nlargest(5)
        .index.tolist()
    )

    # 4. 조건에 맞는 TOP 5 영화의 데이터만 필터링
    top5_df = df[df["영화명"].isin(top5_movies)]

    # 5. Plotly 다중 선 그래프 생성 (color='영화명' 설정을 통해 영화별 색상 구분 및 범례 생성)
    fig_top5 = px.line(
        top5_df,
        x="기준일자",
        y="누적관객수",
        color="영화명",  # 영화별로 색상을 다르게 지정
        title="20일 이상 TOP 10 유지 영화 중 누적 관객수 TOP 5 성장 비교",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)", "영화명": "영화 제목"},
        markers=True,
    )

    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig_top5, use_container_width=True)

    # 그래프 하단 설명 공간
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 박스오피스 TOP 10에 20일 이상 지속적으로 머무르며 장기 흥행을 이끈 대표 상위 5개 영화의 누적 관객수 성장 경로와 성과를 비교할 수 있습니다."
    )
