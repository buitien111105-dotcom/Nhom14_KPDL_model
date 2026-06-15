import streamlit as st
import time

# --- IMPORT THÊM HÀM LOGIC ĐỂ ĐỐI CHIẾU DATABASE ---
from utils.database import load_users
from utils.auth import verify_password

# 1. INJECT CSS GLASSMORPHISM (LIGHT MODE)
st.markdown("""
    <style>
        /* Nền sáng thanh lịch */
        .stApp { background-color: #F8FAFC !important; }
        
        /* Hiệu ứng Khối màu lơ lửng dưới nền (Giảm độ đậm để hợp nền sáng) */
        .blob-1 {
            position: fixed; top: -15%; right: -10%; width: 600px; height: 600px;
            background: radial-gradient(circle, rgba(233,64,87,0.15) 0%, transparent 70%);
            border-radius: 50%; filter: blur(80px); z-index: 0; pointer-events: none;
        }
        .blob-2 {
            position: fixed; bottom: -15%; left: -10%; width: 600px; height: 600px;
            background: radial-gradient(circle, rgba(79,172,254,0.15) 0%, transparent 70%);
            border-radius: 50%; filter: blur(80px); z-index: 0; pointer-events: none;
        }

        /* Thẻ kính mờ sáng (Glassmorphism Light) */
        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(255, 255, 255, 0.9) !important;
            border-radius: 24px !important;
            padding: 40px 30px !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05) !important;
            position: relative; z-index: 10;
        }

        /* Ô nhập liệu */
        div[data-baseweb="input"] {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 12px !important;
        }
        /* MÀU CHỮ Ô NHẬP LIỆU: Đen/Xám đậm */
        div[data-baseweb="input"] input { color: #1e293b !important; }
        h1, h3, p, label { color: #1e293b !important; }

        /* Nút Đăng Nhập Gradient */
        button[kind="secondaryFormSubmit"] {
            background: linear-gradient(135deg, #E94057 0%, #8A2387 100%) !important;
            color: white !important; border: none !important; border-radius: 12px !important;
            font-weight: 700 !important; padding: 10px !important;
            transition: all 0.3s ease !important; margin-top: 15px !important;
        }
        button[kind="secondaryFormSubmit"]:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(233,64,87,0.3) !important;
        }

        /* Nút chuyển trang Đăng ký phẳng */
        .stButton > button {
            background: transparent !important; border: none !important;
            color: #64748b !important; font-size: 0.95rem !important;
            font-weight: 500 !important; transition: color 0.3s !important;
            box-shadow: none !important;
        }
        .stButton > button:hover { color: #E94057 !important; background: transparent !important; }
    </style>
    <div class="blob-1"></div><div class="blob-2"></div>
""", unsafe_allow_html=True)

# 2. HEADER
st.markdown("""
    <div style='text-align: center; margin-bottom: 30px; position: relative; z-index: 10;'>
        <h1 style='font-size: 3.2rem; margin-bottom: 5px; background: linear-gradient(135deg, #E94057 0%, #8A2387 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            🩺 CDSS SYSTEM
        </h1>
        <h3 style='font-weight: 300; font-size: 1.1rem; color: #64748b !important;'>Hệ Thống Hỗ Trợ Ra Quyết Định Lâm Sàng</h3>
    </div>
""", unsafe_allow_html=True)

# 3. FORM ĐĂNG NHẬP
col1, col2, col3 = st.columns([1, 1.2, 1])
with col2:
    with st.form("login_form"):
        username = st.text_input("👤 Tên đăng nhập", placeholder="Nhập tên đăng nhập...")
        password = st.text_input("🔒 Mật khẩu", type="password", placeholder="Nhập mật khẩu...")
        submit_btn = st.form_submit_button("Đăng nhập", use_container_width=True)
        
    if submit_btn:
        # Làm sạch khoảng trắng thừa do nhập nhầm
        username_clean = username.strip()
        password_clean = password.strip()

        if not username_clean or not password_clean:
            st.warning("⚠️ Vui lòng nhập đầy đủ Tên đăng nhập và Mật khẩu.")
        else:
            # Tải danh sách và làm sạch cột username trong DB
            df_users = load_users()
            df_users['username_clean'] = df_users['username'].astype(str).str.strip()
            
            # Đối chiếu dữ liệu đã làm sạch
            user_row = df_users[df_users['username_clean'] == username_clean]
            
            if user_row.empty:
                st.error("❌ Tài khoản không tồn tại trên hệ thống.")
            else:
                stored_hashed_password = user_row.iloc[0]['password']
                user_role = user_row.iloc[0]['role']
                
                # Hàm verify_password sẽ băm pass nhập vào và so sánh với pass trong database
                if verify_password(stored_hashed_password, password_clean):
                    st.session_state.logged_in = True
                    st.session_state.username = username_clean
                    st.session_state.role = user_role
                    
                    st.success("✅ Đăng nhập thành công!")
                    time.sleep(0.4)
                    st.switch_page("pages/dashboard.py")
                else:
                    st.error("❌ Mật khẩu không chính xác. Vui lòng thử lại.")
        
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    if st.button("Chưa có tài khoản? Đăng ký ngay", use_container_width=True):
        st.switch_page("pages/register.py")