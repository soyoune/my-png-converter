import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io
import os
from streamlit_image_coordinates import streamlit_image_coordinates
# OpenCV 라이브러리 추가
import cv2 

st.title("🎯 스마트 배경 및 그림자 제거기")
st.write("이미지에서 **지우고 싶은 배경이나 그림자 부분(예: 흰 바탕)**을 한 곳만 클릭하세요!")

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
            st.write("👇 지울 배경/그림자 한 곳을 클릭하세요.")
            value = streamlit_image_coordinates(image, key=f"click_{original_name}")
            
        # 클릭이 발생했을 때 배경 제거 로직 작동 (캐릭터 보호형 FloodFill)
        if value is not None:
            x, y = int(value["x"]), int(value["y"])
            
            # OpenCV FloodFill 알고리즘 적용을 위해 RGB 채널과 알파 채널 분리
            rgb = img_array[:, :, :3]
            alpha = img_array[:, :, 3]
            
            # FloodFill을 위한 마스크 생성 (이미지보다 사방으로 2픽셀 더 커야 함)
            h, w = rgb.shape[:2]
            mask = np.zeros((h + 2, w + 2), np.uint8)
            
            # BGR 색상 순서로 클릭된 색상 가져오기 (OpenCV standard)
            # numpy 배열 인덱싱은 [y, x] 순서입니다.
            c_r, c_g, c_b = int(rgb[y, x, 0]), int(rgb[y, x, 1]), int(rgb[y, x, 2])
            
            # 💡 핵심 로직: FloodFill 알고리즘 적용
            # 사용자가 클릭한 지점(x, y)과 색상이 유사하면서 '연속적으로 연결된 영역'만 추적하여 mask에 1을 채웁니다.
            # 캐릭터 내부의 흰색은 외곽선에 가로막혀 연결되지 않으므로 mask에 포함되지 않습니다.
            
            flooded = rgb.copy()
            cv2.floodFill(flooded, mask, (x, y), (0, 0, 0), loDiff=(10, 10, 10), upDiff=(10, 10, 10))
            
            # floodFill이 채워진 영역(마스크에서 1이 된 부분)을 투명하게 만듦
            # 배경 제거된 마스크는 0번 행렬 기준 1부터 h+1까지 추출
            actual_mask = mask[1:h+1, 1:w+1]
            
            # 찾은 배경 부분의 알파(투명도) 값을 '0(완전 투명)'으로 변경
            new_alpha = alpha.copy()
            new_alpha[actual_mask == 1] = 0
            
            # 최종 투명 이미지 합성 및 세션 저장
            output_array = np.dstack((rgb, new_alpha))
            output_image = Image.fromarray(output_array)
            st.session_state.processed_images[original_name] = output_image

        # 결과 출력 및 다운로드 영역
        with col2:
            if original_name in st.session_state.processed_images:
                st.write("✨ 결과 이미지 (캐릭터 내부 보호 및 배경 투명화 완료)")
                out_img = st.session_state.processed_images[original_name]
                
                # 투명도 확인을 위한 격자무늬(Checkered) 배경 생성
                bg_checker = Image.new("RGBA", out_img.size, (255, 255, 255, 255))
                ch_w, ch_h = out_img.size
                grid_size = 16
                
                draw = ImageDraw.Draw(bg_checker)
                for i in range(0, ch_w, grid_size):
                    for j in range(0, ch_h, grid_size):
                        if (i // grid_size + j // grid_size) % 2 == 0:
                            draw.rectangle([i, j, i + grid_size, j + grid_size], fill=(240, 240, 240, 255))
                
                # 격자 배경 위에 '배경이 투명해진 이미지'를 합성
                preview_img = Image.alpha_composite(bg_checker, out_img)
                
                # 격자가 투명하게 비치는 미리보기 이미지를 화면에 표시
                st.image(preview_img, caption="💡 격자 부분 = 투명하게 지워진 영역", width="stretch")
                
                # 다운로드 파일 준비 (격자 없는 진짜 투명 이미지)
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
