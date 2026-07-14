import streamlit as st
from PIL import Image
import io

# 1. 포토룸 스타일의 고급 다크 테마 설정
st.set_page_config(
    page_title="AI Photoroom Background Remover",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# UI 커스텀 스타일링
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
            margin-top: 20px;
            margin-bottom: 5px;
            background: linear-gradient(45deg, #ff007f, #7f00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle-text {
            text-align: center;
            color: #8a8a93;
            margin-bottom: 30px;
        }
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
st.markdown('<div class="subtitle-text">형태 인지 딥러닝 모델로 캐릭터의 내부 흰색은 지키고 배경만 말끔히 제거합니다.</div>', unsafe_allow_html=True)

# 2. 파일 업로더 생성
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 안전하게 이미지 로드 및 RGBA 포맷 변환
    input_image = Image.open(uploaded_file).convert("RGBA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📷 원본 이미지")
        st.image(input_image, use_container_width=True)
        
    with col2:
        st.markdown("### ✨ 포토룸 결과물")
        
        # 내부 AI 연산 시작
        with st.spinner("AI 엔진이 캐릭터 실루엣을 분석하는 중... (첫 실행 시 1~2분 소요될 수 있습니다)"):
            try:
                # 💡 rembg 코어를 켜고 2D 일러스트/캐릭터 누끼 전용 고화질 세션을 생성합니다.
                from rembg import remove, new_session
                
                # 'isnet-general-use' 세션은 사물의 전체적인 레이아웃(실루엣)을 최우선으로 인식합니다.
                # 따라서 얼굴 안의 흰색은 지우지 않고 바깥 테두리 밖의 흰색만 칼같이 도려냅니다.
                session = new_session("isnet-general-use")
                output_image = remove(input_image, session=session)
                
                # 이미지 화면 출력
                st.image(output_image, use_container_width=True)
                
                # 다운로드 가능한 파일 바이트 변환
                buf = io.BytesIO()
                output_image.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    label="📥 배경 없는 고화질 PNG 다운로드",
                    data=byte_im,
                    file_name=f"photoroom_{uploaded_file.name.split('.')[0]}.png",
                    mime="image/png",
                    use_container_width=True
                )
            except Exception as e:
                # 혹시 모를 에러 발생 시 상세 메시지 출력
                st.error(f"처리 중 예기치 못한 에러가 발생했습니다: {str(e)}")
                st.info("Streamlit Cloud 서버가 AI 구동에 필요한 내부 가상화 모듈을 다시 잡는 중일 수 있습니다. 잠시만 기다린 후 새로고침해 주세요.")
