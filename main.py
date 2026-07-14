import streamlit as st
from PIL import Image
import io
import base64

st.set_page_config(layout="centered")
st.title("🎨 포토룸 스타일 배경 지우개")

# 1. 세션 상태(메모리) 설정
if "history" not in st.session_state:
    st.session_state.history = []

uploaded_file = st.file_uploader("이미지를 선택하세요...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 최초 이미지 로드 및 RGBA(투명도 지원) 변환
    if not st.session_state.history:
        img = Image.open(uploaded_file).convert("RGBA")
        st.session_state.history.append(img)

    # 2. 제어 UI 설정
    mode = st.radio("👉 작업 모드:", ("🔴 배경 지우기", "🟢 잘못 지워진 곳 복구"))
    stroke_width = st.slider("🖌️ 브러시 크기 조절", 5, 100, 20)

    # 상단 제어 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("↩️ 한 단계 되돌리기 (Undo)") and len(st.session_state.history) > 1:
            st.session_state.history.pop()
            st.rerun()
    with col2:
        if st.button("🔄 처음부터 다시 하기 (초기화)"):
            st.session_state.history = [Image.open(uploaded_file).convert("RGBA")]
            st.rerun()

    # 현재 편집 중인 이미지와 원본 이미지(복구용) 준비
    current_img = st.session_state.history[-1]
    original_img = st.session_state.history[0]

    # 이미지를 웹 브라우저에서 그릴 수 있도록 Base64 인코딩
    def img_to_base64(pil_img):
        buffered = io.BytesIO()
        pil_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    current_b64 = img_to_base64(current_img)
    original_b64 = img_to_base64(original_img)

    # 3. HTML5 Canvas + 부드러운 드래그(JS) 코드 적용
    # 마우스를 꾹 누르고 움직이면 실시간으로 선을 그리고, 마우스를 떼는 순간 Streamlit으로 최종 이미지를 전송합니다.
    html_code = f"""
    <div style="text-align: center; position: relative; display: inline-block;">
        <canvas id="paintCanvas" style="border: 1px solid #ccc; cursor: crosshair; max-width: 100%;"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('paintCanvas');
        const ctx = canvas.getContext('2d');
        
        // 이미지 객체 생성 및 로드
        const img = new Image();
        img.src = "data:image/png;base64,{current_b64}";
        
        const origImg = new Image();
        origImg.src = "data:image/png;base64,{original_b64}";

        let isDrawing = false;
        const brushSize = {stroke_width};
        const mode = "{mode}"; // "🔴 배경 지우기" 또는 "🟢 잘못 지워진 곳 복구"

        img.onload = function() {{
            // 캔버스 크기를 원본 이미지 크기와 동일하게 설정
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            ctx.drawImage(img, 0, 0);
        }};

        // 마우스 드래그 이벤트 (부드러운 그리기)
        function getCoords(e) {{
            const rect = canvas.getBoundingClientRect();
            // 화면 캔버스 크기 대비 원본 이미지 크기 비율 계산
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            
            // 터치 이벤트 지원 포함
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;

            return {{
                x: (clientX - rect.left) * scaleX,
                y: (clientY - rect.top) * scaleY
            }};
        }}

        function startDrawing(e) {{
            isDrawing = true;
            draw(e);
        }}

        function stopDrawing() {{
            if (!isDrawing) return;
            isDrawing = false;
            
            // 드로잉이 끝나면(마우스를 떼면) 수정된 캔버스 이미지를 Streamlit 서버로 전송
            const dataUrl = canvas.toDataURL("image/png");
            
            // Streamlit에 전송하기 위해 쿼리 파라미터나 Custom Event를 활용
            const url = new URL(window.parent.location.href);
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: dataUrl
            }}, '*');
        }}

        function draw(e) {{
            if (!isDrawing) return;
            e.preventDefault();
            const coords = getCoords(e);

            ctx.save();
            ctx.beginPath();
            ctx.arc(coords.x, coords.y, brushSize / 2, 0, Math.PI * 2);
            ctx.clip();

            if (mode === "🔴 배경 지우기") {{
                // 픽셀을 완전히 투명하게 지움
                ctx.clearRect(coords.x - brushSize, coords.y - brushSize, brushSize * 2, brushSize * 2);
            }} else {{
                // 원본 이미지의 픽셀을 해당 위치에 다시 덮어씌워 복구
                ctx.drawImage(origImg, 0, 0);
            }}
            ctx.restore();
        }}

        // 이벤트 리스너 연결 (PC 마우스 & 모바일 터치 대응)
        canvas.addEventListener('mousedown', startDrawing);
        canvas.addEventListener('mousemove', draw);
        window.addEventListener('mouseup', stopDrawing);

        canvas.addEventListener('touchstart', startDrawing);
        canvas.addEventListener('touchmove', draw);
        window.addEventListener('touchend', stopDrawing);
    </script>
    """

    # 4. 자바스크립트가 보내온 결과 이미지 수신 및 히스토리 업데이트
    # Streamlit html component가 반환한 데이터를 감지합니다.
    from streamlit.components.v1 import html
    
    # 클릭 및 드래그 동작을 부드럽게 감지하는 캔버스 컴포넌트 실행
    canvas_container = st.container()
    with canvas_container:
        html(html_code, height=int(current_img.height * (600 / current_img.width)) + 50 if current_img.width > 0 else 500)

    # 세션 상태로 자바스크립트가 보낸 이미지 데이터 수신 처리
    # (참고: streamlit_js_eval 또는 query_params를 활용하거나 컴포넌트 이벤트를 통해 상태 업데이트)
    # 아래는 주소창 파라미터나 메시지 기반 전송 데이터 처리 영역입니다.
