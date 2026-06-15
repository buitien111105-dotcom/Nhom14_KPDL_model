import re

# ==========================================
# 1. KIỂM TRA TÀI KHOẢN & ĐỊNH DANH (AUTH)
# ==========================================

def validate_username(username):
    """
    Kiểm tra tính hợp lệ của tên đăng nhập.
    Yêu cầu: Dài từ 4-20 ký tự, không chứa dấu cách, chỉ gồm chữ cái, số hoặc dấu gạch dưới.
    """
    username = str(username).strip()
    if not username:
        return False, "Tên đăng nhập không được để trống."
    if len(username) < 4 or len(username) > 20:
        return False, "Tên đăng nhập phải có độ dài từ 4 đến 20 ký tự."
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Tên đăng nhập chỉ được chứa chữ cái, chữ số và dấu gạch dưới (_)."
    return True, ""

def validate_email(email):
    """
    Kiểm tra định dạng hòm thư điện tử RFC 5322 tiêu chuẩn.
    """
    email = str(email).strip()
    if not email:
        return False, "Địa chỉ Email không được để trống."
    
    # Kiểu Regex quét định dạng email toàn diện
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email):
        return False, "Định dạng Email không hợp lệ (Ví dụ đúng: bacsi@hospital.com)."
    return True, ""

def validate_password(password):
    """
    Đánh giá độ mạnh mã hóa mật khẩu hệ thống.
    Yêu cầu nghiêm ngặt: Tối thiểu 8 ký tự, phải có ít nhất 1 chữ cái và 1 chữ số để chống brute-force.
    """
    if not password:
        return False, "Mật khẩu không được để trống."
    if len(password) < 8:
        return False, "Mật khẩu quá ngắn (Yêu cầu hệ thống tối thiểu từ 8 ký tự trở lên)."
    if not any(char.isdigit() for char in password):
        return False, "Mật khẩu bảo mật phải chứa ít nhất một chữ số (0-9)."
    if not any(char.isalpha() for char in password):
        return False, "Mật khẩu bảo mật phải chứa ít nhất một chữ cái (A-Z hoặc a-z)."
    return True, ""

def validate_vietnamese_phone(phone):
    """
    Xác thực số điện thoại di động theo nhà mạng Việt Nam.
    Đầu số chuẩn: 03, 05, 07, 08, 09 kèm theo 8 chữ số phía sau (Tổng 10 số).
    """
    phone = str(phone).strip()
    if not phone:
        return False, "Số điện thoại không được để trống."
    
    # Regex cho các nhà mạng di động Việt Nam hiện hành
    pattern = r"^(03|05|07|08|09)\d{8}$"
    if not re.match(pattern, phone):
        return False, "Số điện thoại không hợp lệ (Yêu cầu 10 chữ số, thuộc đầu số Việt Nam)."
    return True, ""

def validate_fullname(fullname):
    """
    Kiểm tra tính hợp lệ của họ và tên.
    Yêu cầu: Dài từ 2-50 ký tự, không chứa các ký tự số hoặc ký tự đặc biệt vô nghĩa.
    """
    fullname = str(fullname).strip()
    if not fullname:
        return False, "Họ và tên không được để trống."
    if len(fullname) < 2 or len(fullname) > 50:
        return False, "Họ và tên phải có độ dài từ 2 đến 50 ký tự."
    
    # Loại bỏ dấu tiếng Việt trước khi kiểm tra ký tự đặc biệt bằng Regex
    from unicodedata import normalize
    clean_name = normalize('NFKD', fullname).encode('ASCII', 'ignore').decode('ASCII')
    if not re.match(r"^[a-zA-Z\s]+$", clean_name):
        return False, "Họ và tên không được chứa chữ số hoặc ký tự đặc biệt."
    return True, ""


# ==========================================
# 2. KIỂM TRA LÂM SÀNG & SINH HIỆU (CLINICAL)
# ==========================================

def validate_blood_pressure(bp_str):
    """
    Xác thực chuỗi định dạng huyết áp lâm sàng.
    Định dạng yêu cầu: Tâm thu / Tâm trương (Ví dụ: 120/80, 140/90).
    """
    bp_str = str(bp_str).strip()
    if not bp_str:
        return False, "Chỉ số huyết áp không được để trống."
    
    # Regex kiểm tra dạng cấu trúc Số/Số
    pattern = r"^\d{2,3}/\d{2,3}$"
    if not re.match(pattern, bp_str):
        return False, "Sai định dạng huyết áp (Định dạng chuẩn dạng Tâm thu/Tâm trương, ví dụ: 120/80)."
    
    # Phân tách giá trị số để kiểm tra ngưỡng sinh lý cơ bản
    try:
        sys, dia = map(int, bp_str.split('/'))
        if sys < 50 or sys > 250 or dia < 30 or dia > 150:
            return False, "Chỉ số huyết áp vượt quá ngưỡng sinh lý thực tế nguy hiểm."
        if sys <= dia:
            return False, "Huyết áp tâm thu phải lớn hơn huyết áp tâm trương."
    except ValueError:
        return False, "Dữ liệu huyết áp không hợp lệ."
        
    return True, ""

def validate_vitals(temp, heart_rate):
    """
    Kiểm tra các thông số sinh hiệu lâm sàng cơ bản của bệnh nhân.
    Nhiệt độ cơ thể (°C) và Nhịp tim (bpm).
    """
    try:
        temp = float(temp)
        heart_rate = int(heart_rate)
    except (ValueError, TypeError):
        return False, "Dữ liệu sinh hiệu truyền vào phải là định dạng số."
        
    # Kiểm tra ngưỡng giới hạn sinh học an toàn cho phép nhập liệu
    if temp < 34.0 or temp > 43.0:
        return False, "Nhiệt độ cơ thể nằm ngoài phạm vi đo lường lâm sàng lý thuyết (34°C - 43°C)."
    if heart_rate < 30 or heart_rate > 220:
        return False, "Nhịp tim nằm ngoài phạm vi ghi nhận lâm sàng lý thuyết (30 - 220 bpm)."
        
    return True, ""