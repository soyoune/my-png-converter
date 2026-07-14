import streamlit as st
from PIL import Image, ImageDraw
import io
import base64

st.title("🎨 캐릭터 배경 지우개 (정밀 클릭 완료)")

# 1. 세션 상태(메모리) 초기화
if "history" not in st.session_state:
    st.session_state.history = []

uploaded_file = st.file_uploader("이미지를 선택하세요...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 최초 이미지 로드 및 RGBA 변환
    if not st.session_state.history:
        img = Image.open(uploaded_file).convert("RGBA")
        st.session_state.history.append(img)

    # 2. 설정 UI
    mode = st.radio("👉 작업 모드를 선택하세요:", ("🔴 배경 지우기", "🟢 잘못 지워진 곳 복구 (브러시)"))
    stroke_width = st.slider("🖌️ 브러시 크기 조절", 5, 100, 15)

    current_img = st.session_state.history[-1]

    # 3. 제어 버튼 (되돌리기 & 초기화)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("↩️ 한 단계 되돌리기 (Undo)") and len(st.session_state.history) > 1:
            st.session_state.history.pop()
            st.rerun()
    with col2:
        if st.button("🔄 처음부터 다시 하기 (초기화)"):
            st.session_state.history = [Image.open(uploaded_file).convert("RGBA")]
            st.rerun()

    # --- HTML / 자바스크립트를 이용한 좌표 수집 우회 기법 ---
    # 이미지를 Base64 인코딩하여 HTML 내부에 렌더링하고, 클릭 좌표를 Streamlit 쿼리 파라미터로 전송
    buffered = io.BytesIO()
    current_img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # 이미지 클릭 시 좌표를 감지하여 Streamlit 페이지를 갱신하는 JS 코드
    html_code = f"""
    <div style="text-align: center;">
        <img id="clickable-img" src="data:image/png;base64,{img_str}" style="max-width: 100%; cursor: crosshair;" />
    </div>
    <script>
        var img = document.getElementById('clickable-img');
        img.addEventListener('click', function(e) {{
            var rect = e.target.getBoundingClientRect();
            var x = e.clientX - rect.left; // 클릭한 상대 X좌표
            var y = e.clientY - rect.top;  // 클릭한 상대 Y좌표
            
            // 실제 이미지 크기 비율에 맞춰 스케일 변환
            var scaleX = e.target.naturalWidth / rect.width;
            var scaleY = e.target.naturalHeight / rect.height;
            
            var realX = Math.round(x * scaleX);
            var realY = Math.round(y * scaleY);

            // Streamlit에 좌표 전달 (URL 쿼리 매개변수 사용)
            const url = new URL(window.location);
            url.searchParams.set('click_x', realX);
            url.searchParams.set('click_y', realY);
            url.searchParams.set('trigger', Date.now()); // 매번 실행되도록 트리거 추가
            window.parent.location.href = url.href;
        }});
    </script>
    """
    st.components.v1.html(html_code, height=500)

    # 클릭된 좌표가 주소창 파라미터에 들어왔는지 감지하고 그리기 수행
    query_params = st.query_params
    if "click_x" in query_params and "click_y" in query_params:
        x = int(query_params["click_x"])
        y = int(query_params["click_y"])
        
        # 쿼리 매개변수 즉시 제거 (무한 반복 방지)
        st.query_params.clear()

        # 도화지 복사 후 그리기
        new_img = current_img.copy()
        draw = ImageDraw.Draw(new_img)
        box = [x - stroke_width, y - stroke_width, x + stroke_width, y + stroke_width]

        if mode == "🔴 배경 지우기":
            draw.ellipse(box, fill=(0, 0, 0, 0))
        else:
            original_img = st.session_state.history[0]
            cropped = original_img.crop((max(0, x - stroke_width), max(0, y - stroke_width), min(current_img.width, x + stroke_width), min(current_img.height, y + stroke_width)))
            new_img.paste(cropped, (max(0, x - stroke_width), max(0, y - stroke_width)))

        # 히스토리에 저장 후 리런
        st.session_state.history.append(new_img)
        st.rerun()
