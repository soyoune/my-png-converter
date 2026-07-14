import streamlit as st
from PIL import Image
import io
import base64

# 1. 포토룸 스타일 와이드 화면 및 사이드바 기본 숨김 설정
st.set_page_config(
    page_title="Photoroom Style Editor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 세션 상태(메모리) 리셋 및 초기화
if "history" not in st.session_state:
    st.session_state.history = []

# 어두운 다크 모드 및 포토룸 스타일 UI 스타일링
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
        /* 버튼 스타일 통일 */
        .stButton>button {
            background-color: #2a2a30 !important;
            color: #ffffff !important;
            border: 1px solid #3e3e46 !important;
            border-radius: 8px !important;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #ff007f !important;
            border-color: #ff007f !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">Photoroom Style AI Editor</div>', unsafe_allow_html=True)

# 파일 업로더
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 최초 업로드 시 이미지 변환 및 첫 기록 저장
    if not st.session_state.history:
        img = Image.open(uploaded_file).convert("RGBA")
        st.session_state.history.append(img)

    # 포토룸 스타일 3:9 레이아웃 배치
    col_control, col_editor = st.columns([3, 9])

    current_img = st.session_state.history[-1]
    original_img = st.session_state.history[0]

    # Pillow 이미지를 자바스크립트로 전송할 Base64 포맷으로 전환
    def img_to_base64(pil_img):
        buffered = io.BytesIO()
        pil_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    current_b64 = img_to_base64(current_img)
    original_b64 = img_to_base64(original_img)

    # 3. 왼쪽 컨트롤러 패널 (포토룸 메뉴)
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
        
        # 실행 취소 (Undo) 버튼
        if st.button("↩️ 한 단계 되돌리기 (Undo)", use_container_width=True):
            if len(st.session_state.history) > 1:
                st.session_state.history.pop()
                st.rerun()
                
        # 리셋 버튼
        if st.button("🔄 전체 초기화 (Reset)", use_container_width=True):
            st.session_state.history = [Image.open(uploaded_file).convert("RGBA")]
            st.rerun()

    # 4. 오른쪽 메인 캔버스 영역 (자바스크립트 엔진 탑재)
    with col_editor:
        # 이 HTML/JS 샌드박스가 포토룸처럼 실시간 드래그 편집과 통신을 완전하게 책임집니다.
        html_code = f"""
        <div style="display: flex; justify-content: center; align-items: center; background-color: #1a1a1e; padding: 20px; border-radius: 12px; border: 1px solid #2a2a30; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
            <canvas id="paintCanvas" style="cursor: crosshair; max-width: 100%; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); background-image: linear-gradient(45deg, #2a2a30 25%, transparent 25%), linear-gradient(-45deg, #2a2a30 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #2a2a30 75%), linear-gradient(-45deg, transparent 75%, #2a2a30 75%); background-size: 20px 20px; background-position: 0 0, 0 10px, 10px -10px, -10px 0px;"></canvas>
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
                
                // 마우스를 뗄 때 그려진 최종 캔버스 이미지를 캡처
                const dataUrl = canvas.toDataURL("image/png");
                
                // 💡 핵심: Streamlit의 쿼리 파라미터를 사용하여 즉각적으로 파이썬 세션에 업로드
                const url = new URL(window.parent.location.href);
                url.searchParams.set('saved_img_data', dataUrl.split(',')[1]);
                window.parent.location.href = url.href;
            }}

            function draw(e) {{
                if (!isDrawing) return;
                e.preventDefault();
                const coords = getCoords(e);

                ctx.save();
                
                // 브러시 마감이 부드러운 둥근 형태로 이어지도록 보정
                ctx.lineJoin = 'round';
                ctx.lineCap = 'round';
                ctx.lineWidth = brushSize;

                if (mode.includes("🔴")) {{
                    // 배경 투명하게 지우기 (Destination-Out)
                    ctx.globalCompositeOperation = 'destination-out';
                    ctx.beginPath();
                    ctx.moveTo(lastX, lastY);
                    ctx.lineTo(coords.x, coords.y);
                    ctx.stroke();
                }} else {{
                    // 브러시 경로대로 원본 픽셀 복구하기 (Clip 활용)
                    ctx.beginPath();
                    ctx.arc(coords.x, coords.y, brushSize / 2, 0, Math.PI * 2);
                    ctx.clip();
                    ctx.drawImage(origImg, 0, 0);
                }}
                
                ctx.restore();
                lastX = coords.x;
                lastY = coords.y;
            }}

            // 마우스/모바일 터치 드래그 바인딩 완료
            canvas.addEventListener('mousedown', startDrawing);
            canvas.addEventListener('mousemove', draw);
            window.addEventListener('mouseup', stopDrawing);

            canvas.addEventListener('touchstart', startDrawing);
            canvas.addEventListener('touchmove', draw);
            window.addEventListener('touchend', stopDrawing);
        </script>
        """

        # 최적의 캔버스 세로 높이 설정
        display_height = int(current_img.height * (800 / current_img.width)) if current_img.width > 0 else 600
        
        from streamlit.components.v1 import html
        html(html_code, height=display_height + 120)

    # 5. 자바스크립트 드로잉 데이터를 수신해 파이썬 세션 히스토리에 병합
    query_params = st.query_params
    if "saved_img_data" in query_params:
        img_b64 = query_params["saved_img_data"]
        
        # 즉시 쿼리 매개변수를 지워 무한 재실행 버그 방지
        st.query_params.clear()
        
        # Base64 디코딩 후 PIL 이미지로 전환하여 저장
        decoded = base64.b64decode(img_b64)
        new_canvas_img = Image.open(io.BytesIO(decoded)).convert("RGBA")
        
        # 새 작업 단계를 히스토리에 기록
        st.session_state.history.append(new_canvas_img)
        st.rerun()
