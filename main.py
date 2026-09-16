# ---------------------------------------------------------
# 그래프 5: 영화 10편 이상 장르별 총 관객 수 분포 (박스플롯)
# ---------------------------------------------------------
st.subheader("5. 영화 10편 이상 장르별 총 관객 수 분포 (박스플롯)")

# 1. 영화 편수가 10편 이상인 장르 필터링
genre_counts_g5 = filtered_df['main_genre'].value_counts()
target_genres = genre_counts_g5[genre_counts_g5 >= 10].index
df_box_g5 = filtered_df[filtered_df['main_genre'].isin(target_genres)]

if not df_box_g5.empty:
    # 2. 박스플롯 생성 (outliers 및 hover_name 설정)
    fig_box_audi = px.box(
        df_box_g5,
        x='main_genre',
        y='total_audi',
        color='main_genre',
        hover_name='movieNm',  # 마우스 호버 시 영화명 표시
        points='outliers',     # 상자 밖의 이상치 점만 표시
        labels={
            'main_genre': '장르',
            'total_audi': '총 관객 수 (명)'
        }
    )

    # 3. 호버 툴팁 포맷팅
    fig_box_audi.update_traces(
        hovertemplate="<b>영화명: %{hovertext}</b><br>장르: %{x}<br>총 관객 수: %{y:,.0f}명<extra></extra>"
    )

    # 4. 레이아웃 설정
    fig_box_audi.update_layout(
        height=500,
        showlegend=False,
        margin=dict(t=30, b=30, l=10, r=10),
        yaxis=dict(tickformat=",")
    )

    st.plotly_chart(fig_box_audi, use_container_width=True)

    # 5. 인사이트 설명 상자
    st.markdown("""
    <div class="insight-box">
        <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
        영화가 10편 이상 등록된 주요 장르별로 총 관객 수의 중앙값과 범주를 한눈에 비교할 수 있습니다. 상자 밖으로 튀어나온 이상치 점에 마우스를 올리면 평균적인 흥행 범주를 뛰어넘어 대흥행을 기록한 개별 영화명을 확인할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("현재 필터 조건 내에 영화 편수가 10편 이상인 장르가 없습니다.")
