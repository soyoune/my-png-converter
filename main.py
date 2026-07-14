import streamlit as st
from PIL import Image
import io
import base64

st.set_page_config(
    page_title="Photoroom Style Editor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 1. 세션 상태(메모리) 초기화
if "history" not in st.session_state:
    st.session_state.history = []

# CSS로 포토룸 특유의 어두운 다크모드 테마 적용
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

# 이미지 업로드
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 최초 이미지 로드 시 RGBA(투명 채널) 변환 및 히스토리 등록
    if not st.session_state.history:
        img = Image.open(uploaded_file).convert("RGBA")
        st.session_state.history.append(img)

    # 레이아웃 분할 (좌측 컨트롤 패널 / 우측 편집기)
    col_control, col_editor = st.columns([3, 9])

    current_img = st.session_state.history[-1]
    original_img = st.session_state.history[0]

    # 이미지를 웹 브라우저가 인식할 수 있게 Base64 인코딩
    def img_to_base64(pil_img):
        buffered = io.BytesIO()
        pil_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    current_b64 = img_to_base64(current_img)
    original_b64 = img_to_base64(original_img)

    # 2. 좌측 포토룸 제어 패널
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
        
        # 되돌리기(Undo) 버튼
        if st.button("↩️ 실행 취소 (Undo)", use_container_width=True):
            if len(st.session_state.history) > 1:
                st.session_state.history.pop()
                st.rerun()
                
        # 리셋 버튼
        if st.button("🔄 작업 초기화 (Reset)", use_container_width=True):
            st.session_state.history = [Image.open(uploaded_file).convert("RGBA")]
            st.rerun()

    # 3. 우측 메인 편집 캔버스 (실시간 드래그 수신 기능 탑재)
    with col_editor:
        # 이 부분이 프론트엔드(JS)와 백엔드(Python)를 매끄럽게 이어주는 자바스크립트 브러시 핵심 엔진입니다.
        html_code = f"""
        <div style="display: flex; justify-content: center; align-items: center; background-color: #1a1a1e; padding: 20px; border-radius: 12px; border: 1px solid #2a2a30;">
            <canvas id="paintCanvas" style="cursor: crosshair; max-width: 100%; border-radius: 8px; background-image: linear-gradient(45deg, #ccc 25%, transparent 25%), linear-gradient(-45deg, #ccc 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #ccc 75%), linear-gradient(-45deg, transparent 75%, #ccc 75%); background-size: 20px 20px; background-position: 0 0, 0 10px, 10px -10px, -10px 0px;"></canvas>
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
                
                // 마우스를 떼는 순간, 수정된 캔버스 이미지를 base64 텍스트로 Streamlit 서버에 전송
                const dataUrl = canvas.toDataURL("image/png");
                
                // Streamlit의 주소창 쿼리 매개변수를 이용해 파이썬 백엔드로 데이터 전달
                const url = new URL(window.parent.location.href);
                url.searchParams.set('canvas_data_trigger', Date.now());
                window.parent.location.href = url.href;
                
                // 세션 스토리지에 최종 이미지 임시 보관
                window.parent.sessionStorage.setItem("edited_image", dataUrl);
            }}

            function draw(e) {{
                if (!isDrawing) return;
                e.preventDefault();
                const coords = getCoords(e);

                ctx.save();
                
                // 선이 끊기지 않고 부드럽게 이어지도록 처리 (Line Drawing 기법)
                ctx.lineJoin = 'round';
                ctx.lineCap = 'round';
                ctx.lineWidth = brushSize;

                if (mode.includes("🔴")) {{
                    // 지우개: 투명하게 깎아내기
                    ctx.globalCompositeOperation = 'destination-out';
                    ctx.beginPath();
                    ctx.moveTo(lastX, lastY);
                    ctx.lineTo(coords.x, coords.y);
                    ctx.stroke();
                }} else {{
                    // 복구 브러시: 원본 이미지 복구 마스킹
                    ctx.beginPath();
                    ctx.arc(coords.x, coords.y, brushSize / 2, 0, Math.PI * 2);
                    ctx.clip();
                    ctx.drawImage(origImg, 0, 0);
                }}
                
                ctx.restore();
                lastX = coords.x;
                lastY = coords.y;
            }}

            // 마우스 및 터치 이벤트 핸들러
            canvas.addEventListener('mousedown', startDrawing);
            canvas.addEventListener('mousemove', draw);
            window.addEventListener('mouseup', stopDrawing);

            canvas.addEventListener('touchstart', startDrawing);
            canvas.addEventListener('touchmove', draw);
            window.addEventListener('touchend', stopDrawing);
        </script>
        """

        # 이미지 높이에 알맞게 컨테이너 크기 확보
        display_height = int(current_img.height * (800 / current_img.width)) if current_img.width > 0 else 600
        
        # HTML 샌드박스 주입
        from streamlit.components.v1 import html
        html(html_code, height=display_height + 120)

    # 4. 자바스크립트가 브러시 질을 마치고 전송한 이미지 수신 로직
    # 세션 스토리지에서 변환된 이미지 데이터를 가져오기 위해 브라우저 우회 쿼리 파라미터를 확인합니다.
    query_params = st.query_params
    if "canvas_data_trigger" in query_params:
        # 무한 리런을 방지하기 위해 쿼리 매개변수 즉시 초기화
        st.query_params.clear()
        
        # 💡 자바스크립트가 저장한 sessionStorage 데이터를 가져오기 위한 스크립트 실행
        # 로컬 세션의 수신 처리를 위해 약간의 세션 트릭 사용
        js_get_code = """
        <script>
            const imgData = window.parent.sessionStorage.getItem("edited_image");
            if (imgData) {
                const url = new URL(window.parent.location.href);
                url.searchParams.set('image_base64', imgData.split(',')[1]);
                window.parent.location.href = url.href;
            }
        </script>
        """
        html(js_get_code, height=0)

    # 최종 변환된 base64 이미지가 쿼리에 포착되면 Pillow 이미지로 변환하여 히스토리에 추가합니다.
    if "image_base64" in query_params:
        img_data = query_params["image_base64"]
        st.query_params.clear() # 중복 처리 방지
        
        # Base64 데이터를 PIL 이미지로 전환
        decoded = base64.b64decode(img_data)
        edited_image = Image.open(io.BytesIO(decoded)).convert("RGBA")
        
        # 히스토리에 추가하고 페이지 새로고침
        st.session_state.history.append(edited_image)
        st.rerun()
