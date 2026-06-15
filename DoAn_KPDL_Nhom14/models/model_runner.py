# model_runner.py
import pandas as pd
import os
import ast
import pickle
from typing import List, Dict

RULES_PATH = os.path.join(os.path.dirname(__file__), "rules.csv")
INFO_PATH = os.path.join(os.path.dirname(__file__), "disease_info.pkl")

_rules = None
_disease_info = None

def load_rules():
    global _rules
    if _rules is None:
        if not os.path.exists(RULES_PATH):
            raise FileNotFoundError(f"❌ Không tìm thấy {RULES_PATH}. Chạy train_fpgrowth.py trước.")
        df = pd.read_csv(RULES_PATH)
        df['antecedents'] = df['antecedents'].apply(ast.literal_eval)
        df['consequents'] = df['consequents'].apply(ast.literal_eval)
        _rules = df
    return _rules

def load_disease_info():
    global _disease_info
    if _disease_info is None and os.path.exists(INFO_PATH):
        with open(INFO_PATH, 'rb') as f:
            _disease_info = pickle.load(f)
    return _disease_info or {'disease_descriptions': {}, 'disease_precautions': {}}

def predict_diseases(user_symptoms: List[str]) -> Dict[str, float]:
    """
    Dự đoán bệnh từ danh sách triệu chứng.
    Sử dụng strict match và fuzzy match với hệ số phạt.
    Trả về dict {bệnh: xác suất (0-1)}.
    """
    rules = load_rules()
    if not user_symptoms:
        return {}
    user_set = {s.strip().lower() for s in user_symptoms if s.strip()}
    if not user_set:
        return {}
    scores = {}
    ALPHA = 0.7   # hệ số phạt cho fuzzy match
    for _, rule in rules.iterrows():
        antecedents = set(rule['antecedents'])
        consequent = list(rule['consequents'])[0]
        confidence = rule['confidence']
        # Strict match
        if antecedents.issubset(user_set):
            prob = confidence
        else:
            # Fuzzy match
            inter = antecedents.intersection(user_set)
            if not inter:
                continue
            ratio = len(inter) / len(antecedents)
            prob = confidence * (ratio ** ALPHA)
        # Giữ xác suất cao nhất cho mỗi bệnh
        if consequent not in scores or prob > scores[consequent]:
            scores[consequent] = prob
    # Sắp xếp giảm dần
    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

def predict_probability_kdpl(user_symptoms: List[str]) -> Dict[str, float]:
    """Trả về top 3 bệnh với xác suất (%)"""
    preds = predict_diseases(user_symptoms)
    if not preds:
        return {"Không đủ dữ liệu để dự đoán": 0.0}
    top3 = list(preds.items())[:3]
    return {disease: round(prob * 100, 1) for disease, prob in top3}

def get_disease_info(disease_name: str) -> Dict:
    """Lấy mô tả và biện pháp phòng ngừa từ dữ liệu đã lưu"""
    info = load_disease_info()
    disease_lower = disease_name.lower()
    desc = info.get('disease_descriptions', {}).get(disease_lower, "Chưa có mô tả.")
    precautions = info.get('disease_precautions', {}).get(disease_lower, [])
    return {
        'name': disease_name,
        'description': desc,
        'precautions': precautions
    }

def get_top_predictions(user_symptoms: List[str], top_n: int = 3) -> List[Dict]:
    preds = predict_probability_kdpl(user_symptoms)
    results = []
    for disease, prob in list(preds.items())[:top_n]:
        info = get_disease_info(disease)
        results.append({
            'disease': disease,
            'probability': prob,
            'description': info['description'],
            'precautions': info['precautions']
        })
    return results

# Test nhanh
if __name__ == "__main__":
    test = ['ho', 'sốt', 'khó thở']
    print("Dự đoán:", predict_probability_kdpl(test))
    print("Thông tin bệnh:", get_disease_info('viêm phổi'))