import streamlit as st
import pandas as pd
import os
import plotly.express as px
import requests
from datetime import datetime, timedelta
from streamlit_lottie import st_lottie

# ==========================================
# 1. CÁC HÀM TRỢ GIÚP & KHỞI TẠO DỮ LIỆU
# ==========================================
def load_lottieurl(url: str):
    """Tải ảnh động Lottie."""
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except:
        return None

# Kiểm tra trạng thái đăng nhập
if not st.session_state.get('logged_in'):
    st.switch_page("app.py")

HISTORY_FILE = os.path.join("data", "diagnosis_history.csv")

def init_mock_history():
    """Tạo dữ liệu mẫu bao gồm cả các trường Sinh hiệu mới."""
    os.makedirs("data", exist_ok=True)
        
    if not os.path.exists(HISTORY_FILE) or os.path.getsize(HISTORY_FILE) == 0:
        now = datetime.now()
        mock_data = [
            [(now - timedelta(days=0, hours=2)).strftime("%Y-%m-%d %H:%M"), "Nguyễn Văn An", 45, "Nam", 38.5, 95, "130/85", "Ho, Sốt, Mệt mỏi", "Cảm cúm", "85.5%"],
            [(now - timedelta(days=1, hours=5)).strftime("%Y-%m-%d %H:%M"), "Trần Thị Bích", 28, "Nữ", 37.2, 80, "110/70", "Đau đầu, Chóng mặt", "Thiếu máu não", "72.0%"],
            [(now - timedelta(days=2, hours=1)).strftime("%Y-%m-%d %H:%M"), "Lê Hoàng Cường", 55, "Nam", 39.0, 110, "150/95", "Khó thở, Tức ngực, Ho", "Viêm phổi", "91.2%"]
        ]
        df_mock = pd.DataFrame(mock_data, columns=["Ngày", "Bệnh nhân", "Tuổi", "Giới tính", "Nhiệt độ", "Nhịp tim", "Huyết áp", "Triệu chứng", "Kết quả", "Độ tin cậy"])
        df_mock.to_csv(HISTORY_FILE, index=False, encoding='utf-8-sig')

init_mock_history()

@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(HISTORY_FILE)
    
    # Chuẩn hóa dữ liệu cũ
    new_cols = {"Tuổi": 0, "Giới tính": "Khác", "Nhiệt độ": 37.0, "Nhịp tim": 80, "Huyết áp": "120/80"}
    for col, default_val in new_cols.items():
        if col not in df.columns:
            df[col] = default_val
            
    df['Ngày_DT'] = pd.to_datetime(df['Ngày'], format="%Y-%m-%d %H:%M", errors='coerce')
    df['Conf_Float'] = df['Độ tin cậy'].astype(str).str.replace('%', '').astype(float)
    return df

df_hist = load_data()

# ==========================================
# 2. GIAO DIỆN HEADER & TÌM KIẾM
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
col_title, col_anim = st.columns([3.5, 1], gap="medium") # Nới nhẹ gap chỗ Header
with col_title:
    st.markdown("<h2 style='color: #007BFF;'>📂 Lịch Sử Khám & Chẩn Đoán</h2>", unsafe_allow_html=True)
    st.caption("Tra cứu, trích xuất và quản lý hồ sơ bệnh án lâm sàng được AI hỗ trợ.")
with col_anim:
    lottie_search = load_lottieurl("https://lottie.host/8e20fcd5-3ba5-4b07-8898-72b16bf156eb/4L6XzM8J7x.json")
    if lottie_search: st_lottie(lottie_search, height=80)

# Khung Tìm kiếm & Lọc nâng cao
with st.expander("🔍 Bộ lọc tìm kiếm nâng cao", expanded=True):
    # FIX LỖI ĐÈ CHỮ: Chỉnh lại tỷ lệ [1.2, 1, 1.8] để ưu tiên ô chọn Ngày rộng hơn, thêm gap="large"
    col_f1, col_f2, col_f3 = st.columns([1.2, 1, 1.8], gap="large")
    
    with col_f1:
        search_name = st.text_input("Tên bệnh nhân", placeholder="Nhập tên cần tìm...")
    with col_f2:
        disease_list = ["Tất cả"] + list(df_hist['Kết quả'].dropna().unique())
        search_disease = st.selectbox("Lọc theo bệnh lý", disease_list)
    with col_f3:
        min_date = df_hist['Ngày_DT'].min().date() if not df_hist.empty else datetime.now().date()
        max_date = datetime.now().date()
        date_range = st.date_input("Khoảng thời gian", value=(min_date, max_date), min_value=min_date, max_value=max_date)

# Áp dụng logic lọc
df_filtered = df_hist.copy()
if search_name:
    df_filtered = df_filtered[df_filtered['Bệnh nhân'].str.contains(search_name, case=False, na=False)]
if search_disease != "Tất cả":
    df_filtered = df_filtered[df_filtered['Kết quả'] == search_disease]
if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df_filtered[(df_filtered['Ngày_DT'].dt.date >= start_date) & (df_filtered['Ngày_DT'].dt.date <= end_date)]

df_filtered = df_filtered.sort_values(by='Ngày_DT', ascending=False).drop(columns=['Ngày_DT'])

# ==========================================
# 3. HIỂN THỊ DỮ LIỆU & BIỂU ĐỒ (TABS)
# ==========================================
tab_table, tab_chart = st.tabs(["📑 Bảng dữ liệu hồ sơ", "📈 Thống kê chuyên sâu"])

with tab_table:
    st.markdown(f"**Tìm thấy `{len(df_filtered)}` hồ sơ phù hợp.**")
    
    st.dataframe(
        df_filtered,
        use_container_width=True,
        hide_index=True,
        column_order=["Ngày", "Bệnh nhân", "Tuổi", "Giới tính", "Huyết áp", "Triệu chứng", "Kết quả", "Conf_Float"],
        column_config={
            "Ngày": st.column_config.DatetimeColumn("Thời gian", format="DD/MM/YYYY HH:mm"),
            "Bệnh nhân": st.column_config.TextColumn("Tên Bệnh Nhân", width="medium"),
            "Tuổi": st.column_config.NumberColumn("Tuổi"),
            "Giới tính": st.column_config.TextColumn("Giới tính"),
            "Huyết áp": st.column_config.TextColumn("Huyết áp"),
            "Triệu chứng": st.column_config.TextColumn("Triệu chứng lâm sàng", width="large"),
            "Kết quả": st.column_config.TextColumn("Chẩn đoán AI", width="medium"),
            "Conf_Float": st.column_config.ProgressColumn(
                "Độ tin cậy", 
                format="%.1f %%", 
                min_value=0, 
                max_value=100
            )
        },
        height=400
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_dl1, col_dl2 = st.columns([3, 1])
    with col_dl2:
        csv_bytes = df_filtered.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 Xuất File Excel (CSV)",
            data=csv_bytes,
            file_name=f"CDSS_Lamsang_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )

with tab_chart:
    if df_filtered.empty:
        st.warning("⚠️ Không có dữ liệu để vẽ biểu đồ.")
    else:
        # FIX LỖI ĐÈ CHỮ BIỂU ĐỒ: Đảm bảo có gap giữa 2 cột đồ thị
        col_c1, col_c2 = st.columns(2, gap="large")
        
        with col_c1:
            st.markdown("<div class='stCard'><h4>🧬 Phân bố bệnh lý theo giới tính</h4>", unsafe_allow_html=True)
            fig_gender = px.histogram(
                df_filtered, y="Kết quả", color="Giới tính",
                orientation='h', barmode='group',
                color_discrete_map={"Nam": "#4C78A8", "Nữ": "#F58518", "Khác": "#E45756"}
            )
            # Tăng Margin trái/phải lên 15 để chữ không bị sát lề
            fig_gender.update_layout(height=350, xaxis_title="Số lượng ca", yaxis_title="Bệnh lý", margin=dict(l=15, r=15, t=30, b=15))
            st.plotly_chart(fig_gender, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_c2:
            st.markdown("<div class='stCard'><h4>🔥 Tương quan Độ tuổi & Độ tin cậy AI</h4>", unsafe_allow_html=True)
            fig_scatter = px.scatter(
                df_filtered, x="Tuổi", y="Conf_Float", color="Kết quả",
                size="Conf_Float", hover_data=["Bệnh nhân"],
                labels={"Conf_Float": "Độ tin cậy (%)", "Tuổi": "Độ tuổi"}
            )
            # Tăng Margin trái/phải lên 15 để chữ không bị sát lề
            fig_scatter.update_layout(height=350, margin=dict(l=15, r=15, t=30, b=15))
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)