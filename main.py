import streamlit as st
from PIL import Image, ImageDraw, ImageChops
import numpy as np
import io
import os
from streamlit_image_coordinates import streamlit_image_coordinates

st.title("🎨 로고·캐릭터 완벽 보호 배경 지우개")
st.write("1. **로고 바깥쪽의 배경**을 콕 찍어보세요. 이제 안쪽의 흰색은 전혀 파먹지 않고 겉에만 싹 빠집니다!")
st.write("2. 미세하게 남은 외각선이나 모서리는 모드를 바꿔서 **브러시로 슥슥 문질러** 복구하세요.")

# 작업 모드 선택
mode = st.radio(
    "👉 작업 모드를 선택하세요:",
    ["🔴 외각 배경만 한 번에 지우기 (로고 내부 완벽 보호)", "🟢 잘못 지워진 곳 슥슥 문질러 채우기 (포토샵형 복구 브러시)"],
    horizontal=True
)

# 브러시 크기 조절
brush_size = st.slider("🖌️ 복구 브러시 크기 조절", min_value=10, max_value=100, value=25, step=5)

# [포토샵 원형 커서 효과] 
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
            st.write("👇 로고 바깥쪽 배경 영역을 콕 찍어주세요.")
            
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
                mask_img = Image.fromarray(st.session_state.bg_masks[original_name] * 255).convert("L")
                
                if "🔴" in mode:
                    # 💡 [핵심 알고리즘 교체: Flood Fill]
                    # 전체 화면에서 색상을 찾는 게 아니라, 클릭한 지점부터 사방으로 퍼져나가며 
                    # 경계선(로고 테두리)에 막힐 때까지만 채우는 방식입니다.
                    # 이 방식은 로고 내부의 흰색 글자나 아이콘을 절대로 침범하지 않습니다!
                    rgb_img = image.convert("RGB")
                    # 오차 범위를 15로 주어 미세한 압축 노이즈까지 깔끔하게 외곽선을 잡아냅니다.
                    flood_mask = Image3 = ImageDraw.floodfill(rgb_img, xy=(x, y), value=(255, 0, 0), thresh=15)
                    
                    # 칠해진 영역(빨간색)만 추출하여 마스크로 변환
                    np_rgb = np.array(rgb_img)
                    flood_zone = (np_rgb[:,:,0] == 255) & (np_rgb[:,:,1] == 0) & (np_rgb[:,:,2] == 0)
                    
                    # 기존 마스크와 병합
                    current_mask = np.where(flood_zone, 255, np.array(mask_img)).astype(np.uint8)
                    mask_img = Image.fromarray(current_mask)
                    st.session_state.last_mouse_pos = None 
                else:
                    # 🟢 슥슥 복구 브러시 효과
                    draw = ImageDraw.Draw(mask_img)
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
