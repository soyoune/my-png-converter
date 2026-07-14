import streamlit as st
from streamlit_canvas import st_canvas
from PIL import Image

st.title("🎨 캐릭터 배경 지우개 & 복구 브러시")

# 1. 이미지 업로드
uploaded_file = st.file_uploader("이미지를 선택하세요...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 안전하게 이미지를 열기 위해 예외 처리 추가
    try:
        bg_image = Image.open(uploaded_file)
        # RGBA 모드일 경우 RGB로 변환해 안전하게 처리
        if bg_image.mode in ("RGBA", "P"):
            bg_image = bg_image.convert("RGB")
            
        width, height = bg_image.size
        
        # 화면에 맞출 크기 조절
        display_width = 600
        display_height = int(height * (display_width / width))

        # 2. 작업 모드 및 브러시 설정
        mode = st.radio("👉 작업 모드를 선택하세요:", ("🔴 배경 지우기", "🟢 잘못 지워진 곳 복구 (브러시)"))
        stroke_width = st.slider("🖌️ 브러시 크기 조절", 1, 100, 15)

        # 드로잉 모드 설정
        drawing_mode = "freedraw"
        stroke_color = "#000000" if mode == "🔴 배경 지우기" else "#FFFFFF"

        st.subheader("👇 이미지 위에서 마우스를 꾹 누르고 슥슥 문질러보세요!")
        
        # 3. 캔버스 그리기
        canvas_result = st_canvas(
            fill_color="rgba(0, 0, 0, 0)",  # 채우기는 투명하게
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_image=bg_image.resize((display_width, display_height)),
            update_streamlit=True,
            height=display_height,
            width=display_width,
            drawing_mode=drawing_mode,
            key="canvas",
        )

        # 4. 실시간 결과 보여주기
        if canvas_result.image_data is not None:
            st.image(canvas_result.image_data, caption="마스크 영역 (그려진 부분)")

    except Exception as e:
        st.error(f"이미지를 처리하는 중 오류가 발생했습니다: {e}")
