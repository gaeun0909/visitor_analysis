import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# 1. 페이지 설정
st.set_page_config(page_title="외국인 방문객 분석", layout="wide")

# 2. 데이터베이스 연결 확인
db_path = 'visitor.db'

if not os.path.exists(db_path):
    st.error(f"🚨 '{db_path}' 파일을 찾을 수 없습니다. 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요!")
    st.stop()

def run_query(q):
    """SQL 쿼리를 실행하여 판다스 데이터프레임으로 반환하는 함수"""
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql(q, conn)

# 헤더 부분
st.title("📊 2025년 외국인 방문객 특성과 입국 흐름 분석")
st.markdown("---")

# --- [분석 질문 1] ---
st.subheader("🔍 1. 어느 대륙에서 많이 왔고, 2030세대 비중은 어떠할까?")

sql1 = """
SELECT 대륙, 소계, 
       (연령_20_29세 + 연령_30_39세) as 연령_2030_계,
       CAST((연령_20_29세 + 연령_30_39세) AS FLOAT) / 소계 * 100 as 비중_2030
FROM age
WHERE 대륙 != '계'
ORDER BY 소계 DESC
"""
df1 = run_query(sql1)

# 시각화: 콤보 차트 (막대 + 라인)
fig1 = go.Figure()
# 막대 그래프 (방문객 수)
fig1.add_trace(go.Bar(x=df1['대륙'], y=df1['소계'], name='전체 방문객 수', marker_color='skyblue'))
# 라인 그래프 (2030 비중) - 보조축 사용
fig1.add_trace(go.Scatter(x=df1['대륙'], y=df1['비중_2030'], name='2030 비중(%)', 
                         yaxis='y2', line=dict(color='orange', width=3)))

fig1.update_layout(
    title='대륙별 방문객 수 및 2030세대 비중',
    yaxis=dict(title='방문객 수 (명)'),
    yaxis2=dict(title='2030 비중 (%)', overlaying='y', side='right'),
    legend=dict(x=1.1, y=1)
)
st.plotly_chart(fig1, use_container_width=True)

st.info("**[사용한 SQL]**\n```sql\n" + sql1 + "\n```")
st.write("**💡 인사이트:**")
st.write("- 전체 방문객 수는 특정 대륙(예: 아시아)이 압도적으로 높을 수 있으나, 2030 세대의 '비중'은 대륙별로 차이가 납니다.")
st.write("- 비중이 높은 대륙을 타겟으로 한 SNS 마케팅 전략이 유효할 것으로 보입니다.")


# --- [분석 질문 2] ---
st.markdown("---")
st.subheader("🔍 2. 외국인 방문객은 어떤 목적으로 한국을 방문했을까?")

sql2 = "SELECT 대륙, 관광, 상용, 공용, 유학_연수, 기타 FROM purpose WHERE 대륙 != '계'"
df2 = run_query(sql2)

# 시각화: 누적 막대그래프 (Wide form to Long form for Plotly)
df2_melted = df2.melt(id_vars='대륙', var_name='방문목적', value_name='인원수')
fig2 = px.bar(df2_melted, x='대륙', y='인원수', color='방문목적', 
             title='대륙별 방문 목적 분포', barmode='stack')

st.plotly_chart(fig2, use_container_width=True)

st.info("**[사용한 SQL]**\n```sql\n" + sql2 + "\n```")
st.write("**💡 인사이트:**")
st.write("- 대부분의 대륙에서 '관광' 목적이 가장 큰 비중을 차지하고 있음을 알 수 있습니다.")
st.write("- 특정 대륙에서 '유학_연수'나 '상용' 목적의 비중이 높다면 해당 국가와의 비즈니스/교육 교류 특성을 반영합니다.")


# --- [분석 질문 3] ---
st.markdown("---")
st.subheader("🔍 3. 대륙별 공항 vs 항구 입국 경로 분석")

sql3 = "SELECT 대륙, 공항_소계, 항구_소계 FROM transport WHERE 대륙 != '계'"
df3 = run_query(sql3)

# 시각화: 그룹 막대그래프
fig3 = px.bar(df3, x='대륙', y=['공항_소계', '항구_소계'], 
             title='대륙별 주요 입국 경로 비교', barmode='group',
             labels={'value': '인원수', 'variable': '입국경로'})

st.plotly_chart(fig3, use_container_width=True)

st.info("**[사용한 SQL]**\n```sql\n" + sql3 + "\n```")
st.write("**💡 인사이트:**")
st.write("- 모든 대륙에서 공항을 통한 입국이 압도적이지만, 지리적으로 가까운 대륙은 항구 이용객도 유의미하게 존재합니다.")
st.write("- 항구 입국자가 많은 지역을 대상으로 크루즈 관광 상품이나 항구 환영 행사를 기획할 수 있습니다.")
