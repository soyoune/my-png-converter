import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io
import os

st.title("🎨 무오류 스마트 배경 제거 및 복구기")
st.write("슬라이더를 조절해 마우스를 슥슥 문지르듯 넓은 영역을 한 번에 지우거나 복구해보세요!")

# 작업 모드 선택
mode = st.radio(
    "👉 작업 모드를 선택하세요:",
    ["🔴 문질러서 투명하게 지우기", "🟢 잘못 지워진 곳 다시 채우기(복구)"],
    horizontal=True
)

# 붓 크기를 키우면 한 번의 클릭으로도 드래그하듯 넓은 면적을 지울 수 있습니다.
brush_size = st.slider("🖌️ 붓(브러시) 크기 조절 (크게 할수록 대형 드래그 효과!)", min_value=10, max_value=150, value=50, step=10)

uploaded_file = st.file_uploader(
    "이미지를 선택하세요...", 
    type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file:
    # 세션 상태에 마스크가 없으면 초기화 (0: 유지, 1: 지움)
    if "mask_layer" not in st.session_state:
        st.session_state.mask_layer = None

    # 원본 이미지 로드
    image = Image.open(uploaded_file).convert("RGBA")
    img_array = np.array(image)
    h, w = img_array.shape[:2]

    if st.session_state.mask_layer is None:
        st.session_state.mask_layer = np.zeros((h, w), np.uint8)

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("📍 **[1단계: 위치 지정 및 문지르기]**")
        st.image(image, use_container_width=True, caption="원본 이미지")
        
        # 💡 마우스 드래그 감도 조절처럼 가로/세로 슬라이더를 움직여 붓을 슥슥 문지릅니다.
        st.write("👇 슬라이더를 움직여 지우거나 복구할 중심 위치를 잡으세요.")
        x_pos = st.slider("↔️ 가로 위치 조절 (좌/우 문지르기)", 0, w, w // 2)
        y_pos = st.slider("↕️ 세로 위치 조절 (상/하 문지르기)", 0, h, h // 2)
        
        # 문지르기 적용 버튼
        if st.button("✨ 선택 영역 슥슥 문지르기 적용", use_container_width=True):
            mask_img = Image.fromarray(st.session_state.mask_layer * 255).convert("L")
            draw = ImageDraw.Draw(mask_img)
            
            fill_val = 255 if "🔴" in mode else 0
            # 설정한 브러시 크기만큼 둥글고 넓게 칠해버림 (드래그 효과)
            draw.ellipse(
                [x_pos - brush_size, y_pos - brush_size, x_pos + brush_size, y_pos + brush_size], 
                fill=fill_val
            )
            st.session_state.mask_layer = np.array(mask_img) // 255
            st.rerun()

    with col2:
        st.write("✨ **[2단계: 실시간 결과 확인]**")
        
        # 알파 채널에 마스크 적용
        rgb = img_array[:, :, :3]
        alpha = img_array[:, :, 3].copy()
        alpha[st.session_state.mask_layer == 1] = 0
        output_image = Image.fromarray(np.dstack((rgb, alpha)))
        
        # 투명 격자 배경판 생성
        bg_checker = Image.new("RGBA", output_image.size, (255, 255, 255, 255))
        draw_grid = ImageDraw.Draw(bg_checker)
        grid_size = 16
        for i in range(0, w, grid_size):
            for j in range(0, h, grid_size):
                if (i // grid_size + j // grid_size) % 2 == 0:
                    draw_grid.rectangle([i, j, i + grid_size, j + grid_size], fill=(240, 240, 240, 255))
        
        # 결과물 합성
        preview_img = Image.alpha_composite(bg_checker, output_image)
        st.image(preview_img, use_container_width=True, caption="💡 격자 부분 = 투명하게 지워진 영역")
        
        # 다운로드 버튼
        buf = io.BytesIO()
        output_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        file_name, _ = os.path.splitext(uploaded_file.name)
        st.download_button(
            label=f"📥 new_{file_name}.png 다운로드",
            data=byte_im,
            file_name=f"new_{file_name}.png",
            mime="image/png",
            use_container_width=True
        )
        
        if st.button("🔄 처음부터 다시 하기 (초기화)", use_container_width=True):
            st.session_state.mask_layer = np.zeros((h, w), np.uint8)
            st.rerun()
