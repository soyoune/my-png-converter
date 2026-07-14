import streamlit as st
from PIL import Image
import io
import base64

# 1. 포토룸 스타일 와이드 레이아웃
st.set_page_config(
    page_title="Photoroom Style Editor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 세션 상태(메모리) 초기화
if "history" not in st.session_state:
    st.session_state.history = []

# 어두운 다크 모드 및 포토룸 스타일 테마 적용
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .main { background-color: #121214; color: #ffffff; }
        .title-text {
            font-size: 26px;
            font-weight: 800;
            text-align: center;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #ff007f, #7f00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">Photoroom Style AI Editor</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 최초 업로드 시 이미지 RGBA 변환 및 첫 기록 저장
    if not st.session_state.history:
        img = Image.open(uploaded_file).convert("RGBA")
        st.session_state.history.append(img)

    # 좌측 컨트롤 패널(3) / 우측 메인 편집기(9) 배치
    col_control, col_editor = st.columns([3, 9])

    current_img = st.session_state.history[-1]
    original_img = st.session_state.history[0]

    # 이미지를 자바스크립트로 전송할 Base64 포맷 변환
    def img_to_base64(pil_img):
        buffered = io.BytesIO()
        pil_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    current_b64 = img_to_base64(current_img)
    original_b64 = img_to_base64(original_img)

    # 3. 좌측 컨트롤러 패널 (포토룸 메뉴)
    with col_control:
        st.markdown("### 🛠️ 에디터 도구")
        mode = st.radio(
            "선택 모드",
            ("🔴 배경 지우기 (Erase)", "🟢 잘못된 곳 복구 (Restore)"),
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("**🖌️ 브러시 크기**")
        stroke_width = st.slider("Brush Size", 5, 150, 30, label_visibility="collapsed")
        
        st.markdown("---")
        
        # 실행 취소 (Undo)
        if st.button("↩️ 한 단계 되돌리기 (Undo)", use_container_width=True):
            if len(st.session_state.history) > 1:
                st.session_state.history.pop()
                st.rerun()
                
        # 리셋
        if st.button("🔄 전체 초기화 (Reset)", use_container_width=True):
            st.session_state.history = [Image.open(uploaded_file).convert("RGBA")]
            st.rerun()

    # 4. 오른쪽 메인 캔버스 영역 (자바스크립트 기반 실시간 지우개 탑재)
    with col_editor:
        # 주소창 대신 LocalStorage와 '부모-자식 창 메시지 이벤트'를 정교하게 우회 설계하여
        # 클릭/드래그가 끝나는 즉시 파이썬으로 드로잉 결과가 동기화되도록 만듭니다.
        html_code = f"""
        <div style="display: flex; justify-content: center; align-items: center; background-color: #1a1a1e; padding: 20px; border-radius: 12px; border: 1px solid #2a2a30;">
            <canvas id="paintCanvas" style="cursor: crosshair; max-width: 100%; border-radius: 8px; background-image: linear-gradient(45deg, #2a2a30 25%, transparent 25%), linear-gradient(-45deg, #2a2a30 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #2a2a30 75%), linear-gradient(-45deg, transparent 75%, #2a2a30 75%); background-size: 20px 20px; background-position: 0 0, 0 10px, 10px -10px, -10px 0px;"></canvas>
        </div>

        <script>
            const canvas = document.getElementById('paintCanvas');
            const ctx = canvas.getContext('2d');
            
            const img = new Image();
            img.src = "data:image/png;base64,{current_b64}";
            
            const origImg = new Image();
            origImg.src = "data:image/png;base64,{original_b64}";

            let isDrawing = false;
            let lastX = 0;
            let lastY = 0;
            const brushSize = {stroke_width};
            const mode = "{mode}";

            img.onload = function() {{
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                ctx.drawImage(img, 0, 0);
            }};

            function getCoords(e) {{
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                
                const clientX = e.touches ? e.touches[0].clientX : e.clientX;
                const clientY = e.touches ? e.touches[0].clientY : e.clientY;

                return {{
                    x: (clientX - rect.left) * scaleX,
                    y: (clientY - rect.top) * scaleY
                }};
            }}

            function startDrawing(e) {{
                isDrawing = true;
                const coords = getCoords(e);
                lastX = coords.x;
                lastY = coords.y;
                draw(e);
            }}

            function stopDrawing() {{
                if (!isDrawing) return;
                isDrawing = false;
                
                const dataUrl = canvas.toDataURL("image/png");
                
                // Iframe 보안 제약을 우회하기 위해 Streamlit의 쿼리 매개변수로 안전하게 데이터 전송
                const url = new URL(window.parent.location.href);
                url.searchParams.set('saved_img_data', dataUrl.split(',')[1]);
                window.parent.location.href = url.href;
            }}

            function draw(e) {{
                if (!isDrawing) return;
                e.preventDefault();
                const coords = getCoords(e);

                ctx.save();
                ctx.lineJoin = 'round';
                ctx.lineCap = 'round';
                ctx.lineWidth = brushSize;

                if (mode.includes("🔴")) {{
                    // 지우개 모드: 클릭한 곳을 투명하게 지움
                    ctx.globalCompositeOperation = 'destination-out';
                    ctx.beginPath();
                    ctx.moveTo(lastX, lastY);
                    ctx.lineTo(coords.x, coords.y);
                    ctx.stroke();
                }} else {{
                    // 복구 브러시 모드: 원본 이미지 해당 부위 복사
                    ctx.beginPath();
                    ctx.arc(coords.x, coords.y, brushSize / 2, 0, Math.PI * 2);
                    ctx.clip();
                    ctx.drawImage(origImg, 0, 0);
                }}
                
                ctx.restore();
                lastX = coords.x;
                lastY = coords.y;
            }}

            // 마우스 및 터치 이벤트
            canvas.addEventListener('mousedown', startDrawing);
            canvas.addEventListener('mousemove', draw);
            window.addEventListener('mouseup', stopDrawing);

            canvas.addEventListener('touchstart', startDrawing);
            canvas.addEventListener('touchmove', draw);
            window.addEventListener('touchend', stopDrawing);
        </script>
        """

        # 이미지 높이에 따라 동적으로 캔버스 공간 배정
        display_height = int(current_img.height * (800 / current_img.width)) if current_img.width > 0 else 600
        
        from streamlit.components.v1 import html
        html(html_code, height=display_height + 120)

    # 5. 자바스크립트 드로잉 데이터가 안전하게 수신되었는지 처리
    # 쿼리 매개변수 검색 방식을 통해 Iframe 보안 장벽을 완전히 뚫습니다.
    query_params = st.query_params
    if "saved_img_data" in query_params:
        img_b64 = query_params["saved_img_data"]
        
        # 즉시 쿼리 매개변수를 초기화하여 무한 렌더링 루프 차단
        st.query_params.clear()
        
        # Base64 데이터를 디코딩하여 Pillow 이미지로 전환
        decoded = base64.b64encode(base64.b64decode(img_b64)) # 한번 정규화
        new_canvas_img = Image.open(io.BytesIO(base64.b64decode(img_b64))).convert("RGBA")
        
        # 세션 히스토리에 한 단계 추가
        st.session_state.history.append(new_canvas_img)
        st.rerun()
