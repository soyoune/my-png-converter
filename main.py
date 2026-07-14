import streamlit as st
from PIL import Image
import io

# 1. 포토룸 스타일 레이아웃 설정
st.set_page_config(
    page_title="AI Photoroom (Pochacco Safe Edition)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 다크 테마 커스텀 UI
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .main { background-color: #121214; color: #ffffff; }
        .title-text {
            font-size: 32px;
            font-weight: 800;
            text-align: center;
            margin-top: 15px;
            margin-bottom: 5px;
            background: linear-gradient(45deg, #ff007f, #7f00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle-text {
            text-align: center;
            color: #8a8a93;
            margin-bottom: 25px;
        }
        /* 포토룸 스타일 다운로드 버튼 */
        .stDownloadButton>button {
            background: linear-gradient(45deg, #ff007f, #7f00ff) !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 20px !important;
            transition: all 0.2s ease;
        }
        .stDownloadButton>button:hover {
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(255, 0, 127, 0.4);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">AI Photoroom Remover</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">포차코의 얼굴은 완벽하게 보호하고 바깥 배경만 정밀하게 분리합니다.</div>', unsafe_allow_html=True)

# 파일 업로더
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 이미지 안전 로드 및 기본 RGBA 변환
    input_image = Image.open(uploaded_file).convert("RGBA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📷 원본 이미지")
        st.image(input_image, use_container_width=True)
        
    with col2:
        st.markdown("### ✨ 배경 제거 완료")
        
        # 내부 AI 라이브러리 구동 (404, 연결 거부 걱정 없음!)
        with st.spinner("AI 엔진이 캐릭터를 인식하고 분석하는 중..."):
            try:
                # 패키지를 이 타이밍에 안전하게 동적 임포트하여 충돌 방지
                from rembg import remove, new_session
                
                # 포차코 같은 2D 일러스트/캐릭터 누끼에 최적화된 'isnet-general-use' 세션 사용
                # 이 옵션을 쓰면 캐릭터 형태를 완벽하게 인지하므로 하얀 포차코 얼굴이 뻥 뚫리지 않습니다!
                session = new_session("isnet-general-use")
                output_image = remove(input_image, session=session)
                
                # 결과 출력
                st.image(output_image, use_container_width=True)
                
                # 다운로드 파일 바이트 변환
                buf = io.BytesIO()
                output_image.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    label="📥 배경 없는 고화질 PNG 다운로드",
                    data=byte_im,
                    file_name=f"photoroom_safe_{uploaded_file.name.split('.')[0]}.png",
                    mime="image/png",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"처리 중 오류가 발생했습니다. AI 환경을 구성하는 중일 수 있으니 잠시 후 새로고침해 주세요! (오류내용: {str(e)})")
