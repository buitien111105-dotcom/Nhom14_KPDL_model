import streamlit as st
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import requests
from streamlit_lottie import st_lottie
import sys

# Thêm đường dẫn để import từ thư mục models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models'))

# ==========================================
# KẾT NỐI VỚI MÔ HÌNH MACHINE LEARNING MỚI
# ==========================================
try:
    from model_runner import (
        predict_probability_kdpl,
        predict_diseases, 
        get_top_predictions,
        get_disease_info
    )
except ImportError as e:
    st.error(f"❌ Lỗi: Không thể tải mô hình. Chạy train_model.py trước.")
    st.write(f"Chi tiết lỗi: {e}")
    st.stop()

# ==========================================
# 1. CÁC HÀM TRỢ GIÚP (HELPERS)
# ==========================================
def load_lottieurl(url: str):
    """Tải animation Lottie từ URL"""
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def get_symptom_list():
    """Lấy danh sách triệu chứng từ mô hình"""
    try:
        from model_runner import _metadata, load_model
        _, _, metadata = load_model()
        if metadata and 'symptom_encoder_classes' in metadata:
            symptoms = metadata['symptom_encoder_classes']
            # Chuyển về tiếng Việt có khoảng trắng tự nhiên
            return [s.strip().title() for s in symptoms]
    except:
        pass
    
    # Fallback: Danh sách mặc định
    return [
        "Ho", "Sốt", "Đau đầu", "Khó thở", "Buồn nôn", "Đau ngực", "Chóng mặt", "Mệt mỏi",
        "Hắt hơi", "Sổ mũi", "Đau họng", "Tiêu chảy", "Phát ban", "Ngứa", "Ớn lạnh",
        "Đau nhức cơ bắp", "Mất vị giác", "Mất khứu giác", "Đau bụng", "Sụt cân"
    ]

# Kiểm tra trạng thái đăng nhập
if not st.session_state.get('logged_in'):
    st.switch_page("app.py")

# ==========================================
# 2. QUẢN LÝ TRẠNG THÁI (SESSION STATE)
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

# Tải danh sách triệu chứng
ALL_SYMPTOMS = get_symptom_list()

# ==========================================
# 3. GIAO DIỆN CHÍNH (MAIN UI)
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)

col_h1, col_h2, col_h3 = st.columns([3, 1, 1])
with col_h1:
    st.markdown("<h2 style='color: #007BFF; margin-bottom: 0;'>🧠 Hệ thống Chẩn đoán bệnh AI (CDSS)</h2>", unsafe_allow_html=True)
    st.caption("Sử dụng mô hình Machine Learning (Random Forest) để hỗ trợ chẩn đoán lâm sàng từ dữ liệu tiếng Việt.")
with col_h2:
    st.button("🧪 Điền dữ liệu mẫu", on_click=activate_demo, help="Tự động điền dữ liệu để test hệ thống", use_container_width=True)
with col_h3:
    st.button("🔄 Khám ca mới", on_click=reset_form, help="Xóa trắng form nhập liệu", use_container_width=True, type="secondary")

st.markdown("<hr style='margin-top: 5px;'>", unsafe_allow_html=True)

# Chia layout 2 cột: Cột nhập liệu (trái) - Cột kết quả (phải)
col_input, col_result = st.columns([1.1, 1], gap="large")

# --------------------------------------------------
# CỘT TRÁI: FORM HỒ SƠ & TRIỆU CHỨNG
# --------------------------------------------------
with col_input:
    st.markdown("<div class='stCard'>", unsafe_allow_html=True)
    st.markdown("<h4>📋 Hồ sơ sinh hiệu bệnh nhân</h4>", unsafe_allow_html=True)
    
    # Gán giá trị mặc định nếu bật chế độ Demo
    def_name = "Nguyễn Văn Demo" if st.session_state.demo_mode else ""
    def_age = 45 if st.session_state.demo_mode else 25
    def_temp = 39.2 if st.session_state.demo_mode else 37.0
    def_hr = 110 if st.session_state.demo_mode else 75
    def_bp = "140/90" if st.session_state.demo_mode else "120/80"
    
    patient_name = st.text_input("Họ tên bệnh nhân", value=def_name, placeholder="Nhập tên bệnh nhân...")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        age = st.number_input("Tuổi", min_value=1, max_value=120, value=def_age)
    with col_p2:
        gender = st.selectbox("Giới tính", ["Nam", "Nữ", "Khác"])
    with col_p3:
        temp = st.number_input("Nhiệt độ (°C)", min_value=34.0, max_value=42.0, value=def_temp, step=0.1)
        
    col_p4, col_p5 = st.columns(2)
    with col_p4:
        hr = st.number_input("Nhịp tim (bpm)", min_value=40, max_value=200, value=def_hr)
    with col_p5:
        bp = st.text_input("Huyết áp (mmHg)", value=def_bp)

    st.markdown("<br><h4>🤒 Ghi nhận triệu chứng lâm sàng</h4>", unsafe_allow_html=True)
    
    def_symptoms = ["Ho", "Sốt", "Khó thở", "Mất vị giác"] if st.session_state.demo_mode else []
    # Lọc chỉ giữ các triệu chứng có trong ALL_SYMPTOMS (tránh lỗi)
    def_symptoms_filtered = [s for s in def_symptoms if s in ALL_SYMPTOMS]
    selected_symptoms = st.multiselect(
        "Chọn các triệu chứng (Có thể gõ để tìm kiếm):",
        options=ALL_SYMPTOMS,
        default=def_symptoms_filtered,
        placeholder="🔍 Tìm kiếm và chọn triệu chứng..."
    )   
        
    st.markdown("""
        <div style='background-color: #E3F2FD; padding: 10px; border-radius: 8px; font-size: 0.9rem; color: #0056b3; margin-bottom: 15px;'>
            💡 <b>Mẹo:</b> Hệ thống cần ít nhất 2 triệu chứng để đạt độ chính xác cao. Mô hình ML được huấn luyện từ dữ liệu tiếng Việt.
        </div>
    """, unsafe_allow_html=True)
    
    analyze_btn = st.button("🚀 Chạy mô hình phân tích AI", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# CỘT PHẢI: KẾT QUẢ TRẢ VỀ TỪ THUẬT TOÁN
# --------------------------------------------------
with col_result:
    if analyze_btn:
        if not patient_name:
            st.error("⚠️ Khai báo thiếu: Vui lòng nhập tên bệnh nhân.")
        elif len(selected_symptoms) < 2:
            st.warning("⚠️ Cảnh báo: Thuật toán cần ít nhất 2 triệu chứng để dự đoán chính xác.")
        else:
            st.session_state.analysis_done = True
            
            # 1. HIỆU ỨNG TRẠNG THÁI LOADING CHUYÊN NGHIỆP
            status_placeholder = st.empty()
            with status_placeholder.container():
                st.markdown("<div class='stCard' style='text-align:center;'>", unsafe_allow_html=True)
                lottie_scan = load_lottieurl("https://lottie.host/e06b908b-dc5c-43a9-b684-28eab7eb8501/2LMM92uI4W.json")
                if lottie_scan:
                    st_lottie(lottie_scan, height=200)
                
                status_text = st.empty()
                status_text.markdown("🔄 *Đang khởi tạo vector đặc trưng...*")
                time.sleep(0.3)
                status_text.markdown("🤖 *Đang xử lý dữ liệu qua mô hình ML...*")
                time.sleep(0.3)
                status_text.markdown("🧮 *Đang tính toán xác suất dự đoán...*")
                time.sleep(0.3)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Xóa hiệu ứng loading
            status_placeholder.empty()
            
            # 2. GỌI HÀM DỰ ĐOÁN
            # Chuẩn hóa triệu chứng (chuyển về chữ thường cho mô hình)
            normalized_symptoms = [s.strip().lower() for s in selected_symptoms]
            
            try:
                predictions = predict_probability_kdpl(normalized_symptoms)
                if not predictions:
                    st.warning("⚠️ Không thể dự đoán với các triệu chứng này. Vui lòng thử triệu chứng khác.")
                    st.stop()
                
                top_disease = list(predictions.keys())[0]
                top_prob = list(predictions.values())[0]
                
                st.toast("✅ Hoàn tất quá trình phân tích!", icon="✨")
                
            except Exception as e:
                st.error(f"❌ Lỗi khi dự đoán: {e}")
                st.stop()
            
            # 3. HIỂN THỊ UI KẾT QUẢ & CẢNH BÁO SINH HIỆU
            st.markdown("<div class='stCard' style='border-top: 5px solid #00C2A8;'>", unsafe_allow_html=True)
            st.markdown("<h4>🔬 Kết quả chẩn đoán hỗ trợ (AI-Assisted)</h4>", unsafe_allow_html=True)
            
            # Khối phân tích sinh hiệu (Logic thông minh)
            vitals_warnings = []
            if temp >= 38.5:
                vitals_warnings.append(f"🌡️ Sốt cao ({temp}°C)")
            elif temp < 36.0:
                vitals_warnings.append(f"❄️ Hạ thân nhiệt ({temp}°C)")
            
            if hr > 100:
                vitals_warnings.append(f"💓 Nhịp tim nhanh ({hr} bpm)")
            elif hr < 60:
                vitals_warnings.append(f"💤 Nhịp tim chậm ({hr} bpm)")
            
            try:
                sys_bp, dia_bp = map(int, bp.split('/'))
                if sys_bp >= 140 or dia_bp >= 90:
                    vitals_warnings.append(f"📈 Huyết áp cao ({bp})")
                elif sys_bp <= 90 or dia_bp <= 60:
                    vitals_warnings.append(f"📉 Huyết áp thấp ({bp})")
            except:
                pass  # Bỏ qua nếu nhập sai định dạng huyết áp

            if vitals_warnings:
                st.error(f"🚨 **Cảnh báo sinh hiệu bất thường:** {', '.join(vitals_warnings)}")
            else:
                st.success("✅ Sinh hiệu bệnh nhân nằm trong mức ổn định.")

            # Biểu đồ Gauge (Tốc độ kế)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=top_prob,
                title={'text': f"<span style='font-size:1.2em; color:#DC3545'>{top_disease.upper()}</span><br><span style='font-size:0.8em; color:gray'>Xác suất cao nhất</span>"},
                number={'suffix': "%", 'font': {'size': 35, 'color': '#DC3545'}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#DC3545"},
                    'steps': [
                        {'range': [0, 40], 'color': "#E8F5E9"},
                        {'range': [40, 75], 'color': "#FFF3CD"},
                        {'range': [75, 100], 'color': "#F8D7DA"}
                    ],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}
                }
            ))
            fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Differential Diagnosis (Bệnh lý phân biệt)
            if len(predictions) > 1:
                with st.expander("🔍 Các khả năng bệnh lý khác (Differential Diagnosis)"):
                    df_prob = pd.DataFrame({
                        'Bệnh lý': list(predictions.keys())[1:],
                        'Xác suất (%)': list(predictions.values())[1:]
                    })
                    fig_bar = px.bar(
                        df_prob, x='Xác suất (%)', y='Bệnh lý', 
                        orientation='h', 
                        color='Xác suất (%)',
                        color_continuous_scale='Blues'
                    )
                    fig_bar.update_layout(
                        height=200,
                        margin=dict(l=10, r=10, t=10, b=10),
                        showlegend=False,
                        yaxis_title="",
                        xaxis_title="Xác suất (%)"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
            
            # Lấy thông tin chi tiết về bệnh chính
            try:
                disease_info = get_disease_info(top_disease)
                
                # Hiển thị mô tả bệnh
                if disease_info.get('description'):
                    with st.expander("📖 Thông tin về bệnh"):
                        st.write(disease_info['description'])
                
                # Hiển thị lệnh khuyên
                if disease_info.get('precautions'):
                    st.info(f"""
                    **💊 Lệnh khuyên & Hướng dẫn:**
                    - {chr(10).join(['✓ ' + p for p in disease_info['precautions']])}
                    """)
            except Exception as e:
                pass
            
            # Khung Khuyến nghị
            st.info(f"""
            **🔔 Khuyến nghị cho Bệnh nhân {patient_name}:**
            - 🏥 Kết quả dự đoán: **{top_disease}** ({top_prob:.1f}% độ tin cậy)
            - ⚠️ **Lưu ý**: Hệ thống AI chỉ mang tính chất hỗ trợ, quyết định chẩn đoán và điều trị cuối cùng thuộc về Bác sĩ lâm sàng.
            - 📋 Vui lòng tiến hành các xét nghiệm bổ sung nếu cần thiết.
            """)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 4. GHI NHẬN LỊCH SỬ VÀO DATABASE
            history_file = os.path.join("data", "diagnosis_history.csv")

            # Chuẩn bị dữ liệu cho dòng mới
            new_row = {
                "Ngày": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Bệnh nhân": patient_name,
                "Triệu chứng": ", ".join(selected_symptoms),
                "Kết quả": top_disease,
                "Độ tin cậy": f"{top_prob:.1f}%",
                "Tuổi": age,
                "Giới tính": gender,
                "Nhiệt độ": temp,
                "Nhịp tim": hr,
                "Huyết áp": bp
            }

            # Nếu file chưa tồn tại -> tạo mới với header đầy đủ
            if not os.path.exists(history_file):
                df_new = pd.DataFrame([new_row])
                df_new.to_csv(history_file, index=False, encoding='utf-8-sig')
            else:
                # Đọc file hiện tại, giữ nguyên header
                df_existing = pd.read_csv(history_file, encoding='utf-8-sig')
                # Thêm dòng mới (pandas tự động align theo cột)
                df_existing = pd.concat([df_existing, pd.DataFrame([new_row])], ignore_index=True)
                df_existing.to_csv(history_file, index=False, encoding='utf-8-sig')
                
    elif not st.session_state.analysis_done:
        # TRẠNG THÁI CHỜ MẶC ĐỊNH
        st.markdown("""
        <div class='stCard' style='text-align: center; color: #999; padding: 60px 20px;'>
            <h3 style='color: #555;'>📊 Hệ thống đang chờ dữ liệu</h3>
            <p>Vui lòng khai báo sinh hiệu và triệu chứng bệnh nhân<br>bên cột trái để tiến hành phân tích.</p>
        </div>
        """, unsafe_allow_html=True)