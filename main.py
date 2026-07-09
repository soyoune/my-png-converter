import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io
import os
from streamlit_image_coordinates import streamlit_image_coordinates

st.title("🎯 스마트 배경 지우개 & 포토샵형 복구 브러시")
st.write("1. 배경을 클릭해 캐릭터를 보호하면서 배경을 먼저 지우세요.")
st.write("2. 모드가 바뀐 뒤 이미지 위로 마우스를 올리면 **포토샵처럼 원형 브러시 크기**가 표시됩니다!")

# 작업 모드 선택
mode = st.radio(
    "👉 작업 모드를 선택하세요:",
    ["🔴 터치하여 배경 한 번에 지우기 (캐릭터 보호)", "🟢 잘못 지워진 곳 슥슥 문질러 채우기 (포토샵형 복구 브러시)"],
    horizontal=True
)

# 브러시 크기 조절
brush_size = st.slider("🖌️ 복구 브러시 크기 조절", min_value=10, max_value=100, value=30, step=5)

# 💡 [핵심 추가] 마우스가 올라갔을 때 포토샵처럼 브러시 크기의 원형(Circle) 커서가 따라다니도록 만드는 CSS 효과
st.markdown(
    f"""
    <style>
    /* 이미지 편집 영역 위에만 포토샵 스타일의 원형 커서 적용 */
    .stImageCoordinates, .stImageCoordinates img, img {{
        cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="{brush_size*2}" height="{brush_size*2}" viewBox="0 0 {brush_size*2} {brush_size*2}"><circle cx="{brush_size}" cy="{brush_size}" r="{brush_size-1}" stroke="%23ff4b4b" stroke-width="1.5" fill="none" stroke-dasharray="3,3"/></svg>') {brush_size} {brush_size}, crosshair !important;
    }
    </style>
    """,
    unsafe_allow_html=True
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
    # 드래그 궤적 추적을 위한 좌표 메모리
    if "last_mouse_pos" not in st.session_state:
        st.session_state.last_mouse_pos = None

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
        
        # 누적 마스크 초기화
        if original_name not in st.session_state.bg_masks:
            st.session_state.bg_masks[original_name] = np.zeros((h, w), np.uint8)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("👇 이미지 위에서 마우스를 움직이거나 클릭하여 복구하세요.")
            
            display_width = 350
            scale_ratio = display_width / w
            display_height = int(h * scale_ratio)
            preview_img_for_click = image.resize((display_width, display_height), Image.Resampling.LANCZOS)

            current_counter = st.session_state.reset_counters[original_name]
            
            # 실시간 좌표와 무브먼트를 연속 감지하는 컴포넌트 호출
            value = streamlit_image_coordinates(
                preview_img_for_click, 
                key=f"click_{original_name}_{current_counter}"
            )
            
        if value is not None:
            x = int(int(value["x"]) / scale_ratio)
            y = int(int(value["y"]) / scale_ratio)
            
            if 0 <= x < w and 0 <= y < h:
                rgb = img_array[:, :, :3]
                mask_img = Image.fromarray(st.session_state.bg_masks[original_name] * 255).convert("L")
                draw = ImageDraw.Draw(mask_img)
                
                if "🔴" in mode:
                    # 스마트 배경 자동 제거
                    target_color = rgb[y, x]
                    color_diff = np.abs(rgb - target_color)
                    color_mask = np.all(color_diff < 15, axis=-1)
                    current_mask = np.where(color_mask, 255, 0).astype(np.uint8)
                    temp_mask_img = Image.fromarray(current_mask)
                    mask_img = Image.blend(mask_img, temp_mask_img, 1.0)
                    st.session_state.last_mouse_pos = None # 좌표 초기화
                else:
                    # 💡 [연속 드래그 붓 터치 시뮬레이션]
                    # 이전 마우스 위치가 있다면 끊어지지 않게 선(Line)으로 연결하여 슥슥 문지르는 효과를 구현합니다.
                    if st.session_state.last_mouse_pos is not None:
                        lx, ly = st.session_state.last_mouse_pos
                        draw.line([lx, ly, x, y], fill=0, width=brush_size * 2)
                    
                    # 현재 마우스 위치에 둥근 브러시 칠하기
                    draw.ellipse([x - brush_size, y - brush_size, x + brush_size, y + brush_size], fill=0)
                    st.session_state.last_mouse_pos = (x, y)
                
                st.session_state.bg_masks[original_name] = np.array(mask_img) // 255

        # 최종 투명도 반영
        accumulated_mask = st.session_state.bg_masks[original_name]
        rgb = img_array[:, :, :3]
        alpha = img_array[:, :, 3].copy()
        alpha[accumulated_mask == 1] = 0
        
        output_image = Image.fromarray(np.dstack((rgb, alpha)))

        with col2:
            st.write("✨ 실시간 결과 이미지")
            bg_checker = Image.new("RGBA", output_image.size, (255, 255, 255, 255))
            draw_grid = ImageDraw.Draw(bg_checker)
            grid_size = 16
            for i in range(0, w, grid_size):
                for j in range(0, h, grid_size):
                    if (i // grid_size + j // grid_size) % 2 == 0:
                        draw_grid.rectangle([i, j, i + grid_size, j + grid_size], fill=(240, 240, 240, 255))
            
            preview_img = Image.alpha_composite(bg_checker, output_image).resize((display_width, display_height))
            st.image(preview_img, caption="💡 격자 부분 = 투명하게 지워진 영역")
            
            buf = io.BytesIO()
            output_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label=f"📥 {new_filename} 다운로드",
                data=byte_im,
                file_name=new_filename,
                mime="image/png",
                key=f"dl_{original_name}"
            )
            
            if st.button("🔄 처음부터 다시 하기 (초기화)", key=f"reset_{original_name}"):
                if original_name in st.session_state.bg_masks:
                    st.session_state.bg_masks[original_name] = np.zeros((h, w), np.uint8)
                st.session_state.last_mouse_pos = None
                st.session_state.reset_counters[original_name] += 1
                st.rerun()
