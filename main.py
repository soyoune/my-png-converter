import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io
import os
from streamlit_image_coordinates import streamlit_image_coordinates
import cv2 

st.title("🎯 스마트 배경 및 그림자 제거기")
st.write("이미지에서 **지우고 싶은 배경 부분(예: 흰 바탕)**을 한 곳만 클릭하세요!")

uploaded_files = st.file_uploader(
    "이미지를 선택하세요...", 
    type=["jpg", "jpeg", "png", "webp"], 
    accept_multiple_files=True
)

if uploaded_files:
    if "processed_images" not in st.session_state:
        st.session_state.processed_images = {}

    for uploaded_file in uploaded_files:
        original_name = uploaded_file.name
        file_name, _ = os.path.splitext(original_name)
        new_filename = f"new_{file_name}.png"
        
        st.markdown("---")
        st.subheader(f"작업 파일: {original_name}")
        
        # 이미지 로드
        image = Image.open(uploaded_file).convert("RGBA")
        img_array = np.array(image)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("👇 지울 배경 한 곳을 클릭하세요.")
            value = streamlit_image_coordinates(image, key=f"click_{original_name}")
            
        # 클릭이 발생했을 때 배경 제거 로직 작동 (캐릭터 보호 및 그림자 보존)
        if value is not None:
            x, y = int(value["x"]), int(value["y"])
            
            # RGB 채널과 알파 채널 분리
            rgb = img_array[:, :, :3]
            alpha = img_array[:, :, 3]
            
            # FloodFill용 마스크 생성
            h, w = rgb.shape[:2]
            mask = np.zeros((h + 2, w + 2), np.uint8)
            
            # 오차 범위를 5로 낮춰 연회색 그림자가 함께 지워지는 것을 방지
            flooded = rgb.copy()
            cv2.floodFill(flooded, mask, (x, y), (0, 0, 0), loDiff=(5, 5, 5), upDiff=(5, 5, 5))
            
            actual_mask = mask[1:h+1, 1:w+1]
            
            # 연결된 흰 배경 영역만 투명화
            new_alpha = alpha.copy()
            new_alpha[actual_mask == 1] = 0
            
            # 최종 이미지 합성
            output_array = np.dstack((rgb, new_alpha))
            output_image = Image.fromarray(output_array)
            st.session_state.processed_images[original_name] = output_image

        # 결과 출력 및 다운로드 영역
        with col2:
            if original_name in st.session_state.processed_images:
                st.write("✨ 결과 이미지 (캐릭터 내부 및 그림자 보호 완료)")
                out_img = st.session_state.processed_images[original_name]
                
                # 투명도 확인을 위한 격자무늬 배경 생성
                bg_checker = Image.new("RGBA", out_img.size, (255, 255, 255, 255))
                ch_w, ch_h = out_img.size
                grid_size = 16
                
                draw = ImageDraw.Draw(bg_checker)
                for i in range(0, ch_w, grid_size):
                    for j in range(0, ch_h, grid_size):
                        if (i // grid_size + j // grid_size) % 2 == 0:
                            draw.rectangle([i, j, i + grid_size, j + grid_size], fill=(240, 240, 240, 255))
                
                # 격자 배경 위에 결과물 합성
                preview_img = Image.alpha_composite(bg_checker, out_img)
                
                # 최신 Streamlit 규격에 맞게 화면 표시
                st.image(preview_img, caption="💡 격자 부분 = 투명하게 지워진 영역", width="stretch")
                
                # 다운로드 파일 준비
                buf = io.BytesIO()
                out_img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label=f"📥 {new_filename} 다운로드",
                    data=byte_im,
                    file_name=new_filename,
                    mime="image/png",
                    key=f"dl_{original_name}"
                )
            else:
                st.info("왼쪽 이미지에서 배경을 클릭하면 결과가 여기에 표시됩니다.")
