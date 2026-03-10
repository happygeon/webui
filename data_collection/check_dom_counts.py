import json

with open("dom_counts.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 각 항목(폴더 수) 출력
print("structure 폴더 개수:", len(data["structure"]))
print("structure_simplified 폴더 개수:", len(data["structure_simplified"]))
