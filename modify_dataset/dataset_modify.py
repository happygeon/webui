import os
import json
import openai
import requests
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_KEY

# 2. Load input data
with open("ui_design_data.json", "r", encoding="utf-8") as f:
    items = json.load(f)

# 3. Load system prompt
with open("img_insert_prompt.txt", "r", encoding="utf-8") as f:
    base_prompt = f.read()

# 4. Load few-shot examples
with open("img_insert_fewshot.json", "r", encoding="utf-8") as f:
    fewshot_examples = json.load(f)

# 5. Unsplash 이미지 검색 함수
def get_unsplash_url(query):
    headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    params = {"query": query, "per_page": 1}
    response = requests.get("https://api.unsplash.com/search/photos", headers=headers, params=params)
    if response.status_code == 200:
        results = response.json()["results"]
        if results:
            return results[0]["urls"]["regular"]
    return None


# 6. GPT 호출 함수 (few-shot 포함)
def call_gpt(query, html):
    messages = [
        {"role": "system", "content": base_prompt},
    ]
    for ex in fewshot_examples:
        messages.append({"role": "user", "content": f"query: {ex['query']}\nhtml: {ex['html']}"})
        messages.append({"role": "assistant", "content": json.dumps(ex['response'], ensure_ascii=False)})

    # 현재 입력
    messages.append({"role": "user", "content": f"query: {query}\nhtml: {html}"})

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.4
    )
    return response["choices"][0]["message"]["content"]

# 7. main 실행
results = []

i=0
print(len(items))
for item in items:
    i += 1
    query = item["query"]
    html = item["html"]
    print(f"[INFO] Processing query: {query[:40]}...")

    gpt_output = call_gpt(query, html)
    parsed = json.loads(gpt_output)

    modified_html = parsed["modified_html"]
    image_queries = parsed["image_queries"]

    print("done gpt call index:", i)

    # Unsplash로 실제 이미지 URL 매핑
    for key, keyword in image_queries.items():
        img_url = get_unsplash_url(keyword)
        if img_url:
            modified_html = modified_html.replace(f"url='{key}'", img_url)

    results.append({
        "query": query,
        "final_html": modified_html,
        "keywords": image_queries
    })
    if(i == 100):
        break

# 8. 결과 저장
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("[DONE] All HTMLs processed and output.json saved.")
