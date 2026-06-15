import streamlit as st
import time
import base64 

# ==========================================
# 1. KHỞI TẠO & KIỂM TRA PHIÊN
# ==========================================
if not st.session_state.get('logged_in'):
    st.switch_page("app.py")

username = st.session_state.username

def get_image_as_base64(path):
    try:
        with open(path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded_string}"
    except:
        return None 

# ==========================================
# 2. CSS TỐI GIẢN (Chỉ dùng cho Avatar & Metric)
# ==========================================
st.markdown("""
    <style>
        .avatar-img {
            width: 100%;
            max-width: 200px;
            border-radius: 50%;
            border: 4px solid #f8fafc;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            display: block;
            margin: 0 auto 20px auto;
        }
        .placeholder-avatar {
            width: 150px; height: 150px; border-radius: 50%;
            background-color: #cbd5e1; display: flex; align-items: center; justify-content: center;
            font-size: 4rem; margin: 0 auto 20px auto;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. GIAO DIỆN CHÍNH
# ==========================================
st.title("Hồ Sơ Thành Viên")
st.markdown("Hệ thống Hỗ trợ Ra quyết định Lâm sàng (CDSS)")
st.divider()

# Sử dụng Tabs để quản lý UX gọn gàng hơn
tab_profile, tab_security = st.tabs(["👤 Thông tin chung", "🔒 Bảo mật tài khoản"])

# --- TAB 1: THÔNG TIN CHUNG ---
with tab_profile:
    col_avatar, col_info = st.columns([1, 2.5], gap="large")
    
    # Cột Trái: Ảnh đại diện & Thống kê nhanh
    with col_avatar:
        doctor_img_base64 = get_image_as_base64("doctor.png")
        if doctor_img_base64:
            st.markdown(f"<img src='{doctor_img_base64}' class='avatar-img'>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='placeholder-avatar'>👨‍⚕️</div>", unsafe_allow_html=True)
        
        # Thêm các Metric để nhìn giống Dashboard thật
        st.metric(label="Ca chẩn đoán tháng này", value="128", delta="+12")
        st.metric(label="Đánh giá nội bộ", value="4.9/5.0")

    # Cột Phải: Form thông tin cá nhân
    with col_info:
        st.subheader("Thông tin chi tiết")
        
        # Dùng container để nhóm các trường
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("ID Tài khoản", value=f"@{username}", disabled=True)
                st.text_input("Email làm việc", value="nguyenvana@hospital.vn", disabled=True)
            with col2:
                st.text_input("Họ và tên", value="Nguyễn Văn A", disabled=True)
                st.text_input("Số điện thoại", value="0912 345 678", disabled=True)
                
            st.text_input("Chuyên khoa", value="Nội tổng hợp", disabled=True)
            st.text_input("Vai trò trên hệ thống", value="Bác sĩ Chẩn đoán (Quyền truy cập: Cấp 2)", disabled=True)
            
        # Nút Đăng xuất đưa xuống góc gọn gàng hơn
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Đăng xuất khỏi hệ thống", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.success("Đang đăng xuất...")
            time.sleep(0.5)
            st.switch_page("app.py")

# --- TAB 2: BẢO MẬT TÀI KHOẢN ---
with tab_security:
    st.subheader("Đổi mật khẩu")
    st.info("Để đảm bảo an toàn cho dữ liệu bệnh nhân, mật khẩu mới cần có ít nhất 8 ký tự, bao gồm chữ cái và số.")
    
    # Form đổi mật khẩu đặt vào giữa để tạo sự tập trung
    col_sec1, col_sec_main, col_sec2 = st.columns([1, 2, 1])
    
    with col_sec_main:
        with st.form("change_password_form", border=True):
            old_pass = st.text_input("Mật khẩu hiện tại", type="password")
            new_pass = st.text_input("Mật khẩu mới", type="password")
            confirm_pass = st.text_input("Xác nhận mật khẩu mới", type="password")
            
            submit_btn = st.form_submit_button("Cập nhật mật khẩu", type="primary", use_container_width=True)

        # Xử lý logic
        if submit_btn:
            if not old_pass or not new_pass or not confirm_pass:
                st.warning("⚠️ Vui lòng điền đầy đủ các trường.")
            elif new_pass != confirm_pass:
                st.error("❌ Mật khẩu mới và xác nhận không khớp.")
            elif len(new_pass) < 8:
                st.error("❌ Mật khẩu quá ngắn.")
            else:
                st.success("🎉 Cập nhật thành công! (Dữ liệu Demo)")
                time.sleep(1)
                st.rerun()