import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io
import os
from streamlit_image_coordinates import streamlit_image_coordinates

st.title("🎯 스마트 배경 제거 및 정밀 복구기")
st.write("얼굴이나 모자가 날아가지 않도록 터치 세기(오차 범위)와 정밀 복구 기능을 제공합니다.")

# 작업 모드 선택
mode = st.radio(
    "👉 작업 모드를 선택하세요:",
    ["🔴 터치하여 투명하게 지우기 (번짐 최소화)", "🟢 잘못 지워진 곳 조금씩 채우기 (정밀 복구)"],
    horizontal=True
)

# 💡 복구하거나 지울 때 범위를 조절할 수 있는 브러시 크기
brush_size = st.slider("🖌️ 붓(브러시) 크기 조절", min_value=5, max_value=60, value=15, step=5)

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
            
        # 원본 고화질 이미지 로드
        image = Image.open(uploaded_file).convert("RGBA")
        img_array = np.array(image)
        h, w = img_array.shape[:2]
        
        # 마스크 초기화 (0: 유지, 1: 지움)
        if original_name not in st.session_state.bg_masks:
            st.session_state.bg_masks[original_name] = np.zeros((h, w), np.uint8)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("👇 이미지 위를 콕콕 터치하여 편집하세요.")
            
            # 화면 세로 잘림 방지용 크기 제한
            max_size = 320
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
            # 미리보기 좌표 -> 원본 고해상도 좌표로 변환
            x = int(int(value["x"]) / scale_ratio)
            y = int(int(value["y"]) / scale_ratio)
            
            if 0 <= x < w and 0 <= y < h:
                # 💡 외부 라이브러리(OpenCV) 없이 순수 내장 PIL로 마스크 그리기 처리
                mask_img = Image.fromarray(st.session_state.bg_masks[original_name] * 255).convert("L")
                draw = ImageDraw.Draw(mask_img)
                
                if "🔴" in mode:
                    # 지우기: 터치한 중심을 기준으로 선택한 브러시 크기만큼 투명화 영역 추가
                    draw.ellipse([x - brush_size, y - brush_size, x + brush_size, y + brush_size], fill=255)
                else:
                    # 🟢 복구하기: 모자나 얼굴이 날아간 부위를 문지르면(터치하면) 그 부분만 원상복구
                    draw.ellipse([x - brush_size, y - brush_size, x + brush_size, y + brush_size], fill=0)
                
                st.session_state.bg_masks[original_name] = np.array(mask_img) // 255

        # 마스크 적용하여 투명도 반영
        accumulated_mask = st.session_state.bg_masks[original_name]
        rgb = img_array[:, :, :3]
        alpha = img_array[:, :, 3].copy()
        alpha[accumulated_mask == 1] = 0
        
        output_image = Image.fromarray(np.dstack((rgb, alpha)))

        # 결과 출력 및 다운로드 영역
        with col2:
            st.write("✨ 실시간 결과 이미지")
            
            # 투명 격자 배경판 만들기
            bg_checker = Image.new("RGBA", output_image.size, (255, 255, 255, 255))
            ch_w, ch_h = output_image.size
            grid_size = 16
            draw_grid = ImageDraw.Draw(bg_checker)
            for i in range(0, ch_w, grid_size):
                for j in range(0, ch_h, grid_size):
                    if (i // grid_size + j // grid_size) % 2 == 0:
                        draw_grid.rectangle([i, j, i + grid_size, j + grid_size], fill=(240, 240, 240, 255))
            
            # 최종 결과물 합성 후 화면 크기에 맞게 축소 표시
            if ch_w > max_size or ch_h > max_size:
                out_scale = min(max_size / ch_w, max_size / ch_h)
                res_w, res_h = int(ch_w * out_scale), int(ch_h * out_scale)
                preview_img = Image.alpha_composite(bg_checker, output_image).resize((res_w, res_h), Image.Resampling.LANCZOS)
            else:
                preview_img = Image.alpha_composite(bg_checker, output_image)
                
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
            
            if st.button("🔄 이 파일 처음부터 다시 지우기", key=f"reset_{original_name}"):
                if original_name in st.session_state.bg_masks:
                    st.session_state.bg_masks[original_name] = np.zeros((h, w), np.uint8)
                st.session_state.reset_counters[original_name] += 1
                st.rerun()
