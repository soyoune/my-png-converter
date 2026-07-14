import streamlit as st
from streamlit_canvas import st_canvas
from PIL import Image

st.title("🎨 캐릭터 배경 지우개 & 복구 브러시")

# 1. 이미지 업로드
uploaded_file = st.file_uploader("이미지를 선택하세요...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    bg_image = Image.open(uploaded_file)
    width, height = bg_image.size
    
    # 브라우저 화면 크기에 맞게 리사이징 비율 계산 (예: 가로 600px 기준)
    display_width = 600
    display_height = int(height * (display_width / width))

    # 2. 작업 모드 및 브러시 설정
    mode = st.radio("👉 작업 모드를 선택하세요:", ("🔴 배경 지우기", "🟢 잘못 지워진 곳 복구 (브러시)"))
    stroke_width = st.slider("🖌️ 브러시 크기 조절", 1, 100, 15)

    # 모드에 따른 브러시 색상 설정 (배경 지우기는 투명/검은색, 복구는 흰색 등 앱 기획에 맞게 설정)
    stroke_color = "#000000" if mode == "🔴 배경 지우기" else "#FFFFFF"

    st.subheader("👇 이미지 위에서 마우스를 꾹 누르고 슥슥 문질러보세요!")
    
    # 3. 캔버스 컴포넌트 실행 (실시간 드래그 및 되돌리기 완벽 지원)
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",  # 채우기 색상
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_image=bg_image.resize((display_width, display_height)),
        update_streamlit=True,
        height=display_height,
        width=display_width,
        drawing_mode="freedraw",  # 마우스 드래그(자유 그리기) 모드 활성화
        key="canvas",
    )

    # 4. 결과물 처리
    if canvas_result.image_data is not None:
        # canvas_result.image_data에 사용자가 그린 투명도(Alpha) 채널과 그림이 실시간으로 담깁니다.
        # 이 데이터를 활용해 배경을 마스킹하거나 복구하는 로직을 작성하시면 됩니다.
        st.image(canvas_result.image_data, caption="실시간 결과 이미지")
