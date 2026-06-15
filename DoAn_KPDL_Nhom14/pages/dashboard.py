import streamlit as st
import plotly.express as px
import pandas as pd
import os
import requests
from datetime import datetime, timedelta
from streamlit_lottie import st_lottie

# ==========================================
# 1. CÁC HÀM TRỢ GIÚP & ĐỌC DỮ LIỆU
# ==========================================
def load_lottieurl(url: str):
    """Tải ảnh động Lottie."""
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except:
        return None

# Kiểm tra đăng nhập
if not st.session_state.get('logged_in'):
    st.switch_page("app.py") # Chỉnh lại đường dẫn trang chủ cho đúng với cấu trúc của bạn

HISTORY_FILE = os.path.join("data", "diagnosis_history.csv")

@st.cache_data(ttl=10) # Cache dữ liệu 10 giây
def load_dashboard_data():
    """Hàm tải và làm sạch dữ liệu từ file lịch sử."""
    if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
        df = pd.read_csv(HISTORY_FILE)
        if not df.empty:
            # Làm sạch cột độ tin cậy
            df['Conf_Float'] = df['Độ tin cậy'].astype(str).str.replace('%', '').astype(float)
            # Chuyển đổi cột Ngày sang Datetime
            df['Ngày_DateTime'] = pd.to_datetime(df['Ngày'], format="%Y-%m-%d %H:%M", errors='coerce')
            df['Ngày_Ngắn'] = df['Ngày_DateTime'].dt.strftime('%d/%m/%Y')
            return df
    return pd.DataFrame()

df_hist = load_dashboard_data()

# ==========================================
# 2. GIAO DIỆN HEADER
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"<h2>👋 Xin chào, {st.session_state.username}!</h2>", unsafe_allow_html=True)
    st.caption(f"📅 Báo cáo tổng quan hệ thống CDSS - Cập nhật lúc: {datetime.now().strftime('%H:%M - %d/%m/%Y')}")
with col_h2:
    lottie_dash = load_lottieurl("https://lottie.host/80e9a7e6-7788-4670-87a7-336750f28328/z99g9t1XhS.json")
    if lottie_dash: st_lottie(lottie_dash, height=80, key="dash_anim")

st.markdown("<hr style='margin-top: 0px;'>", unsafe_allow_html=True)

# ==========================================
# 3. BỘ LỌC DỮ LIỆU & XUẤT BÁO CÁO
# ==========================================
df_filtered = df_hist.copy()

if not df_hist.empty:
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1.5])
    
    with col_f1:
        disease_list = ["Tất cả"] + list(df_hist['Kết quả'].dropna().unique())
        selected_disease = st.selectbox("🔍 Lọc theo Bệnh lý", disease_list)
        
    with col_f2:
        time_filter = st.selectbox("📅 Khung thời gian", ["Tất cả", "Hôm nay", "7 ngày qua", "30 ngày qua"])
        
    # Xử lý Logic lọc dữ liệu
    now = datetime.now()
    if selected_disease != "Tất cả":
        df_filtered = df_filtered[df_filtered['Kết quả'] == selected_disease]
        
    if time_filter == "Hôm nay":
        df_filtered = df_filtered[df_filtered['Ngày_DateTime'].dt.date == now.date()]
    elif time_filter == "7 ngày qua":
        df_filtered = df_filtered[df_filtered['Ngày_DateTime'].dt.date >= (now.date() - timedelta(days=7))]
    elif time_filter == "30 ngày qua":
        df_filtered = df_filtered[df_filtered['Ngày_DateTime'].dt.date >= (now.date() - timedelta(days=30))]

    with col_f3:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        # Nút xuất file CSV (Chỉ xuất dữ liệu đã lọc)
        csv_data = df_filtered.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Xuất báo cáo (CSV)",
            data=csv_data,
            file_name=f"Bao_cao_CDSS_{now.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
    st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 4. TÍNH TOÁN METRICS (DỰA TRÊN DỮ LIỆU ĐÃ LỌC)
# ==========================================
if not df_filtered.empty:
    total_patients = df_filtered['Bệnh nhân'].nunique()
    total_diagnoses = len(df_filtered)
    avg_confidence = df_filtered['Conf_Float'].mean()
    top_disease = df_filtered['Kết quả'].mode()[0] if not df_filtered['Kết quả'].empty else "Không rõ"
    
    # Tính số ca chẩn đoán trong ngày hôm nay (dùng cho delta)
    today_str = datetime.now().strftime('%d/%m/%Y')
    today_cases = len(df_filtered[df_filtered['Ngày_Ngắn'] == today_str])
else:
    total_patients = total_diagnoses = today_cases = 0
    avg_confidence = 0.0
    top_disease = "Không có dữ liệu"

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("<div class='stCard' style='text-align: center;'>", unsafe_allow_html=True)
    st.metric(label="👥 Tổng bệnh nhân", value=f"{total_patients:,}", delta="Số lượng duy nhất")
    st.markdown("</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='stCard' style='text-align: center;'>", unsafe_allow_html=True)
    st.metric(label="🩺 Số ca phân tích", value=f"{total_diagnoses:,}", delta=f"{today_cases} ca hôm nay" if today_cases > 0 else "Không có ca mới")
    st.markdown("</div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='stCard' style='text-align: center;'>", unsafe_allow_html=True)
    st.metric(label="🎯 Độ tin cậy AI (TB)", value=f"{avg_confidence:.1f}%", delta="Mô hình hiện tại")
    st.markdown("</div>", unsafe_allow_html=True)
with col4:
    st.markdown("<div class='stCard' style='text-align: center;'>", unsafe_allow_html=True)
    st.metric(label="🚨 Nhóm bệnh phổ biến", value=top_disease, delta="Cảnh báo cao", delta_color="inverse")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. TRỰC QUAN HÓA BẰNG BIỂU ĐỒ & BẢNG
# ==========================================
if df_filtered.empty:
    st.info("📊 Không có dữ liệu chẩn đoán phù hợp với bộ lọc hiện tại.")
else:
    col_chart1, col_chart2 = st.columns([1.2, 1], gap="large")

    with col_chart1:
        st.markdown("<div class='stCard'><h4>📈 Lưu lượng khám bệnh theo ngày</h4>", unsafe_allow_html=True)
        df_trend = df_filtered.groupby('Ngày_Ngắn').size().reset_index(name='Số ca khám')
        
        fig_line = px.line(
            df_trend, x='Ngày_Ngắn', y='Số ca khám', markers=True, 
            line_shape='spline', color_discrete_sequence=['#007BFF'],
            labels={'Ngày_Ngắn': 'Ngày ghi nhận', 'Số ca khám': 'Số lượng ca'}
        )
        fig_line.update_traces(fill='tozeroy', fillcolor='rgba(0, 123, 255, 0.1)')
        fig_line.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320, xaxis=dict(showgrid=False))
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_chart2:
        st.markdown("<div class='stCard'><h4>🦠 Tỷ trọng phân bố bệnh lý</h4>", unsafe_allow_html=True)
        df_disease = df_filtered['Kết quả'].value_counts().reset_index()
        df_disease.columns = ['Bệnh lý', 'Số ca']
        
        fig_pie = px.pie(
            df_disease, values='Số ca', names='Bệnh lý', hole=0.45, 
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------
    # BẢNG DỮ LIỆU HOẠT ĐỘNG GẦN NHẤT
    # ------------------------------------------
    st.markdown("<div class='stCard'>", unsafe_allow_html=True)
    st.markdown(f"<h4>⏱️ Các ca chuẩn đoán mới nhất ({len(df_filtered)} ca tìm thấy)</h4>", unsafe_allow_html=True)
    
    # Lấy 5 dòng cuối cùng (mới nhất) và đảo ngược thứ tự
    df_recent = df_filtered.tail(5).iloc[::-1]
    
    st.dataframe(
        df_recent[['Ngày', 'Bệnh nhân', 'Kết quả', 'Độ tin cậy']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ngày": st.column_config.TextColumn("Thời gian"),
            "Bệnh nhân": st.column_config.TextColumn("Bệnh nhân"),
            "Kết quả": st.column_config.TextColumn("Kết luận"),
            "Độ tin cậy": st.column_config.TextColumn("Độ tin cậy AI", width="small")
        }
    )
    st.markdown("</div>", unsafe_allow_html=True)