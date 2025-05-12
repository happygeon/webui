from eval import *

if __name__ == "__main__":
    import sys

    files = ["ex1_1.html","ex2_1.html","ex2_2.html","ex2_3.html", "ex2_4.html"]
    
    for filename in files:
        # 기본적으로 현재 디렉토리의 sample.html을 평가

        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()

        completions = [[{"role": "assistant", "content": html_content}]]
        scores = html_structure_reward_func(completions)

        print(f"📄 {filename} 점수: {scores[0]*100:.2f} / 100")