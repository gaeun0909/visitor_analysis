import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="외국인 방문객 분석", layout="wide")
st.title("📊 2025년 외국인 방문객 특성과 입국 흐름 분석")
st.markdown("---")

# 2. 데이터베이스 연결 확인 (에러 핸들링)
db_file = 'visitor.db'

if not os.path.exists(db_file):
    st.error(f"⚠️ '{db_file}' 파일을 찾을 수 없습니다! 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요.")
    st.stop()

def run_query(query):
    """SQL 쿼리를 실행하여 판다스 데이터프레임으로 반환하는 함수"""
    with sqlite3.connect(db_file) as conn:
        return pd.read_sql(query, conn)

# ---------------------------------------------------------
# [분석 질문 1] 연령층 분석 (Combo Chart)
# ---------------------------------------------------------
st.header("Q1. 외국인 방문객은 어느 대륙에서 많이 왔고, 그중 20~30대 비중은 어떻게 다를까?")

sql1 = """
SELECT 대륙, 소계, 
       (연령_0_9세 + 연령_10_19세 + 연령_20_29세) as 젊은층_합계
FROM age 
WHERE 대륙 != '계'
ORDER BY 소계 DESC
"""
df1 = run_query(sql1)
df1['젊은층_비중'] = (df1['젊은층_합계'] / df1['소계']) * 100

# 시각화 (콤보 차트: 막대 + 라인)
fig1 = go.Figure()
fig1.add_trace(go.Bar(x=df1['대륙'], y=df1['소계'], name='전체 방문객', marker_color='skyblue'))
fig1.add_trace(go.Scatter(x=df1['대륙'], y=df1['젊은층_비중'], name='젊은층 비중(%)', yaxis='y2', line=dict(color='red', width=3)))

fig1.update_layout(
    yaxis=dict(title="방문객 수 (명)"),
    yaxis2=dict(title="젊은층 비중 (%)", overlaying='y', side='right'),
    legend=dict(x=1.1, y=1.1)
)
st.plotly_chart(fig1, use_container_width=True)

with st.expander("사용한 SQL 보기"):
    st.code(sql1, language='sql')

st.info("""
**💡 인사이트**
1. 아시아 대륙의 방문객 수가 압도적으로 많으며, 다른 대륙에 비해 젊은 층(0~29세)의 방문 비중이 높게 나타납니다.
2. 구주(유럽)나 미주 지역은 방문객 수는 적지만 젊은 층 비중이 일정 수준 유지되어 교육이나 문화 체험 목적의 방문을 유추할 수 있습니다.
""")


# ---------------------------------------------------------
# [분석 질문 2] 방문 목적 분석 (Stacked Bar Chart)
# ---------------------------------------------------------
st.markdown("---")
st.header("Q2. 대륙별로 한국을 방문하는 목적은 어떻게 다를까?")

sql2 = "SELECT 대륙, 관광, 상용, 공용, 유학_연수, 기타 FROM purpose WHERE 대륙 != '계'"
df2 = run_query(sql2)

# 시각화 (누적 막대 그래프)
fig2 = px.bar(df2, x='대륙', y=['관광', '상용', '공용', '유학_연수', '기타'], 
             title="대륙별 방문 목적 분포",
             labels={'value': '방문객 수', 'variable': '방문 목적'},
             barmode='stack')
st.plotly_chart(fig2, use_container_width=True)

with st.expander("사용한 SQL 보기"):
    st.code(sql2, language='sql')

st.info("""
**💡 인사이트**
1. 모든 대륙에서 '관광' 목적의 방문이 가장 큰 비중을 차지하고 있습니다.
2. 아시아권은 '유학_연수' 비중이 타 대륙 대비 높으며, 미주와 구주는 '상용' 목적의 비중이 상대적으로 높게 나타납니다.
""")


# ---------------------------------------------------------
# [분석 질문 3] 입국 경로 분석 (Grouped Bar Chart)
# ---------------------------------------------------------
st.markdown("---")
st.header("Q3. 외국인 방문객은 어떤 입국 경로에 집중되어 있으며, 공항 의존도는 어떠할까?")

sql3 = "SELECT 대륙, 공항_소계, 항구_소계 FROM transport WHERE 대륙 != '계'"
df3 = run_query(sql3)
df3['공항_비중'] = (df3['공항_소계'] / (df3['공항_소계'] + df3['항구_소계'])) * 100

# 시각화 (막대 그래프)
fig3 = px.bar(df3, x='대륙', y=['공항_소계', '항구_소계'], 
             title="공항 vs 항구 입국자수 비교",
             barmode='group',
             color_discrete_sequence=['#636EFA', '#EF553B'])
st.plotly_chart(fig3, use_container_width=True)

with st.expander("사용한 SQL 보기"):
    st.code(sql3, language='sql')

st.info("""
**💡 인사이트**
1. 대다수의 대륙에서 공항을 통한 입국이 90% 이상을 차지하여 항공 교통 의존도가 매우 높습니다.
2. 일본이나 중국 등 인접 국가의 경우, 다른 대륙에 비해 항구(부산, 인천 등)를 통한 입국 비중이 유의미하게 관찰됩니다.
""")

st.markdown("---")
st.caption("2025 외국인 방문객 데이터 분석 대시보드 | 시니어 개발자 멘토링")
