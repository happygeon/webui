import csv

def load_csv_to_lists(csv_file):
    # 각 열을 담을 리스트 생성
    col1, col2, col3 = [], [], []
    
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            # row가 3개의 값이 있을 때만
            if len(row) == 3:
                col1.append(row[0])
                col2.append(row[1])
                col3.append(row[2])
    
    return [col1, col2, col3]

# 사용 예시
split_files = load_csv_to_lists('metadata.csv')
# split_files[0] = 첫 번째 열, split_files[1] = 두 번째 열, split_files[2] = 세 번째 열 리스트
print("첫 번째 열:", len(split_files[0]), "개 항목")
print("두 번째 열:", len(split_files[1]), "개 항목")
print("세 번째 열:", len(split_files[2]), "개 항목")
import os

def delete_unwanted_screenshot_files(folder_path, valid_filenames):
    all_files = os.listdir(folder_path)
    for filename in all_files:
        # _screenshot.jpg로 끝나는 파일만 체크
        if filename.endswith('_screenshot.jpg'):
            # _screenshot.jpg를 제거해서 원래 파일명 추출
            basename = filename[:-len('_screenshot.jpg')]
            if basename not in valid_filenames:
                file_path = os.path.join(folder_path, filename)
                os.remove(file_path)
                print(f"Deleted: {file_path}")
    
    print(f"폴더 '{folder_path}'에서 유효하지 않은 파일을 삭제했습니다.")
    print(f"총 {i}개의 파일이 삭제되었습니다.")

folder = ['designer1_target_screenshots', 'final_qwen7b_screenshots', 'qwen14b_screenshots']

for i in range(1, 4):
    folder_path = f'expert_eval_resized_{i}'
    valid_filenames = split_files[i - 1]  # 각 폴더에 해당하는 유효한 파일명 리스트
    for j in folder:
        folder_path_tmp = folder_path + '/' + j
        delete_unwanted_screenshot_files(folder_path_tmp, valid_filenames)
