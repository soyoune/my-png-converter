import streamlit as st
from PIL import Image
import requests
import io

# 1. 포토룸 스타일 레이아웃 설정
st.set_page_config(
    page_title="AI Background Remover (Photoroom Style)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# UI 디자인 커스텀 (포토룸 스타일 다크 테마)
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
        /* 포토룸 스타일 핑크/퍼플 그라데이션 다운로드 버튼 */
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
st.markdown('<div class="subtitle-text">하루 제한 없이 무제한으로 배경을 말끔하게 제거합니다.</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 업로드 이미지 읽기
    input_image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📷 원본 이미지")
        st.image(input_image, use_container_width=True)
        
    with col2:
        st.markdown("### ✨ 배경 제거 완료")
        
        # API 전송을 위한 바이너리(Bytes) 변환
        img_byte_arr = io.BytesIO()
        input_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        with st.spinner("AI가 고해상도로 배경을 지우는 중... (무제한 서버 연동)"):
            try:
                # Hugging Face 무료 API 중 가장 안정적인 배경 제거(BirefNet) API 엔드포인트 호출
                API_URL = "https://zcxu-birefnet-general-use.hf.space/run/predict"
                
                # Gradio 기반 Hugging Face API 양식에 맞춰 데이터 구성
                payload = {
                    "data": [
                        {"data": f"data:image/png;base64,{io.BytesIO(img_byte_arr).read().hex()}", "name": "image.png"}
                    ]
                }
                
                # 혹은 더 간결하고 우수한 대체 백엔드 API 세팅
                # 여기서는 가장 대중적이고 에러가 없는 Hugging Face의 rembg api 무료 미러를 활용합니다.
                mirror_url = "https://danielgatis-rembg.hf.space/api/remove"
                response = requests.post(mirror_url, files={'file': img_byte_arr})
                
                if response.status_code == 200:
                    output_image = Image.open(io.BytesIO(response.content))
                    st.image(output_image, use_container_width=True)
                    
                    # 다운로드 버튼
                    st.download_button(
                        label="📥 배경 없는 투명 PNG 다운로드",
                        data=response.content,
                        file_name=f"photoroom_unlimited_{uploaded_file.name.split('.')[0]}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                else:
                    st.error(f"서버 응답 오류 (코드: {response.status_code}). 잠시 후 다시 시도해 주세요.")
            except Exception as e:
                st.error(f"연결 중 오류가 발생했습니다: {str(e)}")
