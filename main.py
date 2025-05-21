from eval import *

if __name__ == "__main__":
    import sys

    folder_path = "./response/"
    files = []
    for i in range(10):
        files.append(folder_path + str(i) + "_enhance.html")
        files.append(folder_path + str(i) + ".html")
    
    for filename in files:
        # 기본적으로 현재 디렉토리의 sample.html을 평가

        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()

        completions = [[{"role": "assistant", "content": html_content}]]
        
        reward = RewardFunc(completions)
        reward_score = reward.eval()
        #print(f"📄 {filename} 점수: {reward_score[0]*100:.2f} / 100")
        #print("---------------------------------------------")

        reward_new_score = reward.new_eval()
        reward_new_score = reward_new_score[0]['total_score']
        print(f"📄 {filename} (new) 점수: {reward_new_score:.2f} / 100")
        print("---------------------------------------------")