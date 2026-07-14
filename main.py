import streamlit as st

# 1. 페이지 와이드 레이아웃 설정
st.set_page_config(
    page_title="AI Photoroom Background Remover",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 기본 Streamlit 여백 및 메뉴 숨기기
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .main { background-color: #121214; color: #ffffff; padding: 0 !important; }
        .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    </style>
""", unsafe_allow_html=True)

# 2. 외곽 경계선 추출 기반 (Boundary-focused Magic Wand) 엔진 탑재 HTML
photoroom_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Photoroom Engine</title>
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
            justify-content: center;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
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
            max-width: 900px;
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
            margin-top: 30px;
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
            height: 450px;
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
            display: block;
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
            transition: transform 0.2s, box-shadow 0.2s;
            text-align: center;
            text-decoration: none;
            box-sizing: border-box;
        }
        .btn-download:hover {
            transform: scale(1.01);
            box-shadow: 0 0 20px rgba(255, 0, 127, 0.4);
        }
        .loading {
            display: none;
            margin-top: 20px;
            text-align: center;
            color: #ff007f;
            font-weight: bold;
        }
    </style>
</head>
<body>

    <div class="header">
        <h1>AI Photoroom Background Remover</h1>
        <p>캐릭터 내부는 안전하게 보호하고, 외곽 경계선 바깥쪽 배경 위주로 누끼를 제거합니다.</p>
    </div>

    <div class="container">
        <div class="dropzone" id="dropzone" onclick="document.getElementById('fileInput').click()">
            <p>📥 여기에 이미지를 끌어다 놓거나 클릭하여 업로드하세요</p>
            <p style="font-size: 12px; color: #71717a; margin-top: 8px;">Supports PNG, JPG, JPEG</p>
            <input type="file" id="fileInput" accept="image/*" style="display: none">
        </div>

        <div class="loading" id="loading">⚡ 캐릭터 외곽선을 분석하여 배경을 분리하는 중...</div>

        <div class="preview-area" id="previewArea">
            <div class="preview-box">
                <h3>📷 원본 이미지</h3>
                <div class="img-wrapper">
                    <img id="originalImg" src="" alt="Original">
                </div>
            </div>
            <div class="preview-box">
                <h3>✨ 배경 제거 완료</h3>
                <div class="img-wrapper transparent-bg">
                    <img id="resultImg" src="" alt="Result">
                </div>
            </div>
        </div>

        <a id="downloadBtn" class="btn-download" style="display: none;">📥 배경 없는 고화질 PNG 다운로드</a>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const originalImg = document.getElementById('originalImg');
        const resultImg = document.getElementById('resultImg');
        const previewArea = document.getElementById('previewArea');
        const loading = document.getElementById('loading');
        const downloadBtn = document.getElementById('downloadBtn');

        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;

            loading.style.display = 'block';
            previewArea.style.display = 'none';
            downloadBtn.style.display = 'none';

            const reader = new FileReader();
            reader.onload = function(event) {
                originalImg.src = event.target.result;
                
                const img = new Image();
                img.src = event.target.result;
                img.onload = function() {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);

                    const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const data = imgData.data;
                    const width = canvas.width;
                    const height = canvas.height;

                    // 테두리(가장자리 4면)에서 시작하여 안쪽으로 타고 들어가는 외곽 채우기(Flood Fill) 알고리즘 적용
                    // 이 방식을 쓰면 캐릭터가 경계선 역할을 해줘서 캐릭터 내부의 하얀색은 침범당하지 않습니다.
                    const visited = new Uint8Array(width * height);
                    const queue = [];

                    // 상하좌우 외곽 테두리 픽셀들을 시작점으로 큐에 주입
                    const rTarget = data[0], gTarget = data[1], bTarget = data[2];
                    const tolerance = 55; // 포차코 배경 가공에 최적화된 경계 임계값

                    function checkAndEnqueue(x, y) {
                        const idx = y * width + x;
                        if (visited[idx]) return;
                        
                        const pIdx = idx * 4;
                        const r = data[pIdx];
                        const g = data[pIdx + 1];
                        const b = data[pIdx + 2];

                        // 타겟 배경색과의 거리 계산
                        const diff = Math.sqrt(Math.pow(r - rTarget, 2) + Math.pow(g - gTarget, 2) + Math.pow(b - bTarget, 2));
                        
                        if (diff < tolerance) {
                            visited[idx] = 1;
                            queue.push(idx);
                        }
                    }

                    // 상하 테두리 스캔
                    for (let x = 0; x < width; x++) {
                        checkAndEnqueue(x, 0);
                        checkAndEnqueue(x, height - 1);
                    }
                    // 좌우 테두리 스캔
                    for (let y = 0; y < height; y++) {
                        checkAndEnqueue(0, y);
                        checkAndEnqueue(width - 1, y);
                    }

                    // BFS 탐색으로 외부 배경 영역만 추적하여 지우기
                    let head = 0;
                    while (head < queue.length) {
                        const idx = queue[head++];
                        const x = idx % width;
                        const y = Math.floor(idx / width);

                        // 4방향 탐색
                        if (x > 0) checkAndEnqueue(x - 1, y);
                        if (x < width - 1) checkAndEnqueue(x + 1, y);
                        if (y > 0) checkAndEnqueue(x, y - 1);
                        if (y < height - 1) checkAndEnqueue(x, y + 1);
                    }

                    // 탐색 완료된 외부 배경 픽셀만 알파채널을 0(투명)으로 수정
                    for (let i = 0; i < visited.length; i++) {
                        if (visited[i] === 1) {
                            data[i * 4 + 3] = 0;
                        }
                    }

                    ctx.putImageData(imgData, 0, 0);
                    
                    const outputUrl = canvas.toDataURL("image/png");
                    resultImg.src = outputUrl;

                    downloadBtn.href = outputUrl;
                    downloadBtn.download = "photoroom_magic_" + file.name.split('.')[0] + ".png";

                    loading.style.display = 'none';
                    previewArea.style.display = 'grid';
                    downloadBtn.style.display = 'block';
                };
            };
            reader.readAsDataURL(file);
        });
    </script>
</body>
</html>
"""

st.components.v1.html(photoroom_html, height=900, scrolling=False)
