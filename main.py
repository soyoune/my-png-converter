import streamlit as st

st.set_page_config(page_title="AI Photoroom - Unlimited Client Edition", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #121214; color: #ffffff; }
        .stApp { background-color: #121214; }
    </style>
""", unsafe_allow_html=True)

unlimited_ai_html = """
<!DOCTYPE html>
<html>
<body>
    <div id="status" style="color: #ff007f; font-weight: bold; text-align: center; margin: 20px;">
        로컬 AI 로드 중... (잠시만 기다려 주세요)
    </div>
    <script type="module">
        import { pipeline, env } from 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.16.1';
        
        // 보안 오류 해결: 모델 캐싱 및 원격 로드 설정 최적화
        env.allowLocalModels = false;
        env.useBrowserCache = true;

        async function initAI() {
            try {
                const status = document.getElementById('status');
                status.innerText = "⚡ AI 엔진 초기화 완료! 이미지를 업로드하세요.";
                window.segmenter = await pipeline('image-segmentation', 'Xenova/rmbg-1.4');
            } catch (err) {
                document.getElementById('status').innerText = "❌ 오류: " + err.message;
            }
        }
        initAI();
    </script>
    <div style="text-align: center;">
        <input type="file" id="fileInput" accept="image/*">
    </div>
    <script>
        document.getElementById('fileInput').onchange = async (e) => {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = async (event) => {
                const img = new Image();
                img.src = event.target.result;
                img.onload = async () => {
                    document.getElementById('status').innerText = "✨ 배경 제거 작업 중...";
                    const output = await window.segmenter(img.src);
                    
                    const canvas = document.createElement('canvas');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    
                    // 마스크 적용
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const mask = await output.resize(canvas.width, canvas.height).data();
                    for (let i = 0; i < mask.length; i++) {
                        imageData.data[i * 4 + 3] = mask[i] * 255;
                    }
                    ctx.putImageData(imageData, 0, 0);
                    
                    const resultImg = document.createElement('img');
                    resultImg.src = canvas.toDataURL();
                    document.body.appendChild(resultImg);
                    document.getElementById('status').innerText = "✅ 완료!";
                };
            };
            reader.readAsDataURL(file);
        };
    </script>
</body>
</html>
"""
st.components.v1.html(unlimited_ai_html, height=800)
