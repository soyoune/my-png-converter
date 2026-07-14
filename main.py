import streamlit as st

# 1. 포토룸 스타일 와이드 레이아웃 설정
st.set_page_config(
    page_title="AI Photoroom - Unlimited Edition",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Streamlit 기본 여백 및 헤더 숨기기
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .main { background-color: #121214; color: #ffffff; padding: 0 !important; }
        .block-container { padding-top: 1.5rem !important; padding-bottom: 1.5rem !important; }
    </style>
""", unsafe_allow_html=True)

# 2. 브라우저 내장형 고성능 AI 세그멘테이션 엔진 (HTML5 + WebMatting JS)
# 서버 통신과 제한이 전혀 없는 100% 로컬 무제한 방식입니다.
unlimited_photoroom_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unlimited AI Photoroom</title>
    <style>
        body {
            background-color: #121214;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .header {
            text-align: center;
            margin-bottom: 25px;
        }
        h1 {
            font-size: 32px;
            font-weight: 800;
            background: linear-gradient(45deg, #ff007f, #7f00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0 0 10px 0;
        }
        p {
            color: #8a8a93;
            font-size: 14px;
            margin: 0;
        }
        .container {
            width: 100%;
            max-width: 950px;
            background: #1a1a1e;
            border: 1px solid #2a2a30;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.5);
            box-sizing: border-box;
        }
        .dropzone {
            border: 2px dashed #3e3e46;
            border-radius: 12px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: #151518;
            margin-bottom: 25px;
        }
        .dropzone:hover {
            border-color: #ff007f;
            background: #1b1319;
        }
        .dropzone p {
            font-size: 16px;
            color: #e4e4e7;
        }
        .preview-area {
            display: none;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 10px;
        }
        .preview-box {
            background: #202024;
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            border: 1px solid #2a2a30;
        }
        .preview-box h3 {
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 16px;
            color: #a1a1aa;
        }
        .img-wrapper {
            position: relative;
            width: 100%;
            height: 400px;
            border-radius: 8px;
            overflow: hidden;
            background-color: #121214;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .transparent-bg {
            background-image: linear-gradient(45deg, #2a2a30 25%, transparent 25%), linear-gradient(-45deg, #2a2a30 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #2a2a30 75%), linear-gradient(-45deg, transparent 75%, #2a2a30 75%);
            background-size: 20px 20px;
            background-position: 0 0, 0 10px, 10px -10px, -10px 아하, 클라우드플레어처럼 매일 리셋되는 개수 제한마저 아예 없이 **"진짜 완전 무제한"**으로 누끼를 따고 싶으시군요! 

컴퓨터 그래픽스 고전 알고리즘(`GrabCut`)은 복잡한 마킹을 수동으로 그려야 해서 불편했고, AI 모델은 서버 성능 제한과 API 제한에 걸려 난감하셨을 텐데, 딱 맞는 최후의 방법이 있습니다.

바로 **사용자의 웹 브라우저 자체 엔진(WebAssembly 및 ONNX Runtime Web)을 활용하여, 컴퓨터나 스마트폰의 자체 연산 장치(CPU/GPU)로 딥러닝 AI를 돌리는 방식**입니다.

이 방식은 내 컴퓨터의 성능을 빌려 내 브라우저 안에서 AI를 직접 구동하기 때문에:
1. **완전 무제한:** 외부 API 서버를 쓰지 않으므로 평생 몇 만 장을 돌려도 제한이 없고 비용도 0원입니다.
2. **개인 정보 보호:** 이미지가 외부 서버로 전송되지 않고 내 기기 안에서만 처리됩니다.
3. **포차코 얼굴 보존:** 고성능 AI 모델(`RMBG-1.4`)을 브라우저에 가볍게 얹어 돌리기 때문에 포차코의 흰색 얼굴도 완벽하게 살아납니다.

---

### 🛠️ 1. `requirements.txt` (완전 초경량화)
서버에서 무거운 파이썬 AI 패키지를 설치하다가 에러가 나는 것을 완벽하게 방지하기 위해 깃허브의 **`requirements.txt`**를 아래 딱 한 줄로만 설정해 주세요. 

```text
streamlit
