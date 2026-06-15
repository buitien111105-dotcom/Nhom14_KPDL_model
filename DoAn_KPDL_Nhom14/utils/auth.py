import hashlib
import hmac
import streamlit as st
from typing import List

# ==========================================
# 1. CORE BẢO MẬT MẬT KHẨU (CRYPTOGRAPHY)
# ==========================================

def hash_password(password: str) -> str:
    """
    Mã hóa mật khẩu bằng thuật toán SHA-256.
    (Giữ nguyên cơ chế để tương thích ngược với dữ liệu tài khoản cũ).
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(stored_password: str, provided_password: str) -> bool:
    """
    Xác minh mật khẩu an toàn cao.
    Sử dụng hmac.compare_digest để chống lại các cuộc tấn công 
    căn chỉnh thời gian (Timing Attacks) thay vì toán tử == thông thường.
    """
    # Sinh chuỗi mã hóa từ mật khẩu người dùng nhập vào
    provided_hash = hash_password(provided_password)
    
    # Thực hiện so sánh an toàn
    return hmac.compare_digest(stored_password, provided_hash)

# ==========================================
# 2. QUẢN LÝ PHIÊN LÀM VIỆC (SESSION MANAGEMENT)
# ==========================================

def init_auth_session():
    """Khởi tạo các biến bảo mật hệ thống an toàn khi mở ứng dụng."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0 # Theo dõi chống Brute-force

def logout():
    """
    Hủy toàn bộ phiên làm việc (Clear Session).
    Dọn dẹp sạch sẽ rác bộ nhớ để ngăn chặn rò rỉ dữ liệu y tế.
    """
    # Danh sách các biến cần tiêu hủy khi đăng xuất
    keys_to_clear = [
        'logged_in', 'username', 'role', 
        'temp_user', 'temp_role', 'generated_otp', 
        'reg_step', 'reg_data', 'user_profile'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
            
    # Đặt lại trạng thái gốc
    st.session_state.logged_in = False

# ==========================================
# 3. PHÂN QUYỀN TRUY CẬP (RBAC)
# ==========================================

def require_role(allowed_roles: List[str]):
    """
    Lá chắn bảo vệ trang: Kiểm tra quyền truy cập. 
    Nếu không có quyền, chặn đứng và đá văng người dùng.
    
    Cách dùng: Gọi require_role(["Bác sĩ", "Quản trị viên"]) ở đầu các trang quan trọng.
    """
    # 1. Kiểm tra xem đã đăng nhập chưa
    if not st.session_state.get('logged_in'):
        st.warning("⚠️ Phiên làm việc đã hết hạn hoặc chưa xác thực. Vui lòng đăng nhập lại.")
        st.switch_page("pages/login.py")
        st.stop() # Dừng chạy code bên dưới
        
    # 2. Kiểm tra vai trò có khớp danh sách cho phép không
    current_role = st.session_state.get('role', '')
    if current_role not in allowed_roles:
        st.error(f"⛔ Truy cập bị từ chối! Tính năng này chỉ dành cho: {', '.join(allowed_roles)}.")
        st.stop() # Cắt đứt luồng render giao diện