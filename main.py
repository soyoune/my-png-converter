import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io
import os
# 💡 AI 자동 배경 제거 및 마우스 드래그 처리를 위한 라이브러리 추가
from rembg import remove
from streamlit_canvas import st_canvas

st.title("🎯 스마트 AI 배경 제거 및 드래그 복구기")
st.write("이미지를 올리면 AI가 배경을 자동으로 지워줍니다! 혹시 파먹은 곳이 있다면 마우스로 슥슥 문질러서 복구하세요.")

# 작업 모드 선택
mode = st.radio(
    "👉 작업 모드를 선택하세요:",
    ["🤖 AI 자동 배경 제거 (기본 적용)", "🧹 마우스 드래그로 더 지우기", "🟢 잘못 지워진 곳 드래그로 다시 채우기(복구)"],
    horizontal=True,
    index=0 # 기본적으로 AI 자동 제거 모드로 설정
)

# 브러시 크기 조절
brush_size = st.slider("🖌️ 붓(브러시) 크기 조절", min_value=5, max_value=100, value=25, step=5)

uploaded_files = st.file_uploader(
    "이미지를 선택하세요...", 
    type=["jpg", "jpeg", "png", "webp"], 
    accept_multiple_files=True
)

if uploaded_files:
    if "bg_masks" not in st.session_state:
        st.session_state.bg_masks = {}
    if "auto_removed_images" not in st.session_state:
        st.session_state.auto_removed_images = {}

    for uploaded_file in uploaded_files:
        original_name = uploaded_file.name
        file_name, _ = os.path.splitext(original_name)
        new_filename = f"new_{file_name}.png"
        
        st.markdown("---")
        st.subheader(f"작업 파일: {original_name}")
        
        # 원본 이미지 로드
        image = Image.open(uploaded_file).convert("RGBA")
        img_array = np.array(image)
        h, w = img_array.shape[:2]
        
        # 고정된 화면 보기 크기 설정 (350픽셀 가로 고정)
        display_width = 350
        scale_ratio = display_width / w
        display_height = int(h * scale_ratio)
        
        # 💡 [핵심 추가] AI를 이용해 자동으로 배경을 제거한 초기 이미지 생성
        if original_name not in st.session_state.auto_removed_images:
            with st.spinner('🚀 AI가 배경을 분석하여 지우고 있습니다...잠시만 기다려주세요.'):
                # rembg를 이용해 배경 제거 (알파 채널 생성)
                auto_removed = remove(image)
                st.session_state.auto_removed_images[original_name] = auto_removed
                
                # AI가 지운 영역을 누적 마스크 초기값으로 설정
                auto_alpha = np.array(auto_removed)[:, :, 3]
                initial_mask = (auto_alpha == 0).astype(np.uint8)
                st.session_state.bg_masks[original_name] = initial_mask
                
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("👇 추가로 지우거나 복구할 부위를 마우스로 드래그(문지르기)하세요.")
            
            # 수동 지우기/복구용 캔버스 구성
            # 지우기는 하얗게칠하고, 복구는 까맣게칠해서 마스크를 조정
            stroke_color = "#FFFFFF" if "🧹" in mode else "#000000"
            drawing_mode = "freedraw" if ("🧹" in mode or "🟢" in mode) else "transform"
            
            # AI가 1차로 지운 이미지를 캔버스 배경으로 설정
            canvas_bg = st.session_state.auto_removed_images[original_name]
            
            # 💡 드래그 입력을 받는 실시간 캔버스 생성
            canvas_result = st_canvas(
                fill_color="rgba(255, 165, 0, 0.3)", # 오렌지색 투명 채우기
                stroke_width=int(brush_size * scale_ratio), # 화면 비율에 맞는 붓 크기
                stroke_color=stroke_color,
                background_image=canvas_bg.resize((display_width, display_height)),
                update_streamlit=True,
                height=display_height,
                width=display_width,
                drawing_mode=drawing_mode,
                key=f"canvas_{original_name}_{mode}", # 모드가 바뀔 때마다 캔버스 갱신
            )
            
        # 드래그한 마우스 궤적(데이터)이 존재할 때 누적 마스크 계산
        if canvas_result.image_data is not None and drawing_mode == "freedraw":
            # 캔버스에 그려진 선(마스크) 추출
            drawn_mask = canvas_result.image_data[:, :, 0] > 0
            
            # 화면 크기 마스크를 다시 원본 고해상도 크기로 복원
            drawn_mask_resized = np.array(Image.fromarray(drawn_mask).resize((w, h), Image.Resampling.NEAREST))
            
            if "🧹" in mode:
                # 더 지우기: 드래그한 영역을 투명 마스크에 추가 (OR 연산)
                st.session_state.bg_masks[original_name] = np.logical_or(
                    st.session_state.bg_masks[original_name], drawn_mask_resized
                ).astype(np.uint8)
            elif "🟢" in mode:
                # 복구하기: 드래그한 영역을 투명 마스크에서 제거 (AND NOT 연산)
                st.session_state.bg_masks[original_name] = np.logical_and(
                    st.session_state.bg_masks[original_name], np.logical_not(drawn_mask_resized)
                ).astype(np.uint8)

        # 💡 최종 누적 마스크를 원본에 투명도로 적용
        accumulated_mask = st.session_state.bg_masks[original_name]
        rgb = img_array[:, :, :3]
        alpha = img_array[:, :, 3].copy()
        alpha[accumulated_mask == 1] = 0
        
        output_image = Image.fromarray(np.dstack((rgb, alpha)))
        
        # 우측 결과 출력 및 다운로드 영역
        with col2:
            st.write("✨ 실시간 최종 결과 이미지")
            
            # 배경 투명 격자판 생성
            bg_checker = Image.new("RGBA", output_image.size, (255, 255, 255, 255))
            draw = ImageDraw.Draw(bg_checker)
            grid_size = 16
            for i in range(0, w, grid_size):
                for j in range(0, h, grid_size):
                    if (i // grid_size + j // grid_size) % 2 == 0:
                        draw.rectangle([i, j, i + grid_size, j + grid_size], fill=(240, 240, 240, 255))
            
            # 미리보기 이미지 합성 및 화면 크기에 맞게 조정
            preview_img = Image.alpha_composite(bg_checker, output_image).resize((display_width, display_height))
            st.image(preview_img, caption="💡 격자 부분 = 투명하게 지워진 영역")
            
            # 다운로드 버튼
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
            
            # 초기화 버튼 (AI 자동 제거 상태로 되돌림)
            if st.button("🔄 AI 자동 제거 상태로 초기화", key=f"reset_{original_name}"):
                if original_name in st.session_state.auto_removed_images:
                    # AI가 지운 초기 마스크 상태로 복구
                    auto_alpha = np.array(st.session_state.auto_removed_images[original_name])[:, :, 3]
                    st.session_state.bg_masks[original_name] = (auto_alpha == 0).astype(np.uint8)
                st.rerun()
