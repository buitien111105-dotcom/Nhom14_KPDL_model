import pandas as pd
import os
import pickle
from mlxtend.frequent_patterns import fpgrowth
from collections import defaultdict

# ======================================================================
# CẤU HÌNH ĐƯỜNG DẪN
# ======================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(DATA_DIR, "vn_dataset.csv")
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

# 2. Tập hợp triệu chứng
all_symptoms = set()
for col in symptom_cols:
    vals = df[col].dropna().unique()
    all_symptoms.update([str(v).strip().lower() for v in vals if v != ''])
all_symptoms = sorted(all_symptoms)
print(f"   Số triệu chứng: {len(all_symptoms)}")

# 3. Tạo ma trận one-hot (thêm tiền tố DISEASE_ cho bệnh)
diseases_unique = df['Disease'].str.lower().unique()
all_items = list(all_symptoms) + [f"DISEASE_{d}" for d in diseases_unique]

onehot_list = []
for idx, row in df.iterrows():
    trans = set()
    for col in symptom_cols:
        val = row[col]
        if pd.notna(val) and str(val).strip() != '':
            trans.add(str(val).strip().lower())
    disease = str(row['Disease']).strip().lower()
    trans.add(f"DISEASE_{disease}")
    vec = {item: 1 if item in trans else 0 for item in all_items}
    onehot_list.append(vec)

onehot_df = pd.DataFrame(onehot_list).astype(bool)
print(f"   Ma trận kích thước: {onehot_df.shape}")

# 4. Khai phá tập phổ biến
min_support = 0.02  # vì mỗi bệnh có support ~120/4920=0.0244
print(f"\n📊 Khai phá tập phổ biến với min_support = {min_support}...")
frequent_itemsets = fpgrowth(onehot_df, min_support=min_support, use_colnames=True)
print(f"   Số tập phổ biến: {len(frequent_itemsets)}")

# 5. Tự sinh luật kết hợp
min_confidence = 0.6
print(f"\n🔗 Tự sinh luật kết hợp (min_confidence = {min_confidence})...")

# Tạo dict tra cứu support nhanh
support_dict = {frozenset(itemset): supp for itemset, supp in zip(frequent_itemsets['itemsets'], frequent_itemsets['support'])}

rules_list = []
for idx, row in frequent_itemsets.iterrows():
    itemset = row['itemsets']
    supp_itemset = row['support']
    # Tìm các bệnh trong itemset
    diseases_in_itemset = [item for item in itemset if item.startswith("DISEASE_")]
    if not diseases_in_itemset:
        continue
    for disease in diseases_in_itemset:
        antecedent = itemset - {disease}
        if not antecedent:
            continue
        # Tìm support của antecedent
        antecedent_key = frozenset(antecedent)
        supp_antecedent = support_dict.get(antecedent_key, 0)
        if supp_antecedent == 0:
            continue
        confidence = supp_itemset / supp_antecedent
        if confidence < min_confidence:
            continue
        # Tính lift: supp(antecedent ∪ disease) / (supp(antecedent)*supp(disease))
        supp_disease = support_dict.get(frozenset([disease]), 0)
        if supp_disease > 0:
            lift = supp_itemset / (supp_antecedent * supp_disease)
        else:
            lift = 1.0
        rules_list.append({
            'antecedents': antecedent,
            'consequents': {disease},
            'support': supp_itemset,
            'confidence': confidence,
            'lift': lift
        })

if rules_list:
    rules = pd.DataFrame(rules_list)
    rules = rules.sort_values('confidence', ascending=False)
    # Chuyển sang list để lưu CSV
    rules['antecedents'] = rules['antecedents'].apply(list)
    rules['consequents'] = rules['consequents'].apply(list)
    print(f"   Số luật hữu ích: {len(rules)}")
else:
    print("   ⚠️ Không có luật nào. Hãy giảm min_support hoặc min_confidence.")
    rules = pd.DataFrame(columns=['antecedents', 'consequents', 'support', 'confidence', 'lift'])

# Lưu luật
os.makedirs(MODEL_DIR, exist_ok=True)
rules.to_csv(RULES_PATH, index=False)
print(f"✅ Đã lưu luật vào: {RULES_PATH}")

# 6. Lưu metadata
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
        precautions = [str(row[c]).strip() for c in ['Precaution_1','Precaution_2','Precaution_3','Precaution_4'] 
                       if pd.notna(row[c]) and str(row[c]).strip()!='']
        prec_dict[disease] = precautions

metadata = {
    'disease_descriptions': desc_dict,
    'disease_precautions': prec_dict,
    'min_support': min_support,
    'min_confidence': min_confidence,
    'num_rules': len(rules),
    'all_symptoms': all_symptoms  
}
with open(INFO_PATH, 'wb') as f:
    pickle.dump(metadata, f)
print(f"✅ Đã lưu metadata vào: {INFO_PATH}")

print("\n" + "="*60)
print(f"✨ HUẤN LUYỆN HOÀN TẤT! {len(rules)} luật được sinh ra.")
print("="*60)