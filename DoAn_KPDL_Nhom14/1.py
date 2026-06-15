import pandas as pd
import ast
import os

# Đọc file luật
rules_path = "models/ket_qua_khai_pha.csv"
if not os.path.exists(rules_path):
    rules_path = "ket_qua_khai_pha.csv"
    
if not os.path.exists(rules_path):
    print("❌ Không tìm thấy file ket_qua_khai_pha.csv")
    exit()

rules = pd.read_csv(rules_path)
print(f"Tổng số luật: {len(rules)}")

if len(rules) == 0:
    print("⚠️ Không có luật nào. Hãy giảm min_support hoặc min_confidence.")
else:
    # Hiển thị 10 luật đầu
    print("\n10 luật đầu tiên:")
    for i in range(min(10, len(rules))):
        ante = ast.literal_eval(rules.loc[i, 'antecedents'])
        conse = ast.literal_eval(rules.loc[i, 'consequents'])
        print(f"  {ante} → {conse} (conf={rules.loc[i, 'confidence']:.3f})")
    
    # Thống kê các bệnh xuất hiện trong hệ quả
    from collections import Counter
    conse_list = []
    for conse_str in rules['consequents']:
        conse = ast.literal_eval(conse_str)
        conse_list.append(list(conse)[0])
    counter = Counter(conse_list)
    print("\nPhân bố bệnh trong hệ quả:")
    for disease, count in counter.most_common(10):
        print(f"  {disease}: {count} luật")