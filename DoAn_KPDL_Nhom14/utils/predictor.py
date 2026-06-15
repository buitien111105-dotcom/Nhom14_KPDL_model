import pandas as pd
import os
import re
import streamlit as st
from typing import List, Dict, Set

# ==========================================
# 1. HÀM PHỤ TRỢ (XỬ LÝ CHUỖI TỪ THUẬT TOÁN)
# ==========================================
def parse_frozenset(string_val: str) -> Set[str]:
    """
    Hàm làm sạch và chuyển đổi cấu trúc frozenset({'Ho', 'Sốt'}) 
    của thư viện mlxtend thành cấu trúc Set của Python.
    """
    if pd.isna(string_val):
        return set()
    cleaned = re.sub(r"frozenset\(\{", "", str(string_val))
    cleaned = re.sub(r"\}\)", "", cleaned)
    # Tách chuỗi, loại bỏ khoảng trắng và dấu nháy
    items = [x.strip().strip("'").strip('"') for x in cleaned.split(",") if x.strip()]
    return set(items)

# ==========================================
# 2. NẠP KNOWLEDGE BASE VÀO BỘ NHỚ ĐỆM (RAM)
# ==========================================
@st.cache_data(show_spinner=False, ttl=3600)
def load_knowledge_base() -> pd.DataFrame:
    """
    Tải tập luật Khai phá dữ liệu (Association Rules) vào RAM để tăng tốc.
    Chỉ chạy 1 lần duy nhất hoặc khi file CSV có sự thay đổi.
    """
    rule_file = os.path.join("data", "ket_qua_khai_pha.csv")
    
    if not os.path.exists(rule_file):
        return pd.DataFrame() # Trả về DF rỗng nếu không tìm thấy file

    try:
        df_rules = pd.read_csv(rule_file)
        
        # Tiền xử lý: Dịch sẵn cột antecedents và consequents ngay từ đầu
        # Giúp tiết kiệm hàng triệu chu kỳ CPU khi có nhiều lượt dự đoán
        df_rules['parsed_antecedents'] = df_rules['antecedents'].apply(parse_frozenset)
        df_rules['parsed_consequents'] = df_rules['consequents'].apply(parse_frozenset)
        
        return df_rules
    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu KPDL: {e}")
        return pd.DataFrame()

# ==========================================
# 3. CORE ENGINE: HÀM CHUẨN ĐOÁN (PREDICTOR)
# ==========================================
def predict_probability(selected_symptoms: List[str]) -> Dict[str, float]:
    """
    Động cơ so khớp triệu chứng người dùng với Cây quyết định / Luật KPDL.
    Hỗ trợ 2 cơ chế: Trực tiếp (Strict) và Suy luận mềm (Fuzzy Fallback).
    """
    df_rules = load_knowledge_base()
    
    if df_rules.empty:
        return {"Lỗi: Không tìm thấy Cơ sở tri thức (Knowledge Base)": 0.0}

    user_symptoms = set(selected_symptoms)
    predictions = {}
    partial_matches = {}

    # Quét qua toàn bộ bộ luật
    for _, row in df_rules.iterrows():
        rule_symptoms = row['parsed_antecedents']
        rule_disease = row['parsed_consequents']
        confidence = row['confidence']
        
        if len(rule_symptoms) == 0:
            continue

        # [CƠ CHẾ 1] Strict Match: Trùng khớp hoàn toàn (Luật được kích hoạt tuyệt đối)
        if rule_symptoms.issubset(user_symptoms):
            for disease in rule_disease:
                prob = round(confidence * 100, 1)
                # Lưu xác suất cao nhất nếu bệnh này được suy ra từ nhiều luật
                if disease in predictions:
                    predictions[disease] = max(predictions[disease], prob)
                else:
                    predictions[disease] = prob
                    
        # [CƠ CHẾ 2] Fuzzy Match: Bắt các luật trùng lặp một phần (Dùng làm dự phòng)
        else:
            overlap = rule_symptoms.intersection(user_symptoms)
            if len(overlap) > 0:
                # Tính tỷ lệ trùng khớp (Ví dụ: luật có 3 triệu chứng, người dùng có 2 -> 66%)
                overlap_ratio = len(overlap) / len(rule_symptoms)
                # Phạt (Penalize) độ tin cậy do không khớp hoàn toàn
                adjusted_prob = round(confidence * overlap_ratio * 100 * 0.7, 1) 
                
                for disease in rule_disease:
                    if disease not in partial_matches or adjusted_prob > partial_matches[disease]:
                        partial_matches[disease] = adjusted_prob

    # ==========================================
    # 4. TỔNG HỢP VÀ ĐIỀU HƯỚNG KẾT QUẢ QUYẾT ĐỊNH
    # ==========================================
    
    # Nếu có luật khớp hoàn toàn, ưu tiên trả về danh sách đó
    if predictions:
        sorted_predictions = dict(sorted(predictions.items(), key=lambda item: item[1], reverse=True))
        return dict(list(sorted_predictions.items())[:3])
    
    # Nếu không khớp hoàn toàn, nhưng có luật khớp một phần -> Bật Suy luận mềm
    elif partial_matches:
        # Lọc bỏ các kết quả có xác suất quá thấp (dưới 15%)
        filtered_partial = {k: v for k, v in partial_matches.items() if v >= 15.0}
        
        if filtered_partial:
            sorted_partial = dict(sorted(filtered_partial.items(), key=lambda item: item[1], reverse=True))
            return dict(list(sorted_partial.items())[:3])
            
    # Bó tay (Không có bất kỳ dữ liệu nào liên quan)
    return {"Dữ liệu triệu chứng chưa đủ để AI đưa ra kết luận": 0.0}