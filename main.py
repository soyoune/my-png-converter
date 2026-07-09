import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io
import os
from streamlit_image_coordinates import streamlit_image_coordinates
import cv2 

st.title("🎯 스마트 배경 및 그림자 제거기")
st.write("이미지에서 **지우고 싶은 부분(배경, 그림자 등)을 두세 번 반복해서 터치(클릭)**해 보세요!")

uploaded_files = st.file_uploader(
    "이미지를 선택하세요...", 
    type=["jpg", "jpeg", "png", "webp"], 
    accept_multiple_files=True
)

if uploaded_files:
    if "processed_images" not in st.session_state:
        st.session_state.processed_images = {}
    if "bg_masks" not in st.session_state:
        st.session_state.bg_masks = {}

    for uploaded_file in uploaded_files:
        original_name = uploaded_file.name
        file_name, _ = os.path.splitext(original_name)
        new_filename = f"new_{file_name}.png"
        
        st.markdown("---")
        st.subheader(f"작업 파일: {original_name}")
        
        # 이미지 로드 및 초기 마스크 설정
        image = Image.open(uploaded_file).convert("RGBA")
        img_array = np.array(image)
        h, w = img_array.shape[:2]
        
        if original_name not in st.session_state.bg_masks:
            st.session_state.bg_masks[original_name] = np.zeros((h, w), np.uint8)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("👇 투명하게 만들 곳들을 연속해서 클릭하세요.")
            value = streamlit_image_coordinates(image, key=f"click_{original_name}")
            
        if value is not None:
            x, y = int(value["x"]), int(value["y"])
            
            rgb = img_array[:, :, :3]
            alpha = img_array[:, :, 3]
            
            # 💡 [수정] 오작동하던 깐깐한 경고 로직을 완전히 제거했습니다.
            # 대신 FloodFill의 오차 범위를 아주 정밀하게 잡아 검은 선 침범을 원천 차단합니다.
            current_flood_mask = np.zeros((h + 2, w + 2), np.uint8)
            
            # loDiff와 upDiff를 2로 설정하여, 클릭한 색상과 거의 일치하는 밝은 배경만 추적합니다.
            # 이 상태로 전진하다가 검은색 외곽선(어두운 색)을 만나면 선을 넘지 않고 멈춥니다.
            flooded = rgb.copy()
            cv2.floodFill(flooded, current_flood_mask, (x, y), (0, 0, 0), loDiff=(2, 2, 2), upDiff=(2, 2, 2))
            
            actual_current_mask = current_flood_mask[1:h+1, 1:w+1]
            
            # 누적 마스크 합치기 (여러 번 터치 가능)
            st.session_state.bg_masks[original_name] = cv2.bitwise_or(
                st.session_state.bg_masks[original_name], 
                actual_current_mask
            )
            
            # 최종 누적 마스크를 적용해 투명화
            accumulated_mask = st.session_state.bg_masks[original_name]
            new_alpha = alpha.copy()
            new_alpha[accumulated_mask == 1] = 0
            
            output_array = np.dstack((rgb, new_alpha))
            output_image = Image.fromarray(output_array)
            st.session_state.processed_images[original_name] = output_image

        # 결과 출력 및 다운로드 영역
        with col2:
            if original_name in st.session_state.processed_images:
                st.write("✨ 결과 이미지 (여러 번 터치 누적 적용 중)")
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
                
                preview_img = Image.alpha_composite(bg_checker, out_img)
                st.image(preview_img, caption="💡 격자 부분 = 투명하게 지워진 영역", width="stretch")
                
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
                
                if st.button("초기화 (다시 지우기)", key=f"reset_{original_name}"):
                    del st.session_state.processed_images[original_name]
                    del st.session_state.bg_masks[original_name]
                    st.rerun()
            else:
                st.info("왼쪽 이미지에서 지우고 싶은 곳을 터치하면 결과가 여기에 표시됩니다.")
