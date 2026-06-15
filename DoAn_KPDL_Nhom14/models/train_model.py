import pandas as pd
import os
import pickle
from mlxtend.frequent_patterns import fpgrowth, association_rules

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(DATA_DIR, "vn_dataset.csv")   # hoặc dataset.csv
RULES_PATH = os.path.join(MODEL_DIR, "ket_qua_khai_pha.csv")
INFO_PATH = os.path.join(MODEL_DIR, "disease_info.pkl")
DESC_PATH = os.path.join(DATA_DIR, "symptom_Description.csv")
PRECAUTION_PATH = os.path.join(DATA_DIR, "symptom_precaution.csv")

print("="*60)
print("🚀 BẮT ĐẦU HUẤN LUYỆN FP-GROWTH")
print("="*60)

# 1. Đọc dữ liệu
df = pd.read_csv(DATASET_PATH)
print(f"\n📖 Số dòng: {df.shape[0]}, Số cột: {df.shape[1]}")

symptom_cols = [f'Symptom_{i}' for i in range(1, 18)]

# 2. Tập hợp các triệu chứng (không bao gồm bệnh)
all_symptoms = set()
for col in symptom_cols:
    vals = df[col].dropna().unique()
    all_symptoms.update([str(v).strip().lower() for v in vals if v != ''])
all_symptoms = sorted(all_symptoms)
print(f"   Số triệu chứng: {len(all_symptoms)}")

# 3. Tạo ma trận one-hot, trong đó bệnh được thêm tiền tố "DISEASE_"
onehot_list = []
for idx, row in df.iterrows():
    trans = set()
    # Thêm triệu chứng
    for col in symptom_cols:
        val = row[col]
        if pd.notna(val) and str(val).strip() != '':
            trans.add(str(val).strip().lower())
    # Thêm bệnh (có tiền tố để phân biệt)
    disease = str(row['Disease']).strip().lower()
    trans.add(f"DISEASE_{disease}")
    # Tạo vector nhị phân cho tất cả các mục (triệu chứng + bệnh đã prefix)
    all_items = list(all_symptoms) + [f"DISEASE_{d}" for d in df['Disease'].str.lower().unique()]
    vec = {item: 1 if item in trans else 0 for item in all_items}
    onehot_list.append(vec)

onehot_df = pd.DataFrame(onehot_list).astype(bool)
print(f"   Ma trận kích thước: {onehot_df.shape}")

# 4. Khai phá tập phổ biến
min_support = 0.02
print(f"\n📊 Khai phá tập phổ biến với min_support = {min_support}...")
frequent_itemsets = fpgrowth(onehot_df, min_support=min_support, use_colnames=True)
print(f"   Số tập phổ biến: {len(frequent_itemsets)}")

# 5. Sinh luật kết hợp
min_confidence = 0.8
print(f"\n🔗 Sinh luật kết hợp (min_confidence = {min_confidence})...")
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)

# Chỉ giữ luật có hệ quả là 1 bệnh (có tiền tố DISEASE_)
rules = rules[rules['consequents'].apply(lambda x: len(x) == 1)]
rules = rules[rules['consequents'].apply(lambda x: list(x)[0].startswith("DISEASE_"))]
rules = rules[rules['lift'] > 1]

# Chuyển antecedents và consequents thành list để lưu CSV
rules['antecedents'] = rules['antecedents'].apply(list)
rules['consequents'] = rules['consequents'].apply(list)

# Sắp xếp theo confidence giảm dần
rules = rules.sort_values('confidence', ascending=False)
print(f"   Số luật hữu ích: {len(rules)}")

# Lưu luật
rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].to_csv(RULES_PATH, index=False)
print(f"✅ Đã lưu luật vào: {RULES_PATH}")

# 6. Lưu metadata (mô tả bệnh, phòng ngừa) - lưu ý bỏ tiền tố khi tra cứu
desc_dict = {}
if os.path.exists(DESC_PATH):
    desc_df = pd.read_csv(DESC_PATH)
    for _, row in desc_df.iterrows():
        disease = str(row['Disease']).lower()
        desc = str(row['Description']) if pd.notna(row['Description']) else ""
        desc_dict[disease] = desc

prec_dict = {}
if os.path.exists(PRECAUTION_PATH):
    prec_df = pd.read_csv(PRECAUTION_PATH)
    for _, row in prec_df.iterrows():
        disease = str(row['Disease']).lower()
        precautions = [str(row[c]).strip() for c in ['Precaution_1','Precaution_2','Precaution_3','Precaution_4'] if pd.notna(row[c]) and str(row[c]).strip()!='']
        prec_dict[disease] = precautions

metadata = {
    'disease_descriptions': desc_dict,
    'disease_precautions': prec_dict,
    'min_support': min_support,
    'min_confidence': min_confidence,
    'num_rules': len(rules)
}
with open(INFO_PATH, 'wb') as f:
    pickle.dump(metadata, f)
print(f"✅ Đã lưu metadata vào: {INFO_PATH}")

print("\n" + "="*60)
print(f"✨ HUẤN LUYỆN HOÀN TẤT! {len(rules)} luật được sinh ra.")
print("="*60)