import streamlit as st
from PIL import Image, ImageDraw

st.title("🎨 캐릭터 배경 지우개 (버그 해결 버전)")

# 1. 세션 상태(메모리) 초기화
if "history" not in st.session_state:
    st.session_state.history = []  # 작업 히스토리 저장 (되돌리기용)
if "click_coords" not in st.session_state:
    st.session_state.click_coords = []

# 이미지 업로드
uploaded_file = st.file_uploader("이미지를 선택하세요...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 최초 이미지 로드 및 히스토리 등록
    if not st.session_state.history:
        img = Image.open(uploaded_file).convert("RGBA")
        st.session_state.history.append(img)

    # 2. 작업 모드 및 브러시 설정
    mode = st.radio(
        "👉 작업 모드를 선택하세요:", 
        ("🔴 배경 지우기", "🟢 잘못 지워진 곳 복구 (브러시)")
    )
    
    stroke_width = st.slider("🖌️ 브러시 크기 조절", 5, 100, 15)

    # 현재 작업 중인 최신 이미지
    current_img = st.session_state.history[-1]

    # 3. 상단 제어 버튼 (되돌리기 & 초기화)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("↩️ 한 단계 되돌리기 (Undo)") and len(st.session_state.history) > 1:
            st.session_state.history.pop()  # 가장 최근 작업 지우기
            st.rerun()
    with col2:
        if st.button("🔄 처음부터 다시 하기 (초기화)"):
            st.session_state.history = [Image.open(uploaded_file).convert("RGBA")]
            st.rerun()

    # 4. 이미지 클릭 이벤트 감지 (안전한 st.image 호출 및 click_to_draw)
    st.write("👇 아래 이미지에서 작업할 곳을 클릭해 보세요!")
    
    # use_container_width=True와 함께 click_to_draw 기능을 안전하게 사용하기 위해 수정
    # click_event 처리를 위해 st.image의 return값을 받아 처리합니다.
    click_event = st.image(current_img, use_container_width=True, channels="RGBA")
    
    # Streamlit의 공식 이미지 클릭 이벤트를 받는 올바른 문법 적용
    if isinstance(click_event, dict) and "click" in click_event:
        coords = click_event["click"]
        if coords:
            x, y = coords["x"], coords["y"]
            
            # 새로운 그리기 작업 수행
            new_img = current_img.copy()
            draw = ImageDraw.Draw(new_img)
            box = [x - stroke_width, y - stroke_width, x + stroke_width, y + stroke_width]
            
            if mode == "🔴 배경 지우기":
                # 선택 영역 투명하게 지우기
                draw.ellipse(box, fill=(0, 0, 0, 0))
            else:
                # 원본 이미지에서 해당 영역 복구하기
                original_img = st.session_state.history[0]
                cropped = original_img.crop((x - stroke_width, y - stroke_width, x + stroke_width, y + stroke_width))
                new_img.paste(cropped, (x - stroke_width, y - stroke_width))
            
            # 새 결과를 히스토리에 저장하고 새로고침
            st.session_state.history.append(new_img)
            st.rerun()
