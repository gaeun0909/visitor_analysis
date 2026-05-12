import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="외국인 방문객 분석", layout="wide")

st.title("📊 2025년 외국인 방문객 특성과 입국 흐름 분석")
st.markdown("---")

# 2. 데이터베이스 연결 확인 (에러 핸들링)
db_path = 'visitor.db'

if not os.path.exists(db_path):
    st.error(f"⚠️ '{db_path}' 파일을 찾을 수 없습니다. 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요.")
    st.stop()

def run_query(query):
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn)

# ---------------------------------------------------------
# [분석 질문 1] 대륙별 방문객 수와 젊은 층 비중
# ---------------------------------------------------------
st.header("Q1. 외국인 방문객은 어느 대륙에서 많이 왔고, 그중 젊은 층 비중은 어떻게 다를까?")

query1 = "SELECT * FROM age"
df_age = run_query(query1)

# 데이터 가공: 젊은 층(20-29세) 비중 계산
df_age['젊은층_비중'] = (df_age['연령_20_29세'] / df_age['소계']) * 100

# 콤보 차트 구성 (Plotly 사용)
fig1 = go.Figure()

# 막대 그래프: 전체 방문객 수
fig1.add_trace(go.Bar(
    x=df_age['대륙'], y=df_age['소계'], name='전체 방문객 수',
    marker_color='skyblue', yaxis='y1'
))

# 라인 그래프: 20대 비중
fig1.add_trace(go.Scatter(
    x=df_age['대륙'], y=df_age['젊은층_비중'], name='20대 비중(%)',
    line=dict(color='red', width=3), yaxis='y2'
))

fig1.update_layout(
    title="대륙별 총 방문객 및 20대 비중",
    yaxis=dict(title="방문객 수 (명)"),
    yaxis2=dict(title="비중 (%)", overlaying='y', side='right'),
    legend=dict(x=1.1, y=1)
)

st.plotly_chart(fig1, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(query1, language='sql')
    st.write("💡 **인사이트**")
    st.write("- 특정 대륙(예: 아시아)의 방문객 수가 압도적으로 많지만, 젊은 층의 비중은 유럽이나 미주 지역에서 더 높게 나타날 수 있습니다.")
    st.write("- 20대 비중이 높은 대륙을 타겟으로 한 소셜 미디어 마케팅이 효과적일 것입니다.")


# ---------------------------------------------------------
# [분석 질문 2] 대륙별 방문 목적
# ---------------------------------------------------------
st.markdown("---")
st.header("Q2. 대륙별로 한국을 방문하는 목적은 어떻게 다를까?")

query2 = "SELECT * FROM purpose"
df_purpose = run_query(query2)

# 시각화를 위한 데이터 재구성 (Melt)
purpose_cols = ['관광', '상용', '공용', '유학_연수', '기타']
df_purpose_melted = df_purpose.melt(id_vars=['대륙'], value_vars=purpose_cols, var_name='방문목적', value_name='방문객수')

fig2 = px.bar(df_purpose_melted, x='대륙', y='방문객수', color='방문목적',
             title="대륙별 방문 목적 누적 막대그래프",
             barmode='stack')

st.plotly_chart(fig2, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(query2, language='sql')
    st.write("💡 **인사이트**")
    st.write("- 대부분의 대륙에서 '관광' 목적이 가장 크지만, 특정 대륙은 '상용(비즈니스)'이나 '유학_연수'의 비중이 상대적으로 높습니다.")
    st.write("- 목적별 맞춤형 관광 상품(예: 비즈니스 트래블러를 위한 워케이션 등) 기획의 기초 자료로 활용 가능합니다.")


# ---------------------------------------------------------
# [분석 질문 3] 입국 경로 및 공항 의존도
# ---------------------------------------------------------
st.markdown("---")
st.header("Q3. 외국인 방문객은 어떤 입국 경로에 집중되어 있으며, 공항 의존도는 어떠할까?")

query3 = "SELECT * FROM transport"
df_trans = run_query(query3)

col1, col2 = st.columns(2)

with col1:
    # 1. 주요 지점별 방문객 수 (막대그래프)
    entry_points = {
        '공항_인천': '인천공항', '공항_김해': '김해공항', '공항_김포': '김포공항', 
        '공항_제주': '제주공항', '공항_기타': '기타공항', '항구_부산': '부산항', 
        '항구_인천': '인천항', '항구_제주': '제주항', '항구_기타': '기타항구'
    }
    
    df_entry = df_trans[list(entry_points.keys())].sum().reset_index()
    df_entry.columns = ['entry_point', 'visitor_count']
    df_entry['entry_point'] = df_entry['entry_point'].map(entry_points)
    
    fig3_1 = px.bar(df_entry, x='entry_point', y='visitor_count', 
                   title="주요 입국 지점별 총 방문객",
                   color='visitor_count', color_continuous_scale='Viridis')
    st.plotly_chart(fig3_1, use_container_width=True)

with col2:
    # 2. 대륙별 공항/항구 비율 (누적 막대그래프)
    df_trans['공항_비율'] = (df_trans['공항_소계'] / df_trans['소계']) * 100
    df_trans['항구_비율'] = (df_trans['항구_소계'] / df_trans['소계']) * 100
    
    fig3_2 = go.Figure()
    fig3_2.add_trace(go.Bar(x=df_trans['대륙'], y=df_trans['공항_비율'], name='공항 이용률(%)'))
    fig3_2.add_trace(go.Bar(x=df_trans['대륙'], y=df_trans['항구_비율'], name='항구 이용률(%)'))
    
    fig3_2.update_layout(barmode='stack', title="대륙별 공항 vs 항구 이용 비율(%)")
    st.plotly_chart(fig3_2, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(query3, language='sql')
    st.write("💡 **인사이트**")
    st.write("- 인천공항이 압도적인 1위 입국 경로이며, 대다수의 대륙이 공항 의존도가 매우 높습니다.")
    st.write("- 하지만 지리적으로 가까운 특정 대륙의 경우 항구 이용 비율이 유의미하게 나타나기도 하므로 항구 면세점 마케팅 시 참고해야 합니다.")

st.sidebar.info("이 대시보드는 visitor.db 데이터를 기반으로 생성되었습니다.")