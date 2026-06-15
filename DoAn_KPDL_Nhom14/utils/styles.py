import streamlit as st

def load_css():
    """Load CSS Light Glassmorphism Toàn Cục cho CDSS System."""
    st.markdown("""
        <style>
            /* 1. FONT CHỮ VÀ NỀN TOÀN CỤC */
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
            
            html, body, [class*="css"], [class*="st-"] {
                font-family: 'Poppins', sans-serif !important;
                color: #1e293b; /* Chữ xám đậm dễ đọc */
            }
            
            .stApp {
                background-color: #F8FAFC !important;
            }
            
            /* 2. THẺ KÍNH MỜ (Dùng cho Dashboard, Diagnosis...) */
            .stCard, .css-1r6slp0 {
                background: rgba(255, 255, 255, 0.7) !important;
                backdrop-filter: blur(20px) !important;
                -webkit-backdrop-filter: blur(20px) !important;
                border: 1px solid rgba(255, 255, 255, 0.9) !important;
                border-radius: 24px !important;
                padding: 25px !important;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03) !important;
                margin-bottom: 25px !important;
                transition: all 0.3s ease;
            }
            .stCard:hover {
                transform: translateY(-3px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.06) !important;
            }

            /* 3. NÚT BẤM (Đồng bộ Gradient Hồng - Tím) */
            /* Nút Primary (Hành động chính) */
            .stButton > button[kind="primary"] {
                background: linear-gradient(135deg, #E94057 0%, #8A2387 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 12px !important;
                font-weight: 700 !important;
                padding: 8px 20px !important;
                transition: all 0.3s ease !important;
            }
            .stButton > button[kind="primary"]:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 25px rgba(233,64,87,0.3) !important;
            }

            /* Nút Secondary (Hành động phụ) */
            .stButton > button[kind="secondary"] {
                background: transparent !important;
                border: 1px solid #cbd5e1 !important;
                border-radius: 12px !important;
                color: #64748b !important;
                font-weight: 500 !important;
                transition: all 0.3s ease !important;
            }
            .stButton > button[kind="secondary"]:hover {
                border-color: #E94057 !important;
                color: #E94057 !important;
            }

            /* 4. Ô NHẬP LIỆU (Input, Selectbox) */
            .stTextInput > div > div > input, 
            .stNumberInput > div > div > input,
            .stSelectbox > div > div {
                background-color: #ffffff !important;
                border-radius: 12px !important;
                border: 1px solid #cbd5e1 !important;
                padding: 12px !important;
                font-size: 0.95rem !important;
                color: #1e293b !important;
                transition: all 0.3s ease;
                box-shadow: none !important;
            }
            
            /* Viền phát sáng màu hồng khi click vào ô nhập */
            .stTextInput > div > div > input:focus, 
            .stNumberInput > div > div > input:focus,
            .stSelectbox > div > div:focus-within {
                border-color: #E94057 !important;
                box-shadow: 0 0 0 3px rgba(233,64,87,0.15) !important;
            }

            /* 5. GIAO DIỆN SIDEBAR BÊN TRÁI & METRIC */
            [data-testid="stSidebar"] {
                background-color: rgba(255, 255, 255, 0.6) !important;
                backdrop-filter: blur(20px) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.9) !important;
            }
            
            /* Màu số liệu Metric ở trang Dashboard */
            div[data-testid="stMetricValue"] {
                background: linear-gradient(135deg, #E94057 0%, #8A2387 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 2.4rem !important;
                font-weight: 700 !important;
            }
            
            /* Tùy chỉnh thanh cuộn cho mượt */
            ::-webkit-scrollbar { width: 6px; height: 6px; }
            ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
            ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
        </style>
    """, unsafe_allow_html=True)