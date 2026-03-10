import os
import openai
import re

# 🔑 OpenAI API 키 설정
openai.api_key = ""
MODEL = "gpt-4o-mini"   # 필요 시 다른 모델로 변경

def translate_with_gpt(text: str) -> str:
    """
    번호 줄(1., 2., 3.… )마다 영어 원문 바로 아래
    한국어 번역을 삽입한 전체 텍스트를 반환합니다.
    """
    system_msg = (
        "You are a precise translator. "
        "Keep every numbered English line exactly as-is "
        "(e.g., '1. ...'). "
        "Immediately below each such line, add its Korean translation. "
        "Do not change numbering, punctuation, or line order. "
        "No extra blank lines."
    )

    user_msg = (
        "Translate the text below according to the rule.\n"
        "-----\n"
        f"{text}\n"
        "-----"
    )

    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg}
        ],
        temperature=0.0
    )
    return response.choices[0].message.content.strip()

def process_folder(folder="data_merged"):
    """
    folder 안의 모든 .txt 파일을 번역하여
    같은 파일에 바로 덮어씁니다.
    """
    for fname in os.listdir(folder):
        if not fname.lower().endswith(".txt"):
            continue

        path = os.path.join(folder, fname)

        with open(path, "r", encoding="utf-8") as f:
            original_text = f.read().strip()

        translated_text = translate_with_gpt(original_text)

        with open(path, "w", encoding="utf-8") as f:
            f.write(translated_text)

        print(f"✅ 덮어씀: {fname}")

if __name__ == "__main__":
    process_folder("data_merged")
