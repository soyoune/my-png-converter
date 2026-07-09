import streamlit as st
from PIL import Image
import numpy as np
import cv2
import io
import os
# 이미지 클릭 좌표를 가져오기 위한 라이브러리
from streamlit_image_coordinates import streamlit_image_coordinates

st.title("🎯 포인터 지정형 배경 제거기")
st.write("이미지에서 **지우고 싶은 배경 부분(예: 흰 바탕)**을 마우스로 클릭하세요!")

uploaded_files = st.file_uploader(
    "이미지를 선택하세요...", 
    type=["jpg", "jpeg", "png", "webp"], 
    accept_multiple_files=True
)

if uploaded_files:
    # 세션 상태를 활용해 각 파일별로 작업 상태 저장
    if "processed_images" not in st.session_state:
        st.session_state.processed_images = {}

    for uploaded_file in uploaded_files:
        original_name = uploaded_file.name
        file_name, _ = os.path.splitext(original_name)
        new_filename = f"new_{file_name}.png"
        
        st.markdown(f"---")
        st.subheader(f"작업 파일: {original_name}")
        
        # 이미지 로드
        image = Image.open(uploaded_file).convert("RGBA")
        img_array = np.array(image)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("👇 지울 배경 곳을 클릭하세요.")
            # 💡 사용자가 이미지를 클릭하면 해당 좌표(x, y)를 반환합니다.
            value = streamlit_image_coordinates(image, key=f"click_{original_name}")
            
        # 클릭이 발생했을 때 배경 제거 로직 작동
        if value is not None:
            x, y = value["x"], value["y"]
            
            # OpenCV FloodFill 알고리즘 적용을 위해 BGR/RGB 분리
            rgb = img_array[:, :, :3]
            alpha = img_array[:, :, 3]
            
            # FloodFill을 위한 마스크 생성 (이미지보다 사방으로 2픽셀 더 커야 함)
            h, w = rgb.shape[:2]
            mask = np.zeros((h + 2, w + 2), np.uint8)
            
            # 클릭한 지점과 비슷한 색상을 가진 연속된 영역을 찾아서 마스킹
            # loDiff, upDiff 값(10)을 조절하여 오차 범위를 설정 가능
            flooded = rgb.copy()
            cv2.floodFill(flooded, mask, (x, y), (0, 0, 0), loDiff=(10, 10, 10), upDiff=(10, 10, 10))
            
            # floodFill이 채워진 영역(마스크에서 1이 된 부분)을 투명하게 만듦
            # 배경 제거된 마스크는 0번 행렬 기준 1부터 h+1까지
            actual_mask = mask[1:h+1, 1:w+1]
            
            # 클릭된 배경 부분의 알파(투명도) 값을 0으로 변경
            new_alpha = alpha.copy()
            new_alpha[actual_mask == 1] = 0
            
            # 최종 투명 이미지 합성
            output_array = np.dstack((rgb, new_alpha))
            output_image = Image.fromarray(output_array)
            st.session_state.processed_images[original_name] = output_image

        # 결과 출력 및 다운로드
        with col2:
            if original_name in st.session_state.processed_images:
                st.write("✨ 결과 이미지 (선택 영역 투명화 완료)")
                out_img = st.session_state.processed_images[original_name]
                st.image(out_img, use_container_width=True)
                
                # 다운로드 버튼
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
