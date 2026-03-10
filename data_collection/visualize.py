import os, json

ROOT_DIR = "./data_merged"
result   = {}
i = 0
for subdir in os.listdir(ROOT_DIR):
    caption_path = os.path.join(ROOT_DIR, subdir, "caption.txt")
    if not os.path.isfile(caption_path):
        continue            # caption.txt가 없으면 건너뜁니다

    entry = {}
    with open(caption_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.lstrip()          # 앞쪽 공백 제거
            if line.startswith("2"):
                # "2. " 다음 내용만 추출
                entry[2] = line.split("2. ", 1)[-1].rstrip("\n")
            elif line.startswith("3"):
                entry[3] = line.split("3. ", 1)[-1].rstrip("\n")

    # 두 줄 중 하나라도 존재할 때만 기록
    if entry:
        print(f"{i:04d} {subdir} {entry}")
        i += 1
        result[subdir] = entry

# 원한다면 파일로 저장
with open("captions_2_and_3.json", "w", encoding="utf-8") as fp:
    json.dump(result, fp, ensure_ascii=False, indent=2)
