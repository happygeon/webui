import os
import csv
from transformers import AutoTokenizer

# 1) HF 토크나이저 로드 (예: 7B‑Instruct 모델)
tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen2.5-7B-Instruct",  # ← 정확한 모델 아이디
    trust_remote_code=True,
    # private repo 접근이 필요할 경우:
    # use_auth_token=True
)

root_dir = "./feedally"
output_csv = "feedally_qwen25_token_counts.csv"

with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "filename",
        "react_1_tokens",
        "react_2_tokens",
        "react_3_tokens",
        "average_tokens"
    ])

    for folder in sorted(os.listdir(root_dir)):
        folder_path = os.path.join(root_dir, folder)
        if not os.path.isdir(folder_path):
            continue

        counts = [None, None, None]
        for idx in range(3):
            fname = f"react_{idx+1}.html"
            fpath = os.path.join(folder_path, fname)
            if os.path.isfile(fpath):
                html = open(fpath, encoding="utf-8").read()
                tokens = tokenizer(html, add_special_tokens=False)
                counts[idx] = len(tokens["input_ids"])
            else:
                print(f"⚠️ '{fpath}' 없음, 건너뜁니다.")

        valid = [c for c in counts if c is not None]
        if not valid:
            continue

        avg = round(sum(valid) / len(valid), 1)
        writer.writerow([folder, *counts, avg])

print(f"✅ Qwen2.5 토큰 집계 완료: '{output_csv}'")
