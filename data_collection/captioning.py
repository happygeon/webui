import os
import base64
import json
from anthropic import Anthropic, BadRequestError
from tqdm import tqdm
from glob import glob
from PIL import Image
import io

# base64 인코딩된 문자열 기준 최대 바이트 수 및 최소 축소 비율
MAX_BYTES = 5242880
MIN_SCALE = 0.5

def preprocess_image_to_base64(path):
    """
    이미지를 PNG로 저장 후 base64 인코딩.
    인코딩된 문자열 길이가 MAX_BYTES 이하가 될 때까지 반복 downscale.
    MIN_SCALE 아래가 되면 스킵(ValueError 발생).
    """
    img = Image.open(path)

    # helper: PIL 이미지를 PNG로 변환해 base64 문자열 얻는 함수
    def encode(img_obj):
        buf = io.BytesIO()
        img_obj.save(buf, format='PNG')
        raw = buf.getvalue()
        b64 = base64.b64encode(raw)
        return b64

    # 1) 초기 인코딩
    b64 = encode(img)
    size = len(b64)

    if size <= MAX_BYTES:
        return b64.decode('utf-8')

    # 2) 최초 스케일 계산
    scale = (MAX_BYTES / size) ** 0.5

    while True:
        if scale < MIN_SCALE:
            raise ValueError("필요한 축소 비율이 너무 극단적입니다. 스킵합니다.")

        # 리사이즈
        new_w = max(1, int(img.width * scale))
        new_h = max(1, int(img.height * scale))
        resized = img.resize((new_w, new_h), Image.LANCZOS)

        # 다시 인코딩
        b64 = encode(resized)
        size = len(b64)
        if size <= MAX_BYTES:
            return b64.decode('utf-8')

        # 여전히 크면 스케일 추가 조정
        scale *= (MAX_BYTES / size) ** 0.5

# Anthropic 클라이언트 초기화
anthropic = Anthropic(api_key="")

# 프롬프트 로드
with open("./caption_gen.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

# caption.txt가 없는 screenshot만 처리
image_paths = [
    p for p in glob("dataset_0628/*/*/screenshot.png")
    if not os.path.exists(os.path.join(os.path.dirname(p), "caption.txt"))
]

def generate_caption(path):
    try:
        b64_str = preprocess_image_to_base64(path)
        response = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=300,
            temperature=0.0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": b64_str,
                            },
                        },
                    ],
                }
            ],
        )
        return response.content[0].text.strip()

    except (ValueError, BadRequestError) as e:
        print(f"Skipping {path}: {e}")
        return None

# 메인 루프
for path in tqdm(image_paths):
    print(path)
    caption = generate_caption(path)
    if not caption:
        continue
    with open(path.replace("screenshot.png", "caption.txt"), "w", encoding="utf-8") as f:
        f.write(caption)
    print(caption)
