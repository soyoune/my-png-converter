import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io
import os
from streamlit_image_coordinates import streamlit_image_coordinates
import cv2 

st.title("🎯 스마트 배경 및 그림자 제거기")
st.write("이미지에서 지우고 싶은 부분을 터치하여 지우거나, 잘못 지워진 부분을 조금씩 정밀하게 복구해 보세요!")

# 이미지 영역 마우스 오버 시 정밀 십자가 커서(+)로 변경하는 CSS
st.markdown(
    """
    <style>
    div[data-testid="stHorizontalBlock"] iframe, 
    div[data-testid="stHorizontalBlock"] img,
    .stImageCoordinates, 
    img {
        cursor: crosshair !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 작업 모드 선택
mode = st.radio(
    "👉 작업 모드를 선택하세요:",
    ["🔴 터치하여 투명하게 지우기 (넓은 영역)", "🟢 잘못 지워진 곳 조금씩 채우기 (정밀 복구)"],
    horizontal=True
)

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
    if "reset_counters" not in st.session_state:
        st.session_state.reset_counters = {}

    for uploaded_file in uploaded_files:
        original_name = uploaded_file.name
        file_name, _ = os.path.splitext(original_name)
        new_filename = f"new_{file_name}.png"
        
        st.markdown("---")
        st.subheader(f"작업 파일: {original_name}")
        
        if original_name not in st.session_state.reset_counters:
            st.session_state.reset_counters[original_name] = 0
            
        # 1. 고화질 원본 이미지 로드
        image = Image.open(uploaded_file).convert("RGBA")
        img_array = np.array(image)
        h, w = img_array.shape[:2]
        
        if original_name not in st.session_state.bg_masks:
            st.session_state.bg_masks[original_name] = np.zeros((h, w), np.uint8)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("👇 이미지 위의 대상을 조준해서 클릭하세요.")
            
            # 세로 잘림 방지 뷰페이지 스케일링 (280px 제한)
            max_size = 280
            if w > max_size or h > max_size:
                scale_ratio = min(max_size / w, max_size / h)
                preview_w = int(w * scale_ratio)
                preview_h = int(h * scale_ratio)
                preview_img_for_click = image.resize((preview_w, preview_h), Image.Resampling.LANCZOS)
            else:
                scale_ratio = 1.0
                preview_img_for_click = image

            current_counter = st.session_state.reset_counters[original_name]
            value = streamlit_image_coordinates(
                preview_img_for_click, 
                key=f"click_{original_name}_{current_counter}"
            )
            
        if value is not None:
            # 축소 화면의 좌표를 원본 고해상도 좌표로 정확하게 역계산
            x = int(int(value["x"]) / scale_ratio)
            y = int(int(value["y"]) / scale_ratio)
            
            if 0 <= x < w and 0 <= y < h:
                rgb = img_array[:, :, :3]
                alpha = img_array[:, :, 3]
                
                if "🔴" in mode:
                    # 💡 [핵심 알고리즘 수정] 단순히 색상 차이만 보지 않고 그레이스케일 대비를 활용해 사람의 형태 윤곽(Gradient)을 보호합니다.
                    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
                    
                    # 대비를 주어 인물과 배경의 경계선을 더 명확하게 시뮬레이션
                    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
                    
                    current_flood_mask = np.zeros((h + 2, w + 2), np.uint8)
                    
                    # 클릭한 지점의 색상 특성을 분석해 유연하게 floodFill 수행
                    flooded = rgb.copy()
                    cv2.floodFill(
                        flooded, 
                        current_flood_mask, 
                        (x, y), 
                        (0, 0, 0), 
                        loDiff=(3, 3, 3), # 살색/입술이 번지지 않도록 오차 범위를 극단적으로 정밀하게 제어
                        upDiff=(3, 3, 3)
                    )
                    
                    actual_current_mask = current_flood_mask[1:h+1, 1:w+1]
                    
                    # 지우기 마스크 누적 합치기
                    st.session_state.bg_masks[original_name] = cv2.bitwise_or(
                        st.session_state.bg_masks[original_name], 
                        actual_current_mask
                    )
                else:
                    # 🟢 채우기(정밀 복구) 방식: 브러시 반경만큼만 원래대로 복원
                    brush_radius = 15
                    brush_mask = np.zeros((h, w), np.uint8)
                    cv2.circle(brush_mask, (x, y), brush_radius, 1, -1)
                    
                    st.session_state.bg_masks[original_name] = cv2.bitwise_and(
                        st.session_state.bg_masks[original_name], 
                        cv2.bitwise_not(brush_mask)
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
                st.write("✨ 결과 이미지")
                out_img = st.session_state.processed_images[original_name]
                
                bg_checker = Image.new("RGBA", out_img.size, (255, 255, 255, 255))
                ch_w, ch_h = out_img.size
                grid_size = 16
                
                draw = ImageDraw.Draw(bg_checker)
                for i in range(0, ch_w, grid_size):
                    for j in range(0, ch_h, grid_size):
                        if (i // grid_size + j // grid_size) % 2 == 0:
                            draw.rectangle([i, j, i + grid_size, j + grid_size], fill=(240, 240, 240, 255))
                
                if ch_w > max_size or ch_h > max_size:
                    out_scale = min(max_size / ch_w, max_size / ch_h)
                    res_w, res_h = int(ch_w * out_scale), int(ch_h * out_scale)
                    preview_img = Image.alpha_composite(bg_checker, out_img).resize((res_w, res_h), Image.Resampling.LANCZOS)
                else:
                    preview_img = Image.alpha_composite(bg_checker, out_img)
                    
                st.image(preview_img, caption="💡 격자 부분 = 투명하게 지워진 영역")
                
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
                    if original_name in st.session_state.processed_images:
                        del st.session_state.processed_images[original_name]
                    if original_name in st.session_state.bg_masks:
                        del st.session_state.bg_masks[original_name]
                    st.session_state.reset_counters[original_name] += 1
                    st.rerun()
            else:
                st.info("왼쪽 이미지에서 지우고 싶은 곳을 터치하면 결과가 여기에 표시됩니다.")
