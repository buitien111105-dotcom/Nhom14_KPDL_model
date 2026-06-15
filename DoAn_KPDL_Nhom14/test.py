import numpy as np
import pickle
import os
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "disease_model.pkl")
TEST_X_PATH = os.path.join(MODEL_DIR, "X_test.npy")
TEST_Y_PATH = os.path.join(MODEL_DIR, "y_test.npy")

def main():
    if not os.path.exists(TEST_X_PATH) or not os.path.exists(TEST_Y_PATH):
        print("Chưa có tập test. Hãy chạy train_model.py để tạo và lưu tập test.")
        return

    print("Đang tải mô hình...")
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print("Đã tải mô hình.")

    X_test = np.load(TEST_X_PATH)
    y_test = np.load(TEST_Y_PATH, allow_pickle=True)

    print(f"Kích thước tập test: {X_test.shape[0]} mẫu, {X_test.shape[1]} đặc trưng")

    print("Đang dự đoán...")
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print("\n" + "="*60)
    print("KẾT QUẢ ĐÁNH GIÁ TRÊN TẬP TEST (ĐỘC LẬP)")
    print(f"Accuracy : {acc:.4f} ({acc*100:.2f}%)")
    print("="*60)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, digits=4, zero_division=0))

if __name__ == "__main__":
    main()