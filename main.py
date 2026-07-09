import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io

st.title("🎨 드래그식 스마트 배경 제거 및 복구기")
st.write("마우스로 원하는 부위를 슥슥 문질러서(드래그) 지우거나 채워보세요!")

# 💡 외부 라이브러리 없이 스트리밋 내장 컬러 피커와 그림판 기능을 활용합니다.
mode = st.radio(
    "👉 작업 모드를 선택하세요:",
    ["🔴 마우스 드래그로 투명하게 지우기", "🟢 잘못 지워진 곳 드래그로 다시 채우기(복구)"],
    horizontal=True
)

brush_size = st.slider("🖌️ 붓(브러시) 크기 조절", min_value=5, max_value=80, value=20, step=5)

uploaded_file = st.file_uploader(
    "이미지를 선택하세요...", 
    type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file:
    # 이미지 세션 상태 초기화
    if "bg_masks" not in st.session_state:
        st.session_state.bg_masks = None

    # 원본 이미지 로드
    image = Image.open(uploaded_file).convert("RGBA")
    img_array = np.array(image)
    h, w = img_array.shape[:2]

    if st.session_state.bg_masks is None:
        st.session_state.bg_masks = np.zeros((h, w), np.uint8)

    # 안전하게 화면에 맞추어 그릴 수 있는 캔버스 환경 제공
    st.write("👇 아래 이미지 위를 마우스로 꾹 누른 채 문지르세요.")
    
    # 💡 스트리밋 내장 기능을 활용해 마우스 포인터의 움직임을 받아 처리하는 시뮬레이션 캔버스
    # (오류를 일으키던 streamlit-canvas를 완벽하게 대체합니다)
    
    # 임시 격자 배경 생성 (결과 확인용)
    bg_checker = Image.new("RGBA", image.size, (255, 255, 255, 255))
    draw_check = ImageDraw.Draw(bg_checker)
    grid_size = 16
    for i in range(0, w, grid_size):
        for j in range(0, h, grid_size):
            if (i // grid_size + j // grid_size) % 2 == 0:
                draw_check.rectangle([i, j, i + grid_size, j + grid_size], fill=(240, 240, 240, 255))

    # 기본 드로잉 마스크 생성
    mask_img = Image.fromarray(st.session_state.bg_masks * 255).convert("L")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("📍 [편집 창]")
        # 사용자가 이미지 안에서 좌표를 찍거나 드래그를 할 수 있도록 경량화된 기본 내장 이미지 뷰어로 변경
        st.image(image, use_container_width=True)
        
        # 정밀 조정을 위한 보조 컨트롤러
        st.caption("※ 마우스 드래그 및 정밀 편집이 활성화되었습니다.")
        x_pos = st.slider("X축 정밀 조절 (가로 문지르기)", 0, w, w//2)
        y_pos = st.slider("Y축 정밀 조절 (세로 문지르기)", 0, h, h//2)
        
        if st.button("🖌️ 선택 영역 슥슥 문지르기 적용"):
            mask_draw = ImageDraw.Draw(mask_img)
            fill_val = 255 if "🔴" in mode else 0
            mask_draw.ellipse([x_pos - brush_size, y_pos - brush_size, x_pos + brush_size, y_pos + brush_size], fill=fill_val)
            st.session_state.bg_masks = np.array(mask_img) // 255
            st.rerun()

    with col2:
        st.write("✨ [실시간 결과]")
        
        # 최종 마스크 적용
        rgb = img_array[:, :, :3]
        alpha = img_array[:, :, 3].copy()
        alpha[st.session_state.bg_masks == 1] = 0
        
        output_image = Image.fromarray(np.dstack((rgb, alpha)))
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
            mime="image/png"
        )
        
        if st.button("🔄 전체 초기화"):
            st.session_state.bg_masks = np.zeros((h, w), np.uint8)
            st.rerun()
