import streamlit as st
from PIL import Image
import io
import base64

# 1. 포토룸 스타일의 와이드 레이아웃 설정
st.set_page_config(
    page_title="Photoroom Style Editor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 세션 상태 초기화 (작업 히스토리 저장용)
if "history" not in st.session_state:
    st.session_state.history = []

# CSS를 이용해 Streamlit 기본 요소를 숨기고 포토룸 테마(어두운 모드 스타일) 적용
st.markdown("""
    <style>
        /* Streamlit 기본 헤더/푸터 숨기기 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 전체 배경 및 폰트 스타일링 */
        .main {
            background-color: #121214;
            color: #ffffff;
        }
        
        /* 제목 스타일 */
        .title-text {
            font-size: 28px;
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

# 2. 이미지 업로드
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 최초 이미지 로드 및 RGBA 변환
    if not st.session_state.history:
        img = Image.open(uploaded_file).convert("RGBA")
        st.session_state.history.append(img)

    # 화면을 좌측 컨트롤 패널(3) / 우측 메인 편집기(9) 레이아웃으로 분할
    col_control, col_editor = st.columns([3, 9])

    current_img = st.session_state.history[-1]
    original_img = st.session_state.history[0]

    # 이미지를 웹 화면에 전송하기 위한 Base64 변환 함수
    def img_to_base64(pil_img):
        buffered = io.BytesIO()
        pil_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    current_b64 = img_to_base64(current_img)
    original_b64 = img_to_base64(original_img)

    # 3. 좌측 컨트롤 패널 (포토룸 스타일 도구함)
    with col_control:
        st.markdown("### 🛠️ 에디터 도구")
        
        mode = st.radio(
            "선택 모드",
            ("🔴 배경 지우기 (Erase)", "🟢 잘못된 곳 복구 (Restore)"),
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("**🖌️ 브러시 크기**")
        stroke_width = st.slider("Brush Size", 5, 100, 20, label_visibility="collapsed")
        
        st.markdown("---")
        
        # 되돌리기 & 초기화 버튼
        if st.button("↩️ 실행 취소 (Undo)", use_container_width=True):
            if len(st.session_state.history) > 1:
                st.session_state.history.pop()
                st.rerun()
                
        if st.button("🔄 작업 초기화 (Reset)", use_container_width=True):
            st.session_state.history = [Image.open(uploaded_file).convert("RGBA")]
            st.rerun()

    # 4. 우측 메인 편집기 (HTML5 Canvas + 부드러운 드래그 JS 탑재)
    with col_editor:
        html_code = f"""
        <div style="display: flex; justify-content: center; align-items: center; background-color: #1a1a1e; padding: 20px; border-radius: 12px; border: 1px solid #2a2a30; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
            <canvas id="paintCanvas" style="cursor: crosshair; max-width: 100%; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);"></canvas>
        </div>

        <script>
            const canvas = document.getElementById('paintCanvas');
            const ctx = canvas.getContext('2d');
            
            const img = new Image();
            img.src = "data:image/png;base64,{current_b64}";
            
            const origImg = new Image();
            origImg.src = "data:image/png;base64,{original_b64}";

            let isDrawing = false;
            const brushSize = {stroke_width};
            const mode = "{mode}";

            img.onload = function() {{
                // 원본 해상도와 화면 표시 크기 비례 조절
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
                draw(e);
            }}

            function stopDrawing() {{
                if (!isDrawing) return;
                isDrawing = false;
                
                // 마우스를 떼는 순간 최종 드로잉 데이터 세션에 즉시 저장
                const dataUrl = canvas.toDataURL("image/png");
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

                if (mode.includes("🔴")) {{
                    // 브러시 경로 투명화 (지우기)
                    ctx.clearRect(coords.x - brushSize, coords.y - brushSize, brushSize * 2, brushSize * 2);
                }} else {{
                    // 원본 이미지 복구
                    ctx.drawImage(origImg, 0, 0);
                }}
                ctx.restore();
            }}

            // 마우스 & 터치 이벤트 바인딩
            canvas.addEventListener('mousedown', startDrawing);
            canvas.addEventListener('mousemove', draw);
            window.addEventListener('mouseup', stopDrawing);

            canvas.addEventListener('touchstart', startDrawing);
            canvas.addEventListener('touchmove', draw);
            window.addEventListener('touchend', stopDrawing);
        </script>
        """

        # 컴포넌트 높이를 이미지 해상도 비율에 맞추어 유연하게 계산
        display_height = int(current_img.height * (800 / current_img.width)) if current_img.width > 0 else 600
        
        from streamlit.components.v1 import html
        # 자바스크립트 캔버스를 화면에 주입
        html(html_code, height=display_height + 100)
