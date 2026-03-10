import os
import json
from bs4 import BeautifulSoup, Tag

# 1) 단일 HTML 파일의 DOM(Tag) 노드 수를 반환
def count_dom_nodes(filepath: str) -> int:
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    return sum(1 for node in soup.descendants if isinstance(node, Tag))

# 2) data_merged/<folder>/structure*.html 두 파일에 대해 개수 집계
def build_dom_count_json(base_dir: str = "data_merged") -> dict:
    result = {
        "structure": {},
        "structure_simplified": {},
    }
    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue

        struct_path = os.path.join(folder_path, "structure.html")
        s_struct_path = os.path.join(folder_path, "structure_simplified.html")

        # 예외가 발생하면 프로그램이 즉시 중단됩니다.
        result["structure"][folder_name] = count_dom_nodes(struct_path)
        result["structure_simplified"][folder_name] = count_dom_nodes(s_struct_path)

    return result

# 3) 실행 진입점
if __name__ == "__main__":
    counts = build_dom_count_json("data_merged")
    with open("dom_counts.json", "w", encoding="utf-8") as f:
        json.dump(counts, f, ensure_ascii=False, indent=2)
    print("dom_counts.json 저장 완료")
