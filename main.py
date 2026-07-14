import streamlit as st

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="AI Photoroom - Unlimited Client Edition",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 기본 여백 제거 및 다크 모드 스타일링
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .main { background-color: #121214; color: #ffffff; padding: 0 !important; }
        .block-container { padding-top: 1.5rem !important; padding-bottom: 1.5rem !important; }
    </style>
""", unsafe_allow_html=True)

# 2. 브라우저 자체 WebAssembly 가속 기반 AI 엔진 탑재 (Transformers.js)
unlimited_ai_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unlimited AI Photoroom</title>
    <!-- 고성능 브라우저 AI 구동을 위한 라이브러리 로드 -->
    <script type="module">
        import { pipeline, env } from 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.16.1';
        env.allowLocalModels = false;
        
        window.runAI = async function(imageSrc) {
            try {
                document.getElementById('status').innerText = "⚡ 내 브라우저에서 AI 모델 초기화 중... (최초 1회만 약 5~10초 소요)";
                
                // 포토룸 엔진 rmbg-1.4 모델 로드
                const upscaler = await pipeline('image-segmentation', 'Xenova/rmbg-1.4');
                
                document.getElementById('status').innerText = "✨ 캐릭터 실루엣 정밀 도려내는 중...";
                const output = await upscaler(imageSrc);
                
                // 결과 이미지 렌더링 및 다운로드 링크 활성화
                const resultImg = document.getElementById('resultImg');
                resultImg.src = output.toDataURL();
                
                const downloadBtn = document.getElementById('downloadBtn');
                downloadBtn.href = output.toDataURL();
                downloadBtn.style.display = 'block';
                
                document.getElementById('status').innerText = "✅ 누끼 제거 완료!";
                document.getElementById('previewArea').style.display = 'grid';
            } catch (err) {
                document.getElementById('status').innerText = "❌ AI 실행 오류: " + err.message;
                console.error(err);
            }
        };
    </script>
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
            font-size: 28px;
            font-weight: 800;
            background: linear-gradient(45deg, #ff007f, #7f00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0 0 8px 0;
        }
        p {
            color: #8a8a93;
            font-size: 13px;
            margin: 0;
        }
        .container {
            width: 100%;
            max-width: 900px;
            background: #1a1a1e;
            border: 1px solid #2a2a30;
            border-radius: 16px;
            padding: 35px;
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
        }
        .dropzone:hover {
            border-color: #ff007f;
            background: #1b1319;
        }
        .status-bar {
            margin-top: 15px;
            text-align: center;
            font-weight: bold;
            color: #ff007f;
            font-size: 14px;
        }
        .preview-area {
            display: none;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 30px;
        }
        .preview-box {
            background: #202024;
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            border: 1px solid #2a2a30;
        }
        .img-wrapper {
            position: relative;
            width: 100%;
            height: 350px;
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
            background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
        }
        img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        .btn-download {
            display: none;
            width: 100%;
            padding: 15px;
            margin-top: 25px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(45deg, #ff007f, #7f00ff);
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
            box-sizing: border-box;
        }
        .btn-download:hover {
            transform: scale(1.01);
            box-shadow: 0 0 20px rgba(255, 0, 127, 0.4);
        }
    </style>
</head>
<body>

    <div class="header">
        <h1>AI Photoroom - Unlimited Edition</h1>
        <p>서버 트래픽이나 API 개수 제한 없이 사용자의 브라우저 성능으로 영원히 무제한 구동됩니다.</p>
    </div>

    <div class="container">
        <div class="dropzone" id="dropzone" onclick="document.getElementById('fileInput').click()">
            <p>📥 여기에 이미지를 끌어다 놓거나 클릭하여 업로드하세요</p>
            <p style="font-size: 11px; color: #71717a; margin-top: 5px;">내 컴퓨터 안에서 실행되므로 외부 데이터가 유출되지 않습니다</p>
            <input type="file" id="fileInput" accept="image/*" style="display: none">
        </div>

        <div class="status-bar" id="status">파일을 올려주시면 로컬 인공지능이 즉시 활성화됩니다.</div>

        <div class="preview-area" id="previewArea">
            <div class="preview-box">
                <p style="color: #a1a1aa; font-weight: bold; margin-bottom: 10px;">📷 원본 이미지</p>
                <div class="img-wrapper">
                    <img id="originalImg" src="" alt="Original">
                </div>
            </div>
            <div class="preview-box">
                <p style="color: #a1a1aa; font-weight: bold; margin-bottom: 10px;">✨ 배경 제거 완료</p>
                <div class="img-wrapper transparent-bg">
                    <img id="resultImg" src="" alt="Result">
                </div>
            </div>
        </div>

        <a id="downloadBtn" class="btn-download" download="photoroom_unlimited.png">📥 배경 없는 고화질 PNG 다운로드</a>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const originalImg = document.getElementById('originalImg');
        const status = document.getElementById('status');
        const previewArea = document.getElementById('previewArea');

        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;

            status.innerText = "⏳ 이미지 파일을 분석하는 중...";
            previewArea.style.display = 'none';

            const reader = new FileReader();
            reader.onload = function(event) {
                const imageSrc = event.target.result;
                originalImg.src = imageSrc;
                previewArea.style.display = 'grid';
                
                // 브라우저 백엔드 AI 모듈 실행
                window.runAI(imageSrc);
            };
            reader.readAsDataURL(file);
        });
    </script>
</body>
</html>
"""

st.components.v1.html(unlimited_ai_html, height=850, scrolling=False)
