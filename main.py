import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# 페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 분석 - 종합 시각화",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS 스타일링
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
    # 장르 전처리: '|' 구분자로 여러 개 적힌 영화는 첫 번째 장르만 취함
    df['main_genre'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0].strip())
    # 수치형 데이터 안전 변환
    numeric_cols = ['first_scrn', 'first_show', 'first_week_audi', 'total_audi', 'days_in_top10']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df = load_data()

# ---------------------------------------------------------
# 헤더 영역
# ---------------------------------------------------------
st.markdown('<div class="main-header">🎬 영화 데이터 분석 - 종합 시각화</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">KOBIS 1년간 박스오피스 Top 10 영화 216편의 분포 및 지표 간 관계 분석</div>', unsafe_allow_html=True)
st.divider()

# ---------------------------------------------------------
# 사이드바 (필터링)
# ---------------------------------------------------------
st.sidebar.header("🔍 데이터 필터")

all_genres = sorted(df['main_genre'].unique().tolist())
selected_genres = st.sidebar.multiselect("장르 선택", options=all_genres, default=all_genres)

all_nations = sorted(df['nation'].dropna().unique().tolist())
selected_nations = st.sidebar.multiselect("제작 국가 선택", options=all_nations, default=all_nations)

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
        st.metric("총 분석 영화 수", f"{len(filtered_df):,} 편")
    with m2:
        st.metric("평균 총 관객 수", f"{int(filtered_df['total_audi'].mean()):,} 명")
    with m3:
        st.metric("최대 스크린 수", f"{int(filtered_df['first_scrn'].max()):,} 개")
    with m4:
        st.metric("평균 Top10 유지일수", f"{filtered_df['days_in_top10'].mean():.1f} 일")
st.divider()

if filtered_df.empty:
    st.warning("선택한 조건에 해당하는 영화 데이터가 없습니다. 필터를 조정해 주세요.")
    st.stop()

# ---------------------------------------------------------
# 그래프 1: 장르별 영화 편수 (도넛 그래프)
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

st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    개봉 영화 시장에서 특정 주요 장르(예: 드라마, 액션, 애니메이션 등)의 편수 비중이 대다수를 차지하며, 어떤 장르가 시장 공급의 중심인지를 명확히 파악할 수 있습니다.
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 그래프 2: 장르 및 영화별 총 관객 수 (트리맵)
# ---------------------------------------------------------
st.subheader("2. 장르별 영화 총 관객 수 분포 (트리맵)")

fig_treemap = px.treemap(
    filtered_df,
    path=[px.Constant("전체 장르"), 'main_genre', 'movieNm'],
    values='total_audi',
    color='main_genre',
    color_discrete_sequence=px.colors.qualitative.Set3
)

fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객 수: %{value:,.0f}명<extra></extra>"
)

fig_treemap.update_layout(
    margin=dict(t=30, b=30, l=10, r=10),
    height=550
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    장르별 전체 관객 점유율 규모와 더불어, 해당 장르 내에서 어떤 특정 영화가 대흥행을 이끌어 전체 관객 수 지분을 차지했는지 한눈에 비교할 수 있습니다.
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 그래프 3: 총 관객 수 분포 (히스토그램)
# ---------------------------------------------------------
st.subheader("3. 총 관객 수 분포 (히스토그램)")

fig_hist = px.histogram(
    filtered_df,
    x='total_audi',
    nbins=25,
    labels={'total_audi': '총 관객 수 (명)', 'count': '영화 편수'},
    color_discrete_sequence=['#0284C7']
)

fig_hist.update_traces(
    hovertemplate="<b>관객 수 구간: %{x}</b><br>영화 편수: %{y}편<extra></extra>"
)

fig_hist.update_layout(
    margin=dict(t=30, b=30, l=10, r=10),
    height=450,
    yaxis_title="영화 편수 (개)",
    xaxis=dict(tickformat=",")
)

st.plotly_chart(fig_hist, use_container_width=True)

top_movie_idx = filtered_df['total_audi'].idxmax()
top_movie_name = filtered_df.loc[top_movie_idx, 'movieNm']
top_movie_audi = int(filtered_df.loc[top_movie_idx, 'total_audi'])

under_2m_cnt = len(filtered_df[filtered_df['total_audi'] < 2000000])
under_2m_pct = (under_2m_cnt / len(filtered_df)) * 100

st.markdown(f"""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    대부분의 영화({under_2m_pct:.1f}%, 총 {under_2m_cnt}편)가 <b>총 관객 수 200만 명 미만</b>의 하위 구간에 빽빽하게 집중되어 있으며, 가장 많은 관객을 동원한 최흥행작은 <b>'{top_movie_name}'</b> (총 {top_movie_audi:,}명)입니다.
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 그래프 4: 개봉일 스크린 수 vs 총 관객 수 (산점도)
# ---------------------------------------------------------
st.subheader("4. 개봉일 스크린 수와 총 관객 수의 산점도")

fig_scatter_scrn = px.scatter(
    filtered_df,
    x='first_scrn',
    y='total_audi',
    color='main_genre',
    hover_name='movieNm',
    hover_data={
        'first_scrn': ':,f',
        'total_audi': ':,f',
        'main_genre': True
    },
    labels={
        'first_scrn': '개봉일 스크린 수 (개)',
        'total_audi': '총 관객 수 (명)',
        'main_genre': '장르'
    },
    opacity=0.8,
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig_scatter_scrn.update_traces(
    marker=dict(size=10),
    hovertemplate="<b>영화명: %{hovertext}</b><br>장르: %{customdata[2]}<br>개봉일 스크린 수: %{x:,.0f}개<br>총 관객 수: %{y:,.0f}명<extra></extra>"
)

fig_scatter_scrn.update_layout(
    height=500,
    margin=dict(t=30, b=30, l=10, r=10),
    xaxis=dict(tickformat=","),
    yaxis=dict(tickformat=","),
    legend_title_text='장르'
)

st.plotly_chart(fig_scatter_scrn, use_container_width=True)

st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    개봉 초기에 확보한 스크린 수(first_scrn)가 많을수록 최종 총 관객 수(total_audi)가 증가하는 뚜렷한 양의 관계를 확인할 수 있습니다.
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 그래프 5: 영화 10편 이상 장르별 총 관객 수 분포 (박스플롯)
# ---------------------------------------------------------
st.subheader("5. 영화 10편 이상 장르별 총 관객 수 분포 (박스플롯)")

genre_counts_g5 = filtered_df['main_genre'].value_counts()
target_genres = genre_counts_g5[genre_counts_g5 >= 10].index
df_box_g5 = filtered_df[filtered_df['main_genre'].isin(target_genres)]

if not df_box_g5.empty:
    fig_box_audi = px.box(
        df_box_g5,
        x='main_genre',
        y='total_audi',
        color='main_genre',
        hover_name='movieNm',
        points='outliers',
        labels={
            'main_genre': '장르',
            'total_audi': '총 관객 수 (명)'
        }
    )

    fig_box_audi.update_traces(
        hovertemplate="<b>영화명: %{hovertext}</b><br>장르: %{x}<br>총 관객 수: %{y:,.0f}명<extra></extra>"
    )

    fig_box_audi.update_layout(
        height=500,
        showlegend=False,
        margin=dict(t=30, b=30, l=10, r=10),
        yaxis=dict(tickformat=",")
    )

    st.plotly_chart(fig_box_audi, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
        <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
        영화가 10편 이상 수집된 주요 장르별로 총 관객 수의 박스플롯 분포를 한눈에 볼 수 있습니다. 상자 외부로 벗어난 이상치 점에 마우스를 올려놓으면 평균적인 범주를 훌쩍 넘어서서 대흥행을 이뤄낸 특정 영화명을 바로 확인할 수 있습니다.
    </div>
""", unsafe_allow_html=True)
else:
    st.info("선택한 조건 내에 영화 편수가 10편 이상인 장르가 존재하지 않습니다.")

st.divider()

# ---------------------------------------------------------
# 그래프 6: 개봉일 스크린 수, 첫 주 관객 수 및 총 관객 수 (버블 차트)
# ---------------------------------------------------------
st.subheader("6. 개봉일 스크린 수, 첫 주 관객 수 및 총 관객 수 (버블 차트)")

fig_bubble = px.scatter(
    filtered_df,
    x='first_scrn',
    y='total_audi',
    size='first_week_audi',
    size_max=45,
    color='main_genre',
    hover_name='movieNm',
    hover_data={
        'first_scrn': ':,f',
        'total_audi': ':,f',
        'first_week_audi': ':,f',
        'main_genre': True
    },
    labels={
        'first_scrn': '개봉일 스크린 수 (개)',
        'total_audi': '총 관객 수 (명)',
        'first_week_audi': '첫 주 관객 수 (명)',
        'main_genre': '장르'
    },
    opacity=0.7,
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig_bubble.update_traces(
    hovertemplate="<b>영화명: %{hovertext}</b><br>장르: %{customdata[3]}<br>개봉일 스크린 수: %{x:,.0f}개<br>첫 주 관객 수: %{marker.size:,.0f}명<br>총 관객 수: %{y:,.0f}명<extra></extra>"
)

fig_bubble.update_layout(
    height=550,
    margin=dict(t=30, b=30, l=10, r=10),
    xaxis=dict(tickformat=","),
    yaxis=dict(tickformat=","),
    legend_title_text='장르'
)

st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    개봉일 스크린 수(X축)와 최종 총 관객 수(Y축)의 관계 외에도 <b>버블의 크기(첫 주 관객 수)</b>를 통해 초반 흥행 몰이 속도를 한눈에 비교할 수 있습니다.
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 그래프 7: 제작 국가 및 장르별 영화 편수 (선버스트 차트)
# ---------------------------------------------------------
st.subheader("7. 제작 국가 및 장르별 영화 편수 (선버스트 차트)")

fig_sunburst = px.sunburst(
    filtered_df,
    path=['nation', 'main_genre'],
    color='nation',
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig_sunburst.update_traces(
    textinfo='label+percent entry',
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<extra></extra>"
)

fig_sunburst.update_layout(
    height=550,
    margin=dict(t=30, b=30, l=10, r=10)
)

st.plotly_chart(fig_sunburst, use_container_width=True)

st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    안쪽 링의 제작 국가(`nation`)에서 바깥쪽 링의 장르(`main_genre`)로 이어지는 계층 구조를 통해 각 국가별로 어떤 장르의 영화가 주로 제작·수집되었는지 영화 편수 비율을 한눈에 비교할 수 있습니다.
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 그래프 8: 전체 흥행 Top 10 영화의 장르 분포 및 총 관객 수 (선버스트 차트)
# ---------------------------------------------------------
st.subheader("8. 전체 관객 수 Top 10 흥행작의 장르 분포 및 관객 수 (선버스트 차트)")

# 전체 관객 수 기준 상위 10개 흥행 영화 추출
top10_overall = filtered_df.nlargest(10, 'total_audi')

fig_sunburst_top10_overall = px.sunburst(
    top10_overall,
    path=['main_genre', 'movieNm'],
    values='total_audi',
    color='main_genre',
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig_sunburst_top10_overall.update_traces(
    textinfo='label+percent entry',
    hovertemplate="<b>%{label}</b><br>총 관객 수: %{value:,.0f}명<extra></extra>"
)

fig_sunburst_top10_overall.update_layout(
    height=550,
    margin=dict(t=30, b=30, l=10, r=10)
)

st.plotly_chart(fig_sunburst_top10_overall, use_container_width=True)

st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    전체 관객 수 기준 <b>흥행 Top 10 영화</b>들이 어떤 장르로 구성되어 있는지 비율을 한눈에 파악할 수 있습니다. 안쪽 링의 장르 영역이나 바깥쪽 링의 영화에 마우스를 올리면 각 장르 및 개별 영화의 <b>총 관객 수</b>를 즉시 확인할 수 있습니다.
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 그래프 9: 장르별 Top 10 머문 날수 분포 (박스플롯)
# ---------------------------------------------------------
st.subheader("9. 장르별 Top 10 랭킹 유지 기간(일수) 분포")

fig_box = px.box(
    filtered_df,
    x='main_genre',
    y='days_in_top10',
    color='main_genre',
    points='all',
    hover_name='movieNm',
    labels={'main_genre': '장르', 'days_in_top10': 'Top 10 머문 날수 (일)'}
)

fig_box.update_layout(height=450, showlegend=False, margin=dict(t=30, b=30, l=10, r=10))
st.plotly_chart(fig_box, use_container_width=True)

st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    장르에 따라 상위권 랭킹(Top 10)에 장기간 지속적으로 머무르는 영화와 초기에 빠르게 진입 및 퇴출되는 영화 간의 생존 기간 차이를 비교 분석할 수 있습니다.
</div>
""", unsafe_allow_html=True)
