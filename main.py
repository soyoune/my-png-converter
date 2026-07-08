from rembg import remove
from PIL import Image
import os

def remove_background(input_path, output_path):
    try:
        # 1. 이미지 불러오기
        print(f"이미지를 로드하는 중: {input_path}")
        input_image = Image.open(input_path)
        
        # 2. AI 기반 배경 제거 (화질 손실 없음)
        print("배경을 제거하는 중... (첫 실행 시 AI 모델 다운로드로 인해 시간이 조금 걸릴 수 있습니다)")
        output_image = remove(input_image)
        
        # 3. 투명 PNG로 저장 (lossless 설정)
        output_image.save(output_path, format="PNG", compress_level=3)
        print(f"성공! 저장 완료: {output_path}")
        
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

# --- 사용 예시 ---
# 변환하고 싶은 이미지 경로를 적어주세요. (jpg, jpeg, png, heic 등 모두 가능)
input_img = "my_photo.jpg" 
output_img = "my_photo_transparent.png"

remove_background(input_img, output_img)
