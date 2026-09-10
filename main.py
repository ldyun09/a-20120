import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
# [구역 3] 누적 관객수 TOP 5 영화 비교 (다중 선 그래프)
# ---------------------------------------------------------
st.subheader("🏆 누적 관객수 TOP 5 영화 비교 (다중 선 그래프)")

with st.container():
    # 1. 영화별 최대 누적관객수 기준 상위 5개 영화명 추출
    top5_movies = (
        df.groupby("영화명")["누적관객수"]
        .max()
        .nlargest(5)
        .index.tolist()
    )

    # 2. TOP 5 영화의 데이터만 추출
    top5_df = df[df["영화명"].isin(top5_movies)]

    # 3. Plotly 다중 선 그래프 생성
    fig_top5 = px.line(
        top5_df,
        x="기준일자",
        y="누적관객수",
        color="영화명",  # 영화별로 색상을 다르게 지정
        title="누적 관객수 TOP 5 영화의 관객수 증가 비교",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)", "영화명": "영화 제목"},
        markers=True,
    )

    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig_top5, use_container_width=True)

    # 그래프 하단 설명 공간
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 최고 흥행작 TOP 5 영화들의 누적 관객 수 성장 속도 차이 및 개봉 시기별 흥행 경쟁 양상을 한눈에 비교할 수 있습니다."
    )

st.divider()

# ---------------------------------------------------------
# [구역 4] 전체 TOP 10 영화 일별 총 관객수 및 7일 이동평균선
# ---------------------------------------------------------
st.subheader("📉 전체 TOP 10 영화 관객수 합계 및 7일 이동평균")

# 4, 5, 6번 그래프에서 공통 활용할 일별 상위 10개 영화 관객수 합계 계산
daily_top10_sum = (
    df.groupby("기준일자")["해당일관객수"]
    .apply(lambda x: x.nlargest(10).sum())
    .reset_index(name="일별관객수합계")
)

with st.container():
    # 7일 이동평균 계산
    daily_top10_sum["7일이동평균"] = (
        daily_top10_sum["일별관객수합계"].rolling(window=7, min_periods=1).mean()
    )

    # Plotly Graph Objects를 사용하여 원본선(연하게)과 이동평균선(진하게) 생성
    fig_ma = go.Figure()

    # 원본 일별 관객수 합계 (연하고 얇은 선)
    fig_ma.add_trace(
        go.Scatter(
            x=daily_top10_sum["기준일자"],
            y=daily_top10_sum["일별관객수합계"],
            mode="lines",
            name="일별 총관객수 (원본)",
            line=dict(color="rgba(180, 180, 180, 0.5)", width=1.5),
        )
    )

    # 7일 이동평균 (진하고 두꺼운 선)
    fig_ma.add_trace(
        go.Scatter(
            x=daily_top10_sum["기준일자"],
            y=daily_top10_sum["7일이동평균"],
            mode="lines",
            name="7일 이동평균",
            line=dict(color="#1f77b4", width=3.5),
        )
    )

    # 그래프 레이아웃 설정
    fig_ma.update_layout(
        title="일별 TOP 10 영화 관객수 합계 및 7일 이동평균 추이",
        xaxis_title="날짜",
        yaxis_title="관객수(명)",
        hovermode="x unified",
    )

    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig_ma, use_container_width=True)

    # 그래프 하단 설명 공간
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 주말과 평일의 요일별 관객수 진동(노이즈)을 제거하여, 전체 극장가의 계절별/시즌별 흥행 흐름과 시장 규모 변화 추세를 명확하게 파악할 수 있습니다."
    )

st.divider()

# ---------------------------------------------------------
# [구역 5] 월별 전체 관객수 합계 (막대 그래프)
# ---------------------------------------------------------
st.subheader("🗓️ 월별 총 관객수 비교 (막대 그래프)")

with st.container():
    # '기준일자'에서 '연-월(YYYY-MM)' 형식 추출
    daily_top10_sum["연월"] = daily_top10_sum["기준일자"].dt.strftime("%Y-%m")

    # 월(연-월) 단위로 일별 총 관객수 재합산
    monthly_sum = (
        daily_top10_sum.groupby("연월")["일별관객수합계"]
        .sum()
        .reset_index(name="월별관객수합계")
    )

    # Plotly 막대 그래프 생성
    fig_bar = px.bar(
        monthly_sum,
        x="연월",
        y="월별관객수합계",
        title="월별 총 관객수 합계",
        labels={"연월": "연-월", "월별관객수합계": "총 관객수(명)"},
        text_auto=".2s",  # 막대 상단에 간략한 수치 표현
    )

    fig_bar.update_layout(xaxis_type="category")

    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig_bar, use_container_width=True)

    # 그래프 하단 설명 공간
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 연간 월별 총 관객 수 비교를 통해 극장가가 가장 호황을 누렸던 최고의 성수기 달과 상대적으로 침체되었던 비성수기 달을 한눈에 판별할 수 있습니다."
    )

st.divider()

# ---------------------------------------------------------
# [구역 6] 월(주차별) × 요일별 일관객 합계 캘린더 히트맵
# ---------------------------------------------------------
st.subheader("🔥 월(주차별) × 요일별 일관객 합계 (캘린더 히트맵)")

with st.container():
    # 1. 요일 이름 매핑 (월요일~일요일 순서 정렬)
    day_names = ["월", "화", "수", "목", "금", "토", "일"]
    daily_top10_sum["요일_num"] = daily_top10_sum["기준일자"].dt.dayofweek
    daily_top10_sum["요일"] = daily_top10_sum["요일_num"].map(lambda x: day_names[x])

    # 2. 마우스 오버 시 표시할 yyyy-mm-dd 날짜 문자열 생성
    daily_top10_sum["날짜"] = daily_top10_sum["기준일자"].dt.strftime("%Y-%m-%d")

    # 3. Y축 기준인 연도 및 주차(Week number) 계산
    daily_top10_sum["주차"] = daily_top10_sum["기준일자"].dt.strftime("%Y년 %W주차")

    # 4. Plotly 히트맵 생성 (color_continuous_scale="Reds"로 관객이 많을수록 진한 색 적용)
    fig_heatmap = px.density_heatmap(
        daily_top10_sum,
        x="요일",
        y="주차",
        z="일별관객수합계",
        category_orders={"요일": day_names},  # 월요일부터 일요일까지 순서 고정
        color_continuous_scale="Reds",  # 관객수가 많을수록 진한 붉은색
        labels={
            "요일": "요일",
            "주차": "주차",
            "일별관객수합계": "관객수(명)",
            "날짜": "기준일자",
        },
        hover_data={"날짜": True, "요일": True, "주차": True, "일별관객수합계": ":,d"},
        title="주차 및 요일별 일관객 수 분포",
    )

    # 레이아웃 정밀 설정 (Y축 반전하여 최신 주차가 위로 올라오도록 세팅)
    fig_heatmap.update_layout(
        yaxis_autorange="reversed",
        coloraxis_colorbar_title="관객수(명)",
    )

    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # 그래프 하단 설명 공간
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 특정 주차의 요일별 관객 집중 현상과 연휴/성수기 시즌 극장 방문 패턴을 한눈에 시각적으로 감지할 수 있습니다."
    )
