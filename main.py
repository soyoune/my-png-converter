import streamlit as st
from PIL import Image, ImageDraw

st.title("🎨 캐릭터 배경 지우개 (버그 해결 버전)")

# 세션 상태(메모리) 초기화
if "history" not in st.session_state:
    st.session_state.history = []  # 작업 되돌리기용 히스토리
if "last_clicked" not in st.session_state:
    st.session_state.last_clicked = None

# 1. 이미지 업로드
uploaded_file = st.file_uploader("이미지를 선택하세요...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 최초 이미지 로드 및 히스토리 등록
    if not st.session_state.history:
        img = Image.open(uploaded_file).convert("RGBA")
        st.session_state.history.append(img)

    # 2. 작업 모드 선택 (모드가 바뀔 때 이전 클릭 좌표를 강제로 비움)
    mode = st.radio(
        "👉 작업 모드를 선택하세요:", 
        ("🔴 배경 지우기", "🟢 잘못 지워진 곳 복구 (브러시)")
    )
    
    # 모드가 변경되면 이전 클릭 위치 정보를 초기화하여 '엉뚱한 곳 채워짐' 버그 원천 차단
    if st.session_state.last_clicked is not None:
        st.session_state.last_clicked = None

    stroke_width = st.slider("🖌️ 브러시 크기 조절", 5, 100, 15)

    # 현재 작업 중인 최신 이미지 가져오기
    current_img = st.session_state.history[-1]

    # 3. 되돌리기(Undo) 버튼 구현!
    col1, col2 = st.columns(2)
    with col1:
        if st.button("↩️ 한 단계 되돌리기 (Undo)") and len(st.session_state.history) > 1:
            st.session_state.history.pop()  # 가장 최근 작업 제거
            st.rerun()
    with col2:
        if st.button("🔄 처음부터 다시 하기 (초기화)"):
            st.session_state.history = [Image.open(uploaded_file).convert("RGBA")]
            st.session_state.last_clicked = None
            st.rerun()

    # 4. 이미지 클릭 이벤트 처리
    st.write("👇 아래 이미지를 클릭하여 지우거나 복구해 보세요.")
    
    # 사용자 클릭 좌표 감지 (st.image의 click_events 기능 활용)
    value = st.image(current_img, use_container_width=True)
    
    # 새로운 클릭이 발생했을 때만 동작
    if value and "click" in value:
        x, y = value["click"]["x"], value["click"]["y"]
        
        # 클릭한 좌표가 이전과 다를 때만 그리기 실행 (무한 루프 방지)
        current_click = (x, y)
        if st.session_state.last_clicked != current_click:
            st.session_state.last_clicked = current_click
            
            # 새 도화지 생성 및 그리기 준비
            new_img = current_img.copy()
            draw = ImageDraw.Draw(new_img)
            
            # 클릭한 좌표 계산 (원래 이미지 크기에 맞게 스케일링 필요 시 조절 가능)
            box = [x - stroke_width, y - stroke_width, x + stroke_width, y + stroke_width]
            
            if mode == "🔴 배경 지우기":
                # 클릭한 지점을 투명하게(RGBA의 A를 0으로) 지움
                draw.ellipse(box, fill=(0, 0, 0, 0))
            else:
                # 원본 이미지(첫 번째 기록)에서 잘려 나간 부분을 다시 가져와 덮어씌움 (복구)
                original_img = st.session_state.history[0]
                cropped = original_img.crop((x - stroke_width, y - stroke_width, x + stroke_width, y + stroke_width))
                new_img.paste(cropped, (x - stroke_width, y - stroke_width))
            
            # 히스토리에 새 이미지 추가 후 화면 갱신
            st.session_state.history.append(new_img)
            st.rerun()
