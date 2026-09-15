import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# 페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS 스타일링 (그래프 하단 '알 수 있는 것' 구역 강조)
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .insight-box {
        background-color: #F0F9FF;
        border-left: 5px solid #0284C7;
        padding: 12px 16px;
        border-radius: 4px;
        margin-top: 10px;
        margin-bottom: 25px;
        font-size: 0.95rem;
        color: #0F172A;
    }
    .insight-title {
        font-weight: bold;
        color: #0369A1;
        margin-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 데이터 로드 및 전처리
# ---------------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    
    # 1. 장르 전처리: '|' 구분자로 여러 개 적힌 영화는 첫 번째 장르만 취함
    df['main_genre'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0].strip())
    
    # 2. 수치형 컬럼 보정
    numeric_cols = ['first_scrn', 'first_show', 'first_week_audi', 'total_audi', 'days_in_top10']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

df = load_data()

# ---------------------------------------------------------
# 헤더 영역
# ---------------------------------------------------------
st.markdown('<div class="main-header">🎬 영화 데이터 그래프 - 분포와 관계</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">KOBIS 1년간 박스오피스 Top 10 영화 216편의 장르 분포 및 주요 흥행 지표 관계 분석</div>', unsafe_allow_html=True)
st.divider()

# ---------------------------------------------------------
# 사이드바 (필터링)
# ---------------------------------------------------------
st.sidebar.header("🔍 데이터 필터")

# 장르 선택
all_genres = sorted(df['main_genre'].unique().tolist())
selected_genres = st.sidebar.multiselect(
    "장르 선택",
    options=all_genres,
    default=all_genres
)

# 제작 국가 선택
all_nations = sorted(df['nation'].dropna().unique().tolist())
selected_nations = st.sidebar.multiselect(
    "제작 국가 선택",
    options=all_nations,
    default=all_nations
)

# 필터 적용
filtered_df = df[
    (df['main_genre'].isin(selected_genres)) &
    (df['nation'].isin(selected_nations))
]

st.sidebar.divider()
st.sidebar.markdown(f"**📊 현재 표시 데이터:** `{len(filtered_df)}` / `{len(df)}` 편")

# ---------------------------------------------------------
# 주요 지표 (Metric Cards)
# ---------------------------------------------------------
if not filtered_df.empty:
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("분석 영화 수", f"{len(filtered_df):,} 편")
    with m2:
        st.metric("평균 총 관객 수", f"{int(filtered_df['total_audi'].mean()):,} 명")
    with m3:
        st.metric("최대 스크린 수", f"{int(filtered_df['first_scrn'].max()):,} 개")
    with m4:
        st.metric("평균 Top10 유지일수", f"{filtered_df['days_in_top10'].mean():.1f} 일")
st.divider()

if filtered_df.empty:
    st.warning("선택한 조건에 해당하는 영화 데이터가 없습니다. 필터를 변경해 주세요.")
    st.stop()

# ---------------------------------------------------------
# 그래프 1: 장르별 영화 편수 (Plotly 도넛 그래프)
# ---------------------------------------------------------
st.subheader("1. 장르별 영화 편수 분포 (도넛 그래프)")

genre_counts = filtered_df['main_genre'].value_counts().reset_index()
genre_counts.columns = ['장르', '편수']

fig_donut = px.pie(
    genre_counts,
    names='장르',
    values='편수',
    hole=0.45,
    color_discrete_sequence=px.colors.qualitative.Pastel
)

# 툴팁에 마우스를 올리면 편수와 비율이 보이도록 설정
fig_donut.update_traces(
    textinfo='percent+label',
    hovertemplate='<b>장르: %{label}</b><br>영화 편수: %{value}편<br>비율: %{percent:.1%}<extra></extra>'
)

fig_donut.update_layout(
    margin=dict(t=30, b=30, l=10, r=10),
    height=450,
    legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
)

st.plotly_chart(fig_donut, use_container_width=True)

# 그래프 설명 및 구역 구분
st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    개봉 영화 시장에서 특정 주요 장르(예: 드라마, 액션, 애니메이션 등)의 편수 비중이 대다수를 차지하며, 어떤 장르가 시장 공급의 중심인지를 직관적으로 파악할 수 있습니다.
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 그래프 2: 개봉일 스크린 수 vs 총 관객 수 (관계 산점도)
# ---------------------------------------------------------
st.subheader("2. 개봉일 스크린 수와 총 관객 수의 관계")

fig_scatter_scrn = px.scatter(
    filtered_df,
    x='first_scrn',
    y='total_audi',
    color='main_genre',
    size='days_in_top10',
    hover_name='movieNm',
    hover_data={
        'first_scrn': ':,f',
        'total_audi': ':,f',
        'days_in_top10': True,
        'main_genre': False
    },
    labels={
        'first_scrn': '개봉일 스크린 수 (개)',
        'total_audi': '총 관객 수 (명)',
        'main_genre': '장르',
        'days_in_top10': 'Top 10 유지일수'
    },
    opacity=0.8,
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig_scatter_scrn.update_layout(
    height=500,
    margin=dict(t=30, b=30, l=10, r=10),
    xaxis=dict(tickformat=","),
    yaxis=dict(tickformat=",")
)

st.plotly_chart(fig_scatter_scrn, use_container_width=True)

# 그래프 설명 및 구역 구분
st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    개봉 초기에 확보한 스크린 수가 많을수록 최종 총 관객 수가 증가하는 뚜렷한 양의 상관관계를 보이며, 초기 상영관 점유율이 영화 흥행 규모의 주요한 결정 요인임을 나타냅니다.
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 그래프 3: 개봉 첫 주 관객 수 vs 총 관객 수 (상관관계)
# ---------------------------------------------------------
st.subheader("3. 개봉 첫 주 관객 수와 총 관객 수의 상관관계")

fig_scatter_week = px.scatter(
    filtered_df,
    x='first_week_audi',
    y='total_audi',
    color='nation',
    hover_name='movieNm',
    trendline='ols',
    trendline_color_override='red',
    hover_data={
        'first_week_audi': ':,f',
        'total_audi': ':,f',
        'nation': True
    },
    labels={
        'first_week_audi': '개봉 첫 주 관객 수 (명)',
        'total_audi': '총 관객 수 (명)',
        'nation': '제작 국가'
    },
    opacity=0.75
)

fig_scatter_week.update_layout(
    height=500,
    margin=dict(t=30, b=30, l=10, r=10),
    xaxis=dict(tickformat=","),
    yaxis=dict(tickformat=",")
)

st.plotly_chart(fig_scatter_week, use_container_width=True)

# 그래프 설명 및 구역 구분
st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    개봉 첫 주 관객 수가 전체 흥행 성적(총 관객 수)과 매우 강한 선형적 관계를 이루고 있어, 초기 흥행 성패가 최종 성적에 결정적인 영향을 미침을 보여줍니다.
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 그래프 4: 장르별 Top 10 머문 날수 분포 (박스플롯)
# ---------------------------------------------------------
st.subheader("4. 장르별 Top 10 랭킹 유지 기간(일수) 분포")

fig_box = px.box(
    filtered_df,
    x='main_genre',
    y='days_in_top10',
    color='main_genre',
    points='all',
    hover_name='movieNm',
    labels={
        'main_genre': '장르',
        'days_in_top10': 'Top 10 머문 날수 (일)'
    }
)

fig_box.update_layout(
    height=450,
    showlegend=False,
    margin=dict(t=30, b=30, l=10, r=10)
)

st.plotly_chart(fig_box, use_container_width=True)

# 그래프 설명 및 구역 구분
st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    장르에 따라 상위권 랭킹(Top 10)에 장기간 지속적으로 머무르는 영화와 초기에 빠르게 진입 및 퇴출되는 영화 간의 생존 기간 차이를 비교 분석할 수 있습니다.
</div>
""", unsafe_allow_html=True)
