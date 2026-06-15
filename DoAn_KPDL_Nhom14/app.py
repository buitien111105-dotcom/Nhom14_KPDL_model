import streamlit as st
import time
from utils.styles import load_css
from utils.auth import init_auth_session
from utils.database import init_db

# ==========================================
# 1. CẤU HÌNH HỆ THỐNG GỐC (MUST BE FIRST)
# ==========================================
st.set_page_config(
    page_title="CDSS System - Hệ Thống Điều Phối Trung Tâm",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"  # Đổi thành collapsed để trang login hiển thị tràn viền Pro
)

# ==========================================
# 2. KHỞI TẠO TOÀN DIỆN MÔI TRƯỜNG DỮ LIỆU
# ==========================================
init_db()            # Khởi tạo thư mục data, tệp users.csv và các bản sao lưu
init_auth_session()  # Thiết lập các biến Session State bảo mật
load_css()           # Nạp bộ mã CSS cao cấp

# ĐỒNG BỘ NỀN SÁNG VÀ ẨN SIDEBAR CHO TRANG CHỜ/LOGIN
st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC !important; }
        /* Ẩn hoàn toàn nút điều khiển sidebar ở màn hình chờ và đăng nhập */
        [data-testid="collapsedControl"] { display: none !important; }
        
        /* Định dạng khung chờ đồng bộ Light Glassmorphism */
        .splash-card {
            background: rgba(255, 255, 255, 0.8) !important;
            backdrop-filter: blur(15px) !important;
            -webkit-backdrop-filter: blur(15px) !important;
            border: 1px solid rgba(255, 255, 255, 0.9) !important;
            border-radius: 24px !important;
            padding: 40px !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04) !important;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. ĐỘNG CƠ ĐIỀU HƯỚNG THÔNG MINH (ROUTER)
# ==========================================
if st.session_state.get('logged_in'):
    st.switch_page("pages/dashboard.py")
else:
    st.switch_page("pages/login.py")

# ==========================================
# 4. MÀN HÌNH CHỜ DỰ PHÒNG (SPLASH SCREEN)
# ==========================================
st.markdown("<br><br><br>", unsafe_allow_html=True)
col_space1, col_main_card, col_space2 = st.columns([1, 1.5, 1])

with col_main_card:
    st.markdown("""
        <div class='splash-card' style='border-bottom: 5px solid #007BFF;'>
            <h1 style='color: #007BFF; font-size: 2.8rem; margin-bottom: 0px;'>🩺 CDSS SYSTEM</h1>
            <h4 style='color: #64748b; margin-top: 5px; font-weight: 400;'>Clinical Decision Support System</h4>
            <p style='color: #1e293b; font-size: 1.05rem; margin-top: 25px; line-height: 1.6;'>
                Đang tiến hành kiểm tra cấu trúc cơ sở dữ liệu lâm sàng, giải mã bộ luật khai phá dữ liệu 
                và thiết lập môi trường bảo mật mã hóa tài khoản...
            </p>
            <div style='margin: 30px 0;'>
                <span style='color: #64748b; font-style: italic;'>⏳ Hệ thống đang điều hướng tự động, vui lòng chờ...</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Chuyển trang thủ công (Nếu hệ thống không tự nhảy)", type="primary", use_container_width=True):
        if st.session_state.get('logged_in'):
            st.switch_page("pages/dashboard.py")
        else:
            st.switch_page("pages/login.py")

# ==========================================
# 5. TÀI LIỆU KIẾN TRÚC ĐỒ ÁN (DOCUMENTATION)
# ==========================================
"""
📌 KIẾN TRÚC PHÂN RÃ CHỨC NĂNG HỆ THỐNG CDSS:
┌─ app.py (File này - Bộ điều phối và khởi tạo môi trường gốc)
├─ data/
│  ├─ users.csv (Cơ sở dữ liệu tài khoản người dùng)
│  ├─ diagnosis_history.csv (Cơ sở dữ liệu bệnh án lâm sàng)
│  └─ ket_qua_khai_pha.csv (Tập luật sinh ra từ thuật toán FP-Growth)
├─ utils/
│  ├─ auth.py (Bảo mật mã hóa HMAC & SHA-256, Phân quyền require_role)
│  ├─ database.py (Quản lý CRUD, ghi file an toàn Atomic-Write & Tự động Backup)
│  ├─ styles.py (Định dạng UI toàn diện bằng CSS3 Variables & Hiệu ứng 3D)
│  ├─ validation.py (Bắt lỗi định dạng nâng cao: Email, Pass chữ-số, Huyết áp, Sinh hiệu)
│  └─ predictor.py (Động cơ AI: So khớp Strict Match và Suy luận mềm Fuzzy Match)
└─ pages/
   ├─ login.py (Giao diện đăng nhập tối giản Glassmorphism)
   ├─ register.py (Giao diện Đăng ký tối giản đồng bộ)
   ├─ dashboard.py (Bảng thống kê số liệu thực tế, đồ thị lưu lượng và tỷ trọng bệnh lý)
   ├─ diagnosis.py (Form nhập sinh hiệu, ô tìm kiếm chọn triệu chứng, biểu đồ Gauge rủi ro bệnh)
   ├─ history.py (Tra cứu hồ sơ bệnh án, bộ lọc đa chiều, xem chi tiết bệnh án điện tử, xuất Excel)
   └─ profile.py (Trung tâm quản lý tài khoản cá nhân, đổi mật khẩu bảo mật, xem nhật ký log)
"""