import streamlit as st
from PIL import Image
from rembg import remove
import io

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="AI Background Remover (Photoroom Style)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# UI 스타일 커스텀 (포토룸 스타일 다크 테마)
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
        /* 다운로드 버튼 스타일 */
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
st.markdown('<div class="subtitle-text">외부 서버 연결 없이 자체적으로 구동되는 무제한 무료 누끼 제거기입니다.</div>', unsafe_allow_html=True)

# 파일 업로더
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 안전하게 이미지 로드 및 RGBA 변환
    input_image = Image.open(uploaded_file).convert("RGBA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📷 원본 이미지")
        st.image(input_image, use_container_width=True)
        
    with col2:
        st.markdown("### ✨ 배경 제거 완료")
        
        # 자체 라이브러리로 안전하게 연산 실행
        with st.spinner("AI가 배경을 분석하여 정밀하게 지우는 중..."):
            try:
                output_image = remove(input_image)
                st.image(output_image, use_container_width=True)
                
                # 다운로드 버튼 생성
                buf = io.BytesIO()
                output_image.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    label="📥 배경 없는 투명 PNG 다운로드",
                    data=byte_im,
                    file_name=f"photoroom_{uploaded_file.name.split('.')[0]}.png",
                    mime="image/png",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"이미지 처리 중 오류가 발생했습니다: {str(e)}")
