import os
import sys
import subprocess

def check_requirements():
    print("=" * 70)
    print("🔍 KIỂM TRA THƯ VIỆN CẦN THIẾT")
    print("=" * 70)
    
    required_packages = [
        'pandas',
        'numpy',
        'scikit-learn',
        'imblearn',
        'streamlit',
        'plotly',
        'streamlit-lottie'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - CHƯA CÀI ĐẶT")
            missing_packages.append(package)
    
    if missing_packages:
        print("\n⚠️ CẢNH BÁO: Các thư viện sau chưa được cài đặt:")
        print(f"   {', '.join(missing_packages)}")
        print("\n💡 Chạy lệnh sau để cài đặt:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("\n✨ Tất cả thư viện đã sẵn sàng!")
    return True

def check_data_files():
    print("\n" + "=" * 70)
    print("📂 KIỂM TRA DỮ LIỆU")
    print("=" * 70)
    
    data_dir = "data"
    required_files = [
        "vn_dataset.csv",
        "vn_symptom_Description.csv",
        "vn_symptom_precaution.csv",
        "vn_Symptom-severity.csv"
    ]
    
    all_exist = True
    for file in required_files:
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"✅ {file} ({size_mb:.2f} MB)")
        else:
            print(f"❌ {file} - KHÔNG TÌM THẤY")
            all_exist = False
    
    if not all_exist:
        print("\n⚠️ CẢNH BÁO: Một số file dữ liệu chưa tồn tại!")
        return False
    
    print("\n✨ Tất cả dữ liệu đã sẵn sàng!")
    return True

def train_model():
    print("\n" + "=" * 70)
    print("🤖 HUẤN LUYỆN MÔ HÌNH")
    print("=" * 70)
    
    print("\n📍 Chạy: python models/train_model.py\n")
    
    result = subprocess.run(
        [sys.executable, "models/train_model.py"],
        cwd=os.getcwd()
    )
    
    if result.returncode == 0:
        print("\n✨ Huấn luyện hoàn tất thành công!")
        return True
    else:
        print("\n❌ Lỗi khi huấn luyện mô hình!")
        return False

def verify_model():
    print("\n" + "=" * 70)
    print("✔️ KIỂM TRA MÔ HÌNH")
    print("=" * 70)
    
    model_files = [
        "models/disease_model.pkl",
        "models/symptom_encoder.pkl",
        "models/model_metadata.pkl"
    ]
    
    all_exist = True
    for file in model_files:
        if os.path.exists(file):
            size_mb = os.path.getsize(file) / (1024 * 1024)
            print(f"✅ {file} ({size_mb:.2f} MB)")
        else:
            print(f"❌ {file} - KHÔNG TÌM THẤY")
            all_exist = False
    
    if not all_exist:
        print("\n❌ Mô hình chưa được huấn luyện!")
        return False
    
    print("\n✨ Mô hình đã sẵn sàng!")
    return True

def main():
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🏥 HỆ THỐNG CHẨN ĐOÁN BỆ NH VỚI AI (Medical Diagnosis CDSS)".center(68) + "║")
    print("║" + "  Dự đoán bệnh từ triệu chứng - Dữ liệu Tiếng Việt".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    if not check_requirements():
        print("\n❌ Vui lòng cài đặt các thư viện cần thiết trước!")
        sys.exit(1)

    if not check_data_files():
        print("\n❌ Vui lòng đảm bảo tất cả file dữ liệu đã tồn tại!")
        sys.exit(1)

    if not verify_model():
        print("\n⚠️ Mô hình chưa được huấn luyện. Bắt đầu quá trình huấn luyện...")
        if not train_model():
            sys.exit(1)
    else:
        print("\n💬 Mô hình đã tồn tại. Bạn có muốn huấn luyện lại? (y/n)")
        choice = input("→ ").strip().lower()
        if choice == 'y':
            if not train_model():
                sys.exit(1)

    print("\n" + "=" * 70)
    print("🚀 KHỞI ĐỘNG ỨNG DỤNG STREAMLIT")
    print("=" * 70)
    print("\n💡 Ứng dụng sẽ mở trên trình duyệt: http://localhost:8501")
    print("\n📍 Chạy: streamlit run app.py\n")
    
    os.system("streamlit run app.py")

if __name__ == "__main__":
    main()
