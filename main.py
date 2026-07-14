import streamlit as st

# 1. 페이지 레이아웃 및 탭 설정
st.set_page_config(
    page_title="AI Background Remover (Photoroom Style)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# UI 커스텀 스타일 (포토룸 테마)
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
            margin-bottom: 20px;
        }
        /* 앱 전체 카드 스타일 */
        .app-container {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid #2a2a30;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">AI Photoroom Remover</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">서버 전송 없이 사용자의 브라우저에서 직접 실행되는 100% 무제한 무료 누끼 제거기입니다.</div>', unsafe_allow_html=True)

# 2. 안정적으로 가동 중인 Hugging Face의 또 다른 공식 무료 WASM 엔진 사용
src_url = "https://xenova-remove-background-web.hf.space"

st.markdown('<div class="app-container">', unsafe_allow_html=True)
st.components.v1.iframe(src=src_url, height=750, scrolling=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
    <div style="text-align: center; margin-top: 15px; color: #6e6e73; font-size: 13px;">
        💡 <b>작동 원리:</b> Hugging Face의 오픈소스 <a href="https://huggingface.co/briaai/RMBG-1.4" target="_blank" style="color: #ff007f; text-decoration: none;">RMBG V1.4</a> 모델을 
        Transformers.js를 통해 브라우저 내부에서 로컬로 직접 구동합니다. 이미지가 외부 서버로 전송되지 않아 매우 안전합니다.
    </div>
""", unsafe_allow_html=True)
