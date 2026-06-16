import pandas as pd
import os
import ast
import pickle
from typing import List, Dict

RULES_PATH = os.path.join(os.path.dirname(__file__), "ket_qua_khai_pha.csv")
INFO_PATH = os.path.join(os.path.dirname(__file__), "disease_info.pkl")

_rules = None
_disease_info = None
_all_symptoms = None

def load_rules():
    global _rules
    if _rules is None:
        if not os.path.exists(RULES_PATH):
            raise FileNotFoundError(f"Không tìm thấy {RULES_PATH}. Hãy chạy train_fpgrowth.py trước.")
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

def get_all_symptoms() -> List[str]:
    global _all_symptoms
    if _all_symptoms is not None:
        return _all_symptoms

    # Thử lấy từ metadata
    info = load_disease_info()
    if 'all_symptoms' in info:
        _all_symptoms = info['all_symptoms']
        return _all_symptoms

    # Fallback: trích xuất từ luật (các item không phải DISEASE_)
    rules = load_rules()
    sym_set = set()
    for _, row in rules.iterrows():
        for sym in row['antecedents']:
            if isinstance(sym, str) and not sym.startswith("DISEASE_"):
                sym_set.add(sym)
    _all_symptoms = sorted(sym_set)
    return _all_symptoms

def predict_diseases(user_symptoms: List[str]) -> Dict[str, float]:
    rules = load_rules()
    if not user_symptoms:
        return {}
    user_set = {s.strip().lower() for s in user_symptoms if s.strip()}
    if not user_set:
        return {}

    ALPHA = 0.7
    scores = {}
    for _, rule in rules.iterrows():
        antecedents = set(rule['antecedents'])
        consequents = rule['consequents']
        if not consequents:
            continue
        consequent_full = consequents[0]
        if not consequent_full.startswith("DISEASE_"):
            continue
        disease_name = consequent_full[8:]
        confidence = rule['confidence']

        if antecedents.issubset(user_set):
            prob = confidence
        else:
            inter = antecedents.intersection(user_set)
            if not inter:
                continue
            ratio = len(inter) / len(antecedents)
            prob = confidence * (ratio ** ALPHA)

        if disease_name not in scores or prob > scores[disease_name]:
            scores[disease_name] = prob

    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

def predict_probability_kdpl(user_symptoms: List[str]) -> Dict[str, float]:
    preds = predict_diseases(user_symptoms)
    if not preds:
        return {"Không đủ dữ liệu để dự đoán": 0.0}
    top3 = list(preds.items())[:3]
    return {disease: round(prob * 100, 1) for disease, prob in top3}

def get_disease_info(disease_name: str) -> Dict:
    info = load_disease_info()
    disease_lower = disease_name.lower()
    desc = info.get('disease_descriptions', {}).get(disease_lower, "Chưa có mô tả.")
    precautions = info.get('disease_precautions', {}).get(disease_lower, [])
    return {'name': disease_name, 'description': desc, 'precautions': precautions}

def get_top_predictions(user_symptoms: List[str], top_n: int = 3) -> List[Dict]:
    preds = predict_probability_kdpl(user_symptoms)
    results = []
    for disease, prob in list(preds.items())[:top_n]:
        info = get_disease_info(disease)
        results.append({'disease': disease, 'probability': prob, 'description': info['description'], 'precautions': info['precautions']})
    return results

if __name__ == "__main__":
    test = ['ho', 'sốt','khó thở']
    print("Test:", test, "->", predict_probability_kdpl(test))