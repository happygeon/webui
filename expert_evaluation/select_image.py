import os
import shutil
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# ───────────────────────────── 설정 ─────────────────────────────
BASE_DIR = "./expert_eval"
FOLDERS = [
    "designer1_target_screenshots",  # 내부적으로만 복사용 조건으로 사용
    "final_qwen7b_screenshots",
    "qwen14b_screenshots"
]
OUTPUT_DIR = "./select_good_images"
PROCESSED_FILE = os.path.join(OUTPUT_DIR, "processed.txt")
THUMB_SIZE = (600, 600)  # 썸네일 크기
# ────────────────────────────────────────────────────────────────

# 출력 폴더 및 processed.txt 준비
os.makedirs(OUTPUT_DIR, exist_ok=True)
if os.path.exists(PROCESSED_FILE):
    with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
        processed_images = set(line.strip() for line in f if line.strip())
else:
    processed_images = set()

# 첫 번째 폴더 기준 전체 이미지 리스트
all_images = [
    fn for fn in os.listdir(os.path.join(BASE_DIR, FOLDERS[0]))
    if fn.lower().endswith(".png")
]
# 이미 처리된 이미지는 제외
image_names = [fn for fn in all_images if fn not in processed_images]

# 처리 완료 표시 함수
def mark_processed(name):
    processed_images.add(name)
    with open(PROCESSED_FILE, 'a', encoding='utf-8') as f:
        f.write(name + "\n")

# ────────────────────────────────────────────────────────────────
# Tkinter 윈도우 초기화
root = tk.Tk()
root.title("이미지 비교 후 선택")
root.state('zoomed')  # 전체 화면 모드
frame = tk.Frame(root, padx=20, pady=20)
frame.pack(fill="both", expand=True)

def show_images(idx):
    # 모두 처리했으면 종료
    if idx >= len(image_names):
        messagebox.showinfo("완료", "모든 이미지를 처리했습니다.")
        root.destroy()
        return

    name = image_names[idx]
    items = [(folder, os.path.join(BASE_DIR, folder, name)) for folder in FOLDERS]
    random.shuffle(items)

    # 세트 중 하나라도 파일이 없으면 자동 스킵
    if any(not os.path.exists(path) for _, path in items):
        mark_processed(name)
        show_images(idx + 1)
        return

    # 이전 위젯 제거
    for w in frame.winfo_children():
        w.destroy()

    # 키 바인딩 초기화
    for key in ('<Key-0>', '<Key-1>', '<Key-2>', '<Key-3>'):
        root.unbind(key)

    # 썸네일 생성 및 표시
    photos = []
    for col, (_, path) in enumerate(items):
        img = Image.open(path).convert("RGBA")
        img.thumbnail(THUMB_SIZE, Image.Resampling.LANCZOS)
        bg = Image.new("RGBA", THUMB_SIZE, (255,255,255,255))
        x = (THUMB_SIZE[0] - img.width) // 2
        y = (THUMB_SIZE[1] - img.height) // 2
        bg.paste(img, (x, y), img)

        photo = ImageTk.PhotoImage(bg)
        photos.append(photo)
        lbl = tk.Label(frame, image=photo)
        lbl.image = photo
        lbl.grid(row=0, column=col, padx=20, pady=20)

    # 선택 또는 기권 처리
    def on_select(selected_folder):
        mark_processed(name)
        # 첫 번째 폴더(designer1_target_screenshots) 선택 시에만 복사
        if selected_folder == FOLDERS[0]:
            out_dir = os.path.join(OUTPUT_DIR, os.path.splitext(name)[0])
            os.makedirs(out_dir, exist_ok=True)
            for f in FOLDERS:
                src = os.path.join(BASE_DIR, f, name)
                dst = os.path.join(out_dir, f"{os.path.splitext(name)[0]}_{f}.png")
                shutil.copy2(src, dst)
        show_images(idx + 1)

    # “선택” 버튼 및 1,2,3 키 바인딩
    for col, (folder, _) in enumerate(items):
        btn = tk.Button(frame, text="선택", width=20, height=3,
                        command=lambda f=folder: on_select(f))
        btn.grid(row=1, column=col, padx=20, pady=(0,20))
        root.bind(f'<Key-{col+1}>', lambda e, f=folder: on_select(f))

    # “기권” 버튼 및 0 키 바인딩
    skip_btn = tk.Button(frame, text="기권", width=20, height=3,
                         command=lambda: on_select(None))
    skip_btn.grid(row=2, columnspan=3, pady=(0,20))
    root.bind('<Key-0>', lambda e: on_select(None))

    # 키 입력을 받도록 포커스 설정
    root.focus_set()

# 실행
show_images(0)
root.mainloop()
