import os
from glob import glob
from PIL import Image

target_names = [
    "carbonmade", "dopplepress", "duolingo", "eventbrite", "goodreads", "grailed", "habitat", "immanuel_lodge", "javaboynation",
    "jhatkaa", "joncookingclass", "lonelyplanet_mobile", "miro", "newslaundry", "ourworldindata", "retool", "sxsw",
    "tally", "thebeacontoday", "ticketleap", "unsplash", "who", "zionadventurephotog"
]

# glob으로 ./todo/*/{파일명}_screenshoot.png 모두 찾기
pattern = './todo/*/{}_screensh ot.png'
found_paths = []
for name in target_names:
    found_paths += glob(pattern.format(name))
    print(f"Searching for: {pattern.format(name)} - Found {len(glob(pattern.format(name)))} files")
print(f"Found {len(found_paths)} files to process.")
for src_path in found_paths:
    folder = os.path.relpath(os.path.dirname(src_path), './todo')
    filename = os.path.splitext(os.path.basename(src_path))[0]
    ext = os.path.splitext(src_path)[1]

    # 새 파일명 생성: {파일명}_screenshoot_downscailing.png
    base = filename  # 이미 "_screenshoot"이 붙어 있음
    new_filename = f"{base}_downscailing{ext}"
    dst_folder = os.path.join('./new_image', folder)
    dst_path = os.path.join(dst_folder, new_filename)
    os.makedirs(dst_folder, exist_ok=True)

    # 다운스케일 및 저장
    img = Image.open(src_path)
    scale = 0.5
    new_size = (int(img.width * scale), int(img.height * scale))
    img_resized = img.resize(new_size, Image.LANCZOS)
    img_resized.save(dst_path)
    print(f"Saved: {dst_path}")
