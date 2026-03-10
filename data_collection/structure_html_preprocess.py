from glob import glob

# 파일 경로 패턴
html_paths = glob("./dataset_0628/*/*/structure_simplified.html")

for path in html_paths:
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # 불필요한 앞/뒤 텍스트 제거 (정상적인 <!DOCTYPE html> 또는 <html ...>로 시작하는 부분부터만 유지)
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("<!doctype html") or line.strip().lower().startswith("<html"):
            start_idx = i
            break

    end_idx = len(lines)
    for j in range(len(lines) - 1, -1, -1):
        if "</html>" in lines[j].lower():
            end_idx = j + 1
            break

    cleaned_lines = lines[start_idx:end_idx]

    # 덮어쓰기
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(cleaned_lines)
