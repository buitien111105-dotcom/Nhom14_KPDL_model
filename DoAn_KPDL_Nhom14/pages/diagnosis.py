import streamlit as st
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, 'models'))

# ==========================================
# IMPORT CẢ HAI MÔ HÌNH
# ==========================================
try:
    from model_runner_fp import (
        predict_probability_kdpl,
        get_disease_info,
        get_all_symptoms
    )
    model_ready = True
except ImportError as e:
    st.error(f"❌ Lỗi: Không thể tải mô hình FP-Growth. Vui lòng chạy train_fpgrowth.py trước.")
    st.write(f"Chi tiết: {e}")
    st.stop()

# ==========================================
# HÀM LẤY DANH SÁCH TRIỆU CHỨNG
# ==========================================
def get_symptom_list_from_model():
    """Lấy danh sách triệu chứng từ mô hình hiện tại (FP-Growth hoặc RF)"""
    # Thử lấy từ FP-Growth trước
    try:
        from model_runner_fp import get_all_symptoms as fpg_symptoms
        syms = fpg_symptoms()
        if syms:
            return sorted([s.title() for s in syms])
    except:
        pass
    # Thử lấy từ RF encoder
    try:
        from model_runner_rf import load_rf_model
        _, mlb, _ = load_rf_model()
        syms = mlb.classes_
        if len(syms) > 0:
            return sorted([s.title() for s in syms])
    except:
        pass
    # Fallback: đọc từ dataset
    dataset_path = os.path.join(os.path.dirname(__file__), 'data', 'vn_dataset.csv')
    if os.path.exists(dataset_path):
        df = pd.read_csv(dataset_path, nrows=100)
        symptom_cols = [f'Symptom_{i}' for i in range(1, 18)]
        all_syms = set()
        for col in symptom_cols:
            vals = df[col].dropna().unique()
            all_syms.update([str(v).strip() for v in vals if v != ''])
        return sorted([s.title() for s in all_syms])
    return ["Ho", "Sốt", "Đau đầu", "Khó thở", "Buồn nôn"]

# ==========================================
# KIỂM TRA ĐĂNG NHẬP
# ==========================================
if not st.session_state.get('logged_in'):
    st.switch_page("app.py")   # app.py nằm cùng cấp với pages, nên dùng tên file

# ==========================================
# SESSION STATE
# ==========================================
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

def activate_demo():
    st.session_state.demo_mode = True
    st.session_state.analysis_done = False

def reset_form():
    st.session_state.demo_mode = False
    st.session_state.analysis_done = False

ALL_SYMPTOMS = get_symptom_list_from_model()

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
col_h1, col_h2, col_h3 = st.columns([3, 1, 1])
with col_h1:
    st.markdown(f"<h2 style='color: #007BFF;'>🧠 Hệ thống Chẩn đoán bệnh AI (CDSS) - {model_ready}</h2>", unsafe_allow_html=True)
    st.caption("Nhập triệu chứng và sinh hiệu. Mô hình sẽ dự đoán bệnh lý có khả năng cao nhất.")
with col_h2:
    st.button("🧪 Dữ liệu mẫu", on_click=activate_demo)
with col_h3:
    st.button("🔄 Khám mới", on_click=reset_form)

st.markdown("<hr>", unsafe_allow_html=True)
col_input, col_result = st.columns([1.1, 1], gap="large")

# --------------------------------------------------
# CỘT NHẬP LIỆU
# --------------------------------------------------
with col_input:
    st.markdown("#### 📋 Hồ sơ bệnh nhân")
    def_name = "Nguyễn Văn Demo" if st.session_state.demo_mode else ""
    def_age = 45 if st.session_state.demo_mode else 25
    def_temp = 39.2 if st.session_state.demo_mode else 37.0
    def_hr = 110 if st.session_state.demo_mode else 75
    def_bp = "140/90" if st.session_state.demo_mode else "120/80"

    patient_name = st.text_input("Họ tên", value=def_name)
    col1, col2, col3 = st.columns(3)
    with col1: age = st.number_input("Tuổi", 1, 120, def_age)
    with col2: gender = st.selectbox("Giới tính", ["Nam", "Nữ", "Khác"])
    with col3: temp = st.number_input("Nhiệt độ (°C)", 34.0, 42.0, def_temp, 0.1)
    col4, col5 = st.columns(2)
    with col4: hr = st.number_input("Nhịp tim (bpm)", 40, 200, def_hr)
    with col5: bp = st.text_input("Huyết áp (mmHg)", def_bp)

    st.markdown("#### 🤒 Triệu chứng")
    def_symptoms = ["Ho", "Sốt", "Khó thở", "Mất vị giác"] if st.session_state.demo_mode else []
    selected = st.multiselect("Chọn triệu chứng:", ALL_SYMPTOMS, default=[s for s in def_symptoms if s in ALL_SYMPTOMS])
    analyze = st.button("🚀 Phân tích", type="primary", use_container_width=True)

# --------------------------------------------------
# CỘT KẾT QUẢ
# --------------------------------------------------
with col_result:
    if analyze:
        if not patient_name:
            st.error("Nhập tên bệnh nhân")
        elif len(selected) < 2:
            st.warning("Cần ít nhất 2 triệu chứng")
        else:
            with st.spinner("Đang phân tích..."):
                time.sleep(0.5)
                normalized = [s.lower().strip() for s in selected]
                preds = predict_probability_kdpl(normalized)
                if not preds or "Không đủ" in list(preds.keys())[0]:
                    st.error("Không thể dự đoán, hãy thử triệu chứng khác")
                    st.stop()
                top_disease = list(preds.keys())[0]
                top_prob = list(preds.values())[0]

            # Cảnh báo sinh hiệu
            warns = []
            if temp >= 38.5: warns.append(f"Sốt cao ({temp}°C)")
            if hr > 100: warns.append(f"Nhịp tim nhanh ({hr})")
            try:
                s, d = map(int, bp.split('/'))
                if s >= 140 or d >= 90: warns.append(f"Huyết áp cao ({bp})")
            except:
                pass
            if warns:
                st.error("🚨 Cảnh báo: " + ", ".join(warns))
            else:
                st.success("✅ Sinh hiệu ổn định")

            # Gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=top_prob,
                title={"text": f"<b>{top_disease}</b><br>Xác suất"},
                number={"suffix": "%", "font": {"size": 25}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#DC3545"},
                    "steps": [
                        {"range": [0, 40], "color": "#E8F5E9"},
                        {"range": [40, 75], "color": "#FFF3CD"},
                        {"range": [75, 100], "color": "#F8D7DA"}
                    ]
                }
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)

            # Các bệnh khác
            if len(preds) > 1:
                with st.expander("🔍 Bệnh lý phân biệt"):
                    df_other = pd.DataFrame({"Bệnh": list(preds.keys())[1:], "Xác suất %": list(preds.values())[1:]})
                    st.bar_chart(df_other.set_index("Bệnh"))

            # Thông tin bệnh
            info = get_disease_info(top_disease)
            if info.get('description'):
                with st.expander("📖 Mô tả bệnh"):
                    st.write(info['description'])
            if info.get('precautions'):
                st.info("💊 **Lệnh khuyên:**\n- " + "\n- ".join(info['precautions']))

            st.info(f"🔔 **Kết luận:** {top_disease} ({top_prob:.1f}%)\n⚠️ Kết quả chỉ mang tính tham khảo, không thay thế bác sĩ.")

            # Lưu lịch sử
            os.makedirs(os.path.join(parent_dir, 'data'), exist_ok=True)
            history_file = os.path.join(parent_dir, 'data', 'diagnosis_history.csv')
            new_row = {
                "Ngày": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Bệnh nhân": patient_name,
                "Triệu chứng": ", ".join(selected),
                "Kết quả": top_disease,
                "Độ tin cậy": f"{top_prob:.1f}%",
                "Tuổi": age,
                "Giới tính": gender,
                "Nhiệt độ": temp,
                "Nhịp tim": hr,
                "Huyết áp": bp,
                "Mô hình": model_ready
            }
            if not os.path.exists(history_file):
                pd.DataFrame([new_row]).to_csv(history_file, index=False, encoding='utf-8-sig')
            else:
                df_hist = pd.read_csv(history_file, encoding='utf-8-sig')
                df_hist = pd.concat([df_hist, pd.DataFrame([new_row])], ignore_index=True)
                df_hist.to_csv(history_file, index=False, encoding='utf-8-sig')

    else:
        st.markdown("""
        <div style='text-align:center; padding:60px 20px; color:gray;'>
            <h3>📊 Chờ dữ liệu</h3>
            <p>Nhập thông tin bệnh nhân và triệu chứng bên trái, sau đó nhấn "Phân tích".</p>
        </div>
        """, unsafe_allow_html=True)