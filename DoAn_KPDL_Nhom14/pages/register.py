import streamlit as st
import time

# --- IMPORT THÊM HÀM ĐỂ XỬ LÝ LƯU DỮ LIỆU ---
from utils.database import load_users, save_user
from utils.auth import hash_password

# 1. INJECT CSS ĐỒNG BỘ 100% VỚI LOGIN
st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC !important; }
        .blob-1 {
            position: fixed; bottom: -20%; right: -10%; width: 600px; height: 600px;
            background: radial-gradient(circle, rgba(138,35,135,0.15) 0%, transparent 70%);
            border-radius: 50%; filter: blur(90px); z-index: 0; pointer-events: none;
        }
        .blob-2 {
            position: fixed; top: -15%; left: -10%; width: 600px; height: 600px;
            background: radial-gradient(circle, rgba(0,194,168,0.15) 0%, transparent 70%);
            border-radius: 50%; filter: blur(90px); z-index: 0; pointer-events: none;
        }
        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(25px) !important;
            -webkit-backdrop-filter: blur(25px) !important;
            border: 1px solid rgba(255, 255, 255, 0.9) !important;
            border-radius: 24px !important;
            padding: 35px 30px !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05) !important;
            position: relative; z-index: 10;
        }
        div[data-baseweb="input"] {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 10px !important;
        }
        /* MÀU CHỮ ĐEN XÁM ĐỂ HIỂN THỊ RÕ */
        div[data-baseweb="input"] input { color: #1e293b !important; }
        h1, h3, p, label { color: #1e293b !important; }

        button[kind="secondaryFormSubmit"] {
            background: linear-gradient(135deg, #8A2387 0%, #E94057 100%) !important;
            color: white !important; border: none !important; border-radius: 12px !important;
            font-weight: 700 !important; padding: 12px !important;
            transition: all 0.3s ease !important; margin-top: 20px !important;
        }
        button[kind="secondaryFormSubmit"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(233,64,87,0.3) !important;
        }
        .stButton > button {
            background: transparent !important; border: none !important;
            color: #64748b !important; font-size: 0.95rem !important;
            font-weight: 500 !important; transition: color 0.3s !important;
            box-shadow: none !important; margin: 0 auto !important; display: block !important;
        }
        .stButton > button:hover { color: #007BFF !important; background: transparent !important; }
    </style>
    <div class="blob-1"></div><div class="blob-2"></div>
""", unsafe_allow_html=True)

# 2. HEADER
st.markdown("""
    <div style='text-align: center; margin-bottom: 30px; position: relative; z-index: 10;'>
        <h1 style='font-size: 3.2rem; margin-bottom: 5px; background: linear-gradient(135deg, #8A2387 0%, #E94057 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            🩺 CDSS SYSTEM
        </h1>
        <h3 style='font-weight: 300; font-size: 1.1rem; color: #64748b !important;'>Đăng Ký Tài Khoản Thành Viên Lâm Sàng</h3>
    </div>
""", unsafe_allow_html=True)

# 3. FORM ĐĂNG KÝ
col1, col2, col3 = st.columns([0.8, 1.4, 0.8])
with col2:
    with st.form("register_form"):
        username = st.text_input("👤 Tên đăng nhập")
        email = st.text_input("📧 Email làm việc")
        fullname = st.text_input("🏷️ Họ và tên bác sĩ")
        password = st.text_input("🔒 Mật khẩu hệ thống", type="password")
        submit_btn = st.form_submit_button("Đăng ký tài khoản", use_container_width=True)
        
    if submit_btn:
        # 1. Làm sạch dữ liệu (loại bỏ khoảng trắng thừa)
        user_clean = username.strip()
        email_clean = email.strip()
        full_clean = fullname.strip()
        pass_clean = password.strip()

        # 2. Kiểm tra bỏ trống
        if not user_clean or not email_clean or not full_clean or not pass_clean:
            st.warning("⚠️ Vui lòng điền đầy đủ thông tin vào tất cả các trường.")
        elif len(pass_clean) < 8:
            st.error("❌ Mật khẩu quá yếu! Vui lòng nhập ít nhất 8 ký tự.")
        else:
            # 3. Kiểm tra xem tên đăng nhập đã tồn tại chưa
            df_users = load_users()
            
            # Khắc phục lỗi cột username trống lúc file csv mới tạo
            if not df_users.empty and 'username' in df_users.columns:
                existing_users = df_users['username'].astype(str).str.strip().tolist()
            else:
                existing_users = []

            if user_clean in existing_users:
                st.error("❌ Tên đăng nhập này đã có người sử dụng. Vui lòng chọn tên khác.")
            else:
                # 4. Mã hóa mật khẩu và ghi xuống file Database
                hashed_pass = hash_password(pass_clean)
                
                # Gọi hàm save_user từ file utils/database.py
                save_user(
                    username=user_clean, 
                    hashed_password=hashed_pass, 
                    email=email_clean, 
                    role="Bác sĩ", # Đăng ký mặc định là Bác sĩ
                    fullname=full_clean
                )
                
                st.success("🎉 Tạo tài khoản thành công! Dữ liệu đã được lưu vào hệ thống.")
                time.sleep(1.5)
                st.switch_page("pages/login.py")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    if st.button("Đã có tài khoản danh bạ? Đăng nhập ngay"):
        st.switch_page("pages/login.py")