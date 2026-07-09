import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io
import os
from streamlit_image_coordinates import streamlit_image_coordinates

st.title("🎯 스마트 배경 지우개 & 복구 브러시")
st.write("1. 배경을 클릭해 캐릭터를 보호하면서 배경을 싹 지우세요.")
st.write("2. 파먹힌 부분이나 미세한 곳은 모자를 보호하며 브러시 모드로 문질러 복구하세요!")

# 💡 모드 선택 (첫 번째 모드로 배경을 넓게 지우고 시작합니다)
mode = st.radio(
    "👉 작업 모드를 선택하세요:",
    ["🔴 터치하여 배경 한 번에 지우기 (캐릭터 보호)", "🧹 덜 지워진 곳 조금씩 지우기 (지우개 브러시)", "🟢 잘못 지워진 곳 조금씩 채우기 (복구 브러시)"],
    horizontal=True
)

# 브러시 크기 조절
brush_size = st.slider("🖌️ 지우개 / 복구 브러시 크기 조절", min_value=5, max_value=80, value=20, step=5)

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
        
        # 누적 마스크 초기화 (0: 유지, 1: 투명화)
        if original_name not in st.session_state.bg_masks:
            st.session_state.bg_masks[original_name] = np.zeros((h, w), np.uint8)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("👇 아래 이미지에서 작업을 원하는 곳을 콕 찍으세요.")
            
            # 화면 크기에 맞게 미리보기 이미지 조절 (가로 350 고정)
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
            # 클릭 좌표를 원본 고해상도 좌표로 변환
            x = int(int(value["x"]) / scale_ratio)
            y = int(int(value["y"]) / scale_ratio)
            
            if 0 <= x < w and 0 <= y < h:
                rgb = img_array[:, :, :3]
                alpha = img_array[:, :, 3]
                
                # 마스크를 조절하기 위해 PIL ImageDraw 활용
                mask_img = Image.fromarray(st.session_state.bg_masks[original_name] * 255).convert("L")
                draw = ImageDraw.Draw(mask_img)
                
                if "🔴" in mode:
                    # 💡 [캐릭터 보호용 스마트 자동 지우개]
                    # 선택한 타겟 색상(배경)과 비슷한 색상만 원본 전체에서 찾아 지웁니다.
                    target_color = rgb[y, x]
                    # 캐릭터 피부톤이나 옷색상으로 번지는 것을 막기 위해 오차 범위를 아주 깐깐하게(15) 잡음
                    color_diff = np.abs(rgb - target_color)
                    color_mask = np.all(color_diff < 15, axis=-1)
                    
                    # 찾아낸 배경 영역을 투명화 마스크에 병합
                    current_mask = np.where(color_mask, 255, 0).astype(np.uint8)
                    temp_mask_img = Image.fromarray(current_mask)
                    mask_img = Image.blend(mask_img, temp_mask_img, 1.0)
                    
                elif "🧹" in mode:
                    # 🧹 수동 지우개 브러시: 마우스 주변을 브러시 크기만큼 싹 지우기
                    draw.ellipse([x - brush_size, y - brush_size, x + brush_size, y + brush_size], fill=255)
                    
                else:
                    # 🟢 수동 복구 브러시: 얼굴이나 모자가 파먹힌 부위를 찍으면 원본으로 깨끗하게 복구!
                    draw.ellipse([x - brush_size, y - brush_size, x + brush_size, y + brush_size], fill=0)
                
                st.session_state.bg_masks[original_name] = np.array(mask_img) // 255

        # 최종 마스크 적용하여 투명도 반영
        accumulated_mask = st.session_state.bg_masks[original_name]
        rgb = img_array[:, :, :3]
        alpha = img_array[:, :, 3].copy()
        alpha[accumulated_mask == 1] = 0
        
        output_image = Image.fromarray(np.dstack((rgb, alpha)))

        # 우측 결과 출력 및 다운로드 영역
        with col2:
            st.write("✨ 실시간 결과 이미지")
            
            # 투명 격자 배경판 만들기
            bg_checker = Image.new("RGBA", output_image.size, (255, 255, 255, 255))
            draw_grid = ImageDraw.Draw(bg_checker)
            grid_size = 16
            for i in range(0, w, grid_size):
                for j in range(0, h, grid_size):
                    if (i // grid_size + j // grid_size) % 2 == 0:
                        draw_grid.rectangle([i, j, i + grid_size, j + grid_size], fill=(240, 240, 240, 255))
            
            # 최종 미리보기 화면 합성
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
                st.session_state.reset_counters[original_name] += 1
                st.rerun()
