# ---------------------------------------------------------
# 그래프 6: 개봉일 스크린 수, 첫 주 관객 수 및 총 관객 수 (버블 차트)
# ---------------------------------------------------------
st.subheader("6. 개봉일 스크린 수, 첫 주 관객 수 및 총 관객 수 (버블 차트)")

fig_bubble = px.scatter(
    filtered_df,
    x='first_scrn',
    y='total_audi',
    size='first_week_audi',        # 첫 주 관객 수를 버블 크기로 설정
    size_max=45,                   # 버블 최대 크기 조절
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
    개봉일 스크린 수(X축)와 최종 총 관객 수(Y축)의 관계 외에도 <b>버블의 크기(첫 주 관객 수)</b>를 통해 초반 흥행 몰이 속도를 한눈에 비교할 수 있습니다. 버블이 크고 위쪽에 위치한 영화는 개봉 첫 주부터 강력한 관객 동원력을 발휘한 작품입니다.
</div>
""", unsafe_allow_html=True)
