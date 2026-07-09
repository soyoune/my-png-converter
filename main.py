import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io
from streamlit_image_coordinates import streamlit_image_coordinates
import cv2 

st.title("🎯 스마트 배경 및 그림자 제거기")
st.write("이미지에서 **지우고 싶은 배경 부분(예: 흰 바탕)**을 한 곳만 클릭하세요!")

uploaded_file = st.file_uploader("이미지를 선택하세요...", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    # 이미지 로드
    image = Image.open(uploaded_file).convert("RGBA")
    img_array = np.array(image)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("👇 지울 배경 한 곳을 클릭하세요.")
        # 사용자가 이미지를 클릭하면 좌표 수집
        value = streamlit_image_coordinates(image, key="click")
        
    # 클릭이 발생했을 때 배경 제거 로직 작동
    if value is not None:
        x, y = int(value["x"]), int(value["y"])
        
        # RGB 채널과 알파 채널 분리
        rgb = img_array[:, :, :3]
        alpha = img_array[:, :, 3]
        
        # FloodFill용 마스크 생성
        h, w = rgb.shape[:2]
        mask = np.zeros((h + 2, w + 2), np.uint8)
        
        # 💡 [핵심] 그림자를 보호하기 위해 loDiff, upDiff 값을 조절
        # 이 값을 낮추어, 클릭한 흰색과 색상차가 나는 연회색 그림자를 배경 범위에서 제외하여 보호합니다.
        flooded = rgb.copy()
        cv2.floodFill(flooded, mask, (x, y), (0, 0, 0), loDiff=(5, 5, 5), upDiff=(5, 5, 5))
        
        actual_mask = mask[1:h+1, 1:w+1]
        
        # 찾은 배경 영역의 알파(투명도) 값을 0으로 변경
        new_alpha = alpha.copy()
        new_alpha[actual_mask == 1] = 0
        
        # 최종 이미지 합성
        output_array = np.dstack((rgb, new_alpha))
        out_img = Image.fromarray(output_array)
        
        # 결과 출력 영역
        with col2:
            st.write("✨ 결과 이미지 (캐릭터 내부 및 그림자 보호 완료)")
            
            # 💡 [추가] Streamlit 화면에서 투명도를 눈으로 확인하기 위한 격자무늬 합성
            # 원본 이미지 크기의 격자(Checkered) 배경 생성
            bg_checker = Image.new("RGBA", out_img.size, (255, 255, 255, 255))
            ch_w, ch_h = out_img.size
            grid_size = 16  # 격자 크기
            
            # 가상의 투명 배경 패턴 그리기 (연한 회색과 흰색 교차)
            draw = ImageDraw.Draw(bg_checker)
            for i in range(0, ch_w, grid_size):
                for j in range(0, ch_h, grid_size):
                    if (i // grid_size + j // grid_size) % 2 == 0:
                        draw.rectangle([i, j, i + grid_size, j + grid_size], fill=(240, 240, 240, 255))
            
            # 격자 배경 위에 작업한 투명 이미지를 얹어서 화면 표시용 이미지 생성
            preview_img = Image.alpha_composite(bg_checker, out_img)
            
            # 화면에는 격자가 합성된 이미지를 보여주어 투명 여부 확인
            st.image(preview_img, caption="💡 격자 부분 = 투명하게 지워진 영역", use_container_width=True)
            
            # 다운로드 버튼 (격자가 없는 진짜 투명한 이미지를 다운로드)
            buf = io.BytesIO()
            out_img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="📥 결과 이미지 다운로드",
                data=byte_im,
                file_name="transformed_image.png",
                mime="image/png",
            )
