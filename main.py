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
