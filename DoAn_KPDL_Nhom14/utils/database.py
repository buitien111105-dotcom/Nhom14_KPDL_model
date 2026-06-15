import pandas as pd
import os
import time
import shutil
from typing import Dict, Any
import streamlit as st

# ==========================================
# 1. CẤU HÌNH ĐƯỜNG DẪN BỘ NHỚ
# ==========================================
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

# Cấu trúc các trường dữ liệu hệ thống yêu cầu
COLUMNS = [
    "username", "password", "email", "role", 
    "fullname", "phone", "department", "two_factor"
]

# ==========================================
# 2. CÁC HÀM QUẢN TRỊ FILE & BACKUP
# ==========================================
def init_db():
    """Khởi tạo cấu trúc Database và thư mục an toàn."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')

def create_backup():
    """Cơ chế tự động sao lưu dữ liệu (Giữ lại 5 bản snapshot mới nhất)."""
    if os.path.exists(USERS_FILE):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"users_backup_{timestamp}.csv")
        shutil.copy2(USERS_FILE, backup_file)
        
        # Xóa các file backup cũ, chỉ giữ lại 5 bản gần nhất
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.csv')])
        if len(backups) > 5:
            for old_file in backups[:-5]:
                os.remove(os.path.join(BACKUP_DIR, old_file))

def safe_write(df, filepath):
    """Ghi dữ liệu an toàn tránh lỗi đụng độ file (File lock) khi có nhiều user thao tác."""
    temp_file = f"{filepath}.tmp"
    try:
        df.to_csv(temp_file, index=False, encoding='utf-8-sig')
        if os.path.exists(filepath):
            os.replace(temp_file, filepath)
        else:
            os.rename(temp_file, filepath)
    except Exception as e:
        print(f"❌ Lỗi ghi file: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)

# ==========================================
# 3. CÁC HÀM TƯƠNG TÁC DỮ LIỆU (CRUD)
# ==========================================

# ĐÃ XÓA @st.cache_data ĐỂ FIX LỖI ĐĂNG NHẬP (Luôn đọc dữ liệu mới nhất)
def load_users():
    """Tải toàn bộ dữ liệu người dùng từ CSV."""
    init_db()
    try:
        df = pd.read_csv(USERS_FILE)
        # Đảm bảo có đủ các cột nếu update từ bản cũ
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = False if col == 'two_factor' else ""
        return df
    except Exception as e:
        print(f"❌ Lỗi đọc Database: {e}")
        return pd.DataFrame(columns=COLUMNS)

def save_user(username, hashed_password, email, role, **kwargs):
    """Tạo mới tài khoản người dùng và lưu vào Database."""
    create_backup()
    df = load_users()
    
    new_data = {
        "username": username,
        "password": hashed_password,
        "email": email,
        "role": role,
        "fullname": kwargs.get("fullname", ""),
        "phone": kwargs.get("phone", ""),
        "department": kwargs.get("department", ""),
        "two_factor": kwargs.get("two_factor", False)
    }
    
    new_user_df = pd.DataFrame([new_data])
    df = pd.concat([df, new_user_df], ignore_index=True)
    
    safe_write(df, USERS_FILE)

def update_user_profile(username: str, updates: Dict[str, Any]) -> bool:
    """
    Cập nhật dữ liệu cho một tài khoản cụ thể.
    """
    df = load_users()
    
    if username not in df['username'].values:
        return False
        
    create_backup()
    
    # Cập nhật các trường tương ứng
    for key, value in updates.items():
        if key in df.columns:
            df.loc[df['username'] == username, key] = value
            
    safe_write(df, USERS_FILE)
    return True