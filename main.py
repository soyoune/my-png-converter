import streamlit as st
from PIL import Image
import requests
import io

# 1. 포토룸 스타일의 고급 다크 테마 설정
st.set_page_config(
    page_title="AI Photoroom - Pochacco Safe Edition",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# UI 커스텀 스타일링 (포토룸 스타일 테마)
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
st.markdown('<div class="subtitle-text">Cloudflare AI 엔진을 거쳐 포차코 얼굴은 지키고 바깥 배경만 1초 만에 분리합니다.</div>', unsafe_allow_html=True)

# ⚠️ [필수 작성] 발급받으신 클라우드플레어 정보를 아래에 넣어주세요!
CLOUDFLARE_ACCOUNT_ID = "YOUR_CLOUDFLARE_ACCOUNT_ID"
CLOUDFLARE_API_TOKEN = "YOUR_CLOUDFLARE_API_TOKEN"

# 파일 업로더 생성
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
        
        # API 전송을 위한 바이너리(Bytes) 변환
        img_byte_arr = io.BytesIO()
        input_image.save(img_byte_arr, format='PNG')
        img_byte_data = img_byte_arr.getvalue()
        
        # API 설정 확인 안내 메시지
        if CLOUDFLARE_API_TOKEN == "YOUR_CLOUDFLARE_API_TOKEN":
            st.warning("⚠️ 코드 내부의 `CLOUDFLARE_ACCOUNT_ID`와 `CLOUDFLARE_API_TOKEN` 값을 입력해야 AI 기능이 활성화됩니다.")
        else:
            # 대기업 서버의 고성능 연산을 활용하므로 로딩 렉이 완전히 사라집니다!
            with st.spinner("AI가 배경을 분석하여 실시간 제거하는 중... ⚡"):
                try:
                    # 포토룸과 동일한 RMBG-1.4 고정밀 세그멘테이션 모델 호출
                    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/briaai/rmbg-1.4"
                    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
                    
                    response = requests.post(url, headers=headers, data=img_byte_data)
                    
                    if response.status_code == 200:
                        output_image = Image.open(io.BytesIO(response.content))
                        st.image(output_image, use_container_width=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.download_button(
                            label="📥 배경 없는 고화질 PNG 다운로드",
                            data=response.content,
                            file_name=f"photoroom_fast_{uploaded_file.name.split('.')[0]}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    else:
                        st.error(f"AI 서버 응답 실패 (에러 코드: {response.status_code})")
                        st.info("Cloudflare API 토큰 및 계정 ID가 정확하게 입력되었는지 다시 확인해 주세요.")
                except Exception as e:
                    st.error(f"처리 중 오류가 발생했습니다: {str(e)}")
