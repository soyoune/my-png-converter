import streamlit as st
from PIL import Image
from rembg import remove
import io

# 1. 포토룸 스타일의 다크 테마 레이아웃 설정
st.set_page_config(
    page_title="AI Background Remover (Photoroom Style)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# UI 스타일 커스텀 디자인
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
            margin-top: 10px;
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
        /* 다운로드 버튼 포토룸 핑크색 강조 */
        .stDownloadButton>button {
            background: linear-gradient(45deg, #ff007f, #7f00ff) !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            transition: transform 0.2s ease;
        }
        .stDownloadButton>button:hover {
            transform: scale(1.02);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">AI Photoroom Remover</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">이미지를 업로드하면 클릭할 필요도 없이 배경을 자동으로 완벽하게 제거합니다.</div>', unsafe_allow_html=True)

# 파일 업로더 생성
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 원본 이미지 로드
    input_image = Image.open(uploaded_file).convert("RGBA")
    
    # 2. 좌우 분할 레이아웃 배치
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📷 원본 이미지")
        st.image(input_image, use_container_width=True)
        
    with col2:
        st.markdown("### ✨ 배경 제거 완료")
        
        # AI 연산 (rembg를 이용한 실시간 누끼 따기)
        with st.spinner("AI가 스마트하게 배경을 지우는 중..."):
            # rembg 라이브러리를 호출하여 깔끔하게 아웃라인을 땁니다.
            output_image = remove(input_image)
            
        # 결과를 투명 바둑판 배경 느낌의 Streamlit 이미지 뷰어로 렌더링
        st.image(output_image, use_container_width=True)
        
        # 다운로드를 위한 바이트 변환
        buf = io.BytesIO()
        output_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        # 3. 다운로드 버튼 제공
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="📥 배경 없는 이미지 저장하기 (.png)",
            data=byte_im,
            file_name=f"photoroom_style_{uploaded_file.name.split('.')[0]}.png",
            mime="image/png",
            use_container_width=True
        )
