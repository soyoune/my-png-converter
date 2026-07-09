import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io
import os
from streamlit_image_coordinates import streamlit_image_coordinates

st.title("🎯 캐릭터 보호 배경 지우개 & 슥슥 복구 브러시")
st.write("1. 배경을 클릭하면 캐릭터 안쪽을 파먹지 않고 외곽 배경만 조심스럽게 지워집니다.")
st.write("2. 모드를 전환한 뒤 이미지 위에서 마우스를 꾹 누른 채 **슥~~슥~~** 움직여 복구해 보세요!")

# 작업 모드 선택
mode = st.radio(
    "👉 작업 모드를 선택하세요:",
    ["🔴 터치하여 배경 한 번에 지우기 (캐릭터 보호 모드)", "🟢 잘못 지워진 곳 슥슥 문질러 채우기 (포토샵형 복구 브러시)"],
    horizontal=True
)

# 브러시 크기 조절
brush_size = st.slider("🖌️ 복구 브러시 크기 조절", min_value=10, max_value=100, value=25, step=5)

# 💡 [포토샵 원형 커서 효과] 마우스 주변에 브러시 크기 모양의 원형 점선 가이드라인이 부드럽게 따라다닙니다.
style_template = """
<style>
.stImageCoordinates, .stImageCoordinates img, img {{
    cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="{dw}" height="{dw}" viewBox="0 0 {dw} {dw}"><circle cx="{bs}" cy="{bs}" r="{r}" stroke="%23ff4b4b" stroke-width="1.5" fill="none" stroke-dasharray="3,3"/></svg>') {bs} {bs}, crosshair !important;
}}
</style>
"""
st.markdown(
    style_template.format(dw=brush_size * 2, bs=brush_size, r=brush_size - 1),
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
    # 💡 드래그할 때 끊기지 않고 부드럽게 이어지도록 마우스 이전 좌표 기억 장치
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
            
        image = Image.open(uploaded_file).convert("RGBA")
        img_array = np.array(image)
        h, w = img_array.shape[:2]
        
        if original_name not in st.session_state.bg_masks:
            st.session_state.bg_masks[original_name] = np.zeros((h, w), np.uint8)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("👇 이미지 위에서 마우스를 꾹 누른 채 움직이거나 터치하세요.")
            
            display_width = 350
            scale_ratio = display_width / w
            display_height = int(h * scale_ratio)
            preview_img_for_click = image.resize((display_width, display_height), Image.Resampling.LANCZOS)

            current_counter = st.session_state.reset_counters[original_name]
            
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
                    # 💡 [핵심 수정] 캐릭터 파먹기 방지 알고리즘 적용
                    # 오차 허용 범위를 기존 15에서 '8'로 대폭 줄여 피부나 옷 내부로 침범하는 현상을 원천 방지합니다.
                    target_color = rgb[y, x]
                    color_diff = np.abs(rgb - target_color)
                    color_mask = np.all(color_diff < 8, axis=-1)
                    
                    current_mask = np.where(color_mask, 255, 0).astype(np.uint8)
                    temp_mask_img = Image.fromarray(current_mask)
                    mask_img = Image.blend(mask_img, temp_mask_img, 1.0)
                    st.session_state.last_mouse_pos = None 
                else:
                    # 💡 [연속 붓 터치 드래그 효과] 
                    # 사용자가 마우스를 움직일 때 이전 좌표와 현재 좌표를 부드러운 '선(Line)'으로 이어주어 
                    # 콕콕 찍지 않고 슥~~슥~~ 문지르는 브러시 느낌을 그대로 재현합니다.
                    if st.session_state.last_mouse_pos is not None:
                        lx, ly = st.session_state.last_mouse_pos
                        draw.line([lx, ly, x, y], fill=0, width=brush_size * 2)
                    
                    draw.ellipse([x - brush_size, y - brush_size, x + brush_size, y + brush_size], fill=0)
                    st.session_state.last_mouse_pos = (x, y)
                
                st.session_state.bg_masks[original_name] = np.array(mask_img) // 255

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
