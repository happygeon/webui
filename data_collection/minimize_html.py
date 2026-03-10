import os
import openai
from openai import OpenAI
from glob import glob
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("gpt_api_key"))
html_path = [
    path for path in glob("./dataset_0628/*/*/structure.html")
    if not os.path.exists(os.path.join(os.path.dirname(path), "structure_simplified.html"))
]
for path in html_path:
    with open(path, "r", encoding='utf-8') as f:
        html = f.read()
    prompt = f"""
    You are an assistant that simplifies HTML documents.
    Your goal is to simplify the HTML **while maintaining the original structure and all important content(Including Image)**.
    Please consider the original page's purpose and type.
    You SHOULD perform the following steps in order. Other behavior is NOT acceptable:
    1. **Remove all tags that do not include meaningful content** (e.g., empty divs, spans or tags that contain only whitespace).
    2. **Summarize long text paragraphs** into simpler, shorter versions while preserving their core meaning and relevance to the page.
    Here is the HTML:
    {html}
    Simplified HTML:
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        simplified_html = response.choices[0].message.content
        save_path = path.replace("structure.html", "structure_simplified.html")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(simplified_html)
        print(f":흰색_확인_표시: Saved: {save_path}")
    except Exception as e:
        print(f":x: Failed to process {path}: {e}")