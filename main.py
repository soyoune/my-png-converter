import streamlit as st
from PIL import Image
import io

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="AI Photoroom Style Editor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 세션 상태 및 히스토리 초기화
if "history" not in st.session_state:
    st.session_state.history = []

# 다크 테마 및 깔끔한 포토룸 스타일 UI 적용
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .main { background-color: #121214; color: #ffffff; }
        .title-text {
            font-size: 28px;
            font-weight: 800;
            text-align: center;
            margin-top: 10px;
            margin-bottom: 5px;
            background: linear-gradient(45deg, #ff007f, #7f00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle-text {
            text-align: center;
            color: #8a8a93;
            margin-bottom: 25px;
            font-size: 14px;
        }
        /* 포토룸 스타일 분홍색 강조 다운로드 버튼 */
        .stDownloadButton>button {
            background: linear-gradient(45deg, #ff007f, #7f00ff) !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 20px !important;
            font-size: 16px !important;
            transition: all 0.3s ease;
        }
        .stDownloadButton>button:hover {
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(255, 0, 127, 0.4);
        }
        /* 에디터 카드 스타일 */
        .editor-card {
            background-color: #1a1a1e;
            border: 1px solid #2a2a30;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">AI Photoroom Background Remover</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">복잡한 수동 지우개 없이, 클릭 단 한 번으로 투명한 누끼 이미지를 완성합니다.</div>', unsafe_allow_html=True)

# 파일 업로더
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 안전하게 Pillow 이미지 열기
    input_image = Image.open(uploaded_file).convert("RGBA")
    
    # 2. 메인 화면 분할 레이아웃
    col_orig, col_res = st.columns(2)
    
    with col_orig:
        st.markdown("<div class='editor-card'><h3>📷 원본 이미지</h3></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.image(input_image, use_container_width=True)
        
    with col_res:
        st.markdown("<div class='editor-card'><h3>✨ 배경 제거 완료</h3></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 'rembg'가 완전히 임포트되는지 예외 처리(Error-safe) 장치 추가
        try:
            from rembg import remove
            with st.spinner("AI가 배경을 분석하여 정밀하게 지우는 중..."):
                output_image = remove(input_image)
            
            # 투명(바둑판) 배경을 표현하기 위해 결과를 이미지로 띄움
            st.image(output_image, use_container_width=True)
            
            # 다운로드 파일 바이트 변환
            buf = io.BytesIO()
            output_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="📥 배경이 제거된 고화질 PNG 다운로드",
                data=byte_im,
                file_name=f"photoroom_{uploaded_file.name.split('.')[0]}.png",
                mime="image/png",
                use_container_width=True
            )
        except ModuleNotFoundError:
            # rembg 패키지가 아직 배포/빌드 중일 때를 대비한 안전 모드 알림
            st.error("💡 AI 패키지(rembg)가 현재 서버에 설치 중입니다! 잠시 후 새로고침(F5)을 해주세요.")
            st.info("requirements.txt 파일에 streamlit, rembg, Pillow가 정상적으로 기입되어 있는지 확인해 주세요.")
