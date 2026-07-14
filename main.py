import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import cv2
import io

st.set_page_config(
    page_title="Classic Professional Background Remover",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# UI 디자인 커스텀
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .main { background-color: #121214; color: #ffffff; }
        .title-text {
            font-size: 30px;
            font-weight: 800;
            text-align: center;
            margin-top: 10px;
            background: linear-gradient(45deg, #00f2fe, #4facfe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle-text {
            text-align: center;
            color: #8a8a93;
            font-size: 14px;
            margin-bottom: 20px;
        }
        .stDownloadButton>button {
            background: linear-gradient(45deg, #00f2fe, #4facfe) !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 20px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">Classic Interactive BG Remover</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">AI 없이 마우스 드로잉과 고전 그래픽 알고리즘(GrabCut)으로 포차코 얼굴을 완벽하게 살려냅니다!</div>', unsafe_allow_html=True)

# 1. 파일 업로드
uploaded_file = st.file_uploader("누끼를 딸 이미지를 올려주세요", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 이미지 로드 및 크기 최적화 (속도 및 드로잉 캔버스 정합성용)
    raw_image = Image.open(uploaded_file).convert("RGB")
    max_size = 600
    raw_image.thumbnail((max_size, max_size))
    img_np = np.array(raw_image)
    h, w, _ = img_np.shape

    # UI 레이아웃 분할
    col_control, col_canvas, col_result = st.columns([1, 2, 2])

    with col_control:
        st.markdown("### 🛠️ 마킹 도구 선택")
        st.write("이미지 위에 마우스로 슥슥 그려서 컴퓨터에게 알려주세요!")
        
        # 브러시 모드 선택
        mode = st.radio(
            "브러시 종류",
            ("🔴 보존할 구역 (포차코 몸통/얼굴 안쪽)", "🟢 제거할 구역 (바깥쪽 배경)"),
            index=0
        )
        
        stroke_width = st.slider("브러시 크기", 3, 30, 10)
        
        # 색상 세팅
        stroke_color = "#FF0000" if "보존할 구역" in mode else "#00FF00"
        
        st.markdown("""
            ---
            **💡 사용 팁:**
            1. **🔴 보존할 구역**을 선택하고 포차코 얼굴과 귀 안쪽에 빨간 선을 대충 그려줍니다.
            2. **🟢 제거할 구역**을 선택하고 바깥 배경 영역에 초록 선을 슥슥 그려줍니다.
            3. 우측에 캐릭터 얼굴이 완벽하게 보존된 정밀 누끼 컷이 실시간으로 생성됩니다!
        """)

    with col_canvas:
        st.markdown("### ✍️ 마우스로 그리기")
        
        # 드로잉 캔버스 생성
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_image=raw_image,
            update_streamlit=True,
            height=h,
            width=w,
            drawing_mode="freedraw",
            key="canvas",
        )

    with col_result:
        st.markdown("### ✨ 알고리즘 결과")
        
        # 사용자가 그린 드로잉 데이터가 존재할 때만 고전 GrabCut 연산 시작
        if canvas_result.image_data is not None and np.any(canvas_result.image_data):
            # 드로잉 마스크 가져오기 (RGBA)
            draw_mask = canvas_result.image_data
            
            # GrabCut용 마스크 초기화 (기본값은 '아마도 배경'인 PR_BGD)
            mask = np.zeros((h, w), dtype=np.uint8)
            mask[:] = cv2.GC_PR_BGD
            
            # 사용자가 그린 빨간색(보존), 초록색(제거) 영역을 GrabCut 마스크 값에 대입
            # draw_mask의 R, G 채널 값을 비교하여 마스킹
            for y in range(h):
                for x in range(w):
                    r, g, b, a = draw_mask[y, x]
                    if a > 0:  # 투명하지 않은 그린 영역인 경우
                        if r > 200 and g < 100:  # 빨간색 브러시 -> 확실한 전경 (보존)
                            mask[y, x] = cv2.GC_FGD
                        elif g > 200 and r < 100:  # 초록색 브러시 -> 확실한 배경 (제거)
                            mask[y, x] = cv2.GC_BGD

            # 알고리즘 연산에 필요한 임시 메모리 버퍼 생성
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)

            with st.spinner("경계면 정밀 분석 중..."):
                try:
                    # OpenCV 고전 명작 GrabCut 알고리즘 구동
                    cv2.grabCut(img_np, mask, None, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)
                    
                    # 최종 살릴 영역 추출 (확실한 전경 + 아마도 전경)
                    final_mask = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype('uint8')
                    
                    # 원본 이미지에 마스크를 씌워 알파 채널(투명도)이 포함된 투명 이미지로 변환
                    result_rgba = cv2.cvtColor(img_np, cv2.COLOR_RGB2RGBA)
                    result_rgba[:, :, 3] = final_mask
                    
                    # 결과 출력
                    output_image = Image.fromarray(result_rgba)
                    st.image(output_image, use_container_width=True)
                    
                    # 다운로드 버튼
                    buf = io.BytesIO()
                    output_image.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="📥 투명 PNG로 저장하기",
                        data=byte_im,
                        file_name=f"classic_cut_{uploaded_file.name.split('.')[0]}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                except Exception as e:
                    st.info("좌측 화면에 보존할 영역(빨간색)과 제거할 영역(초록색)을 조금 더 그려주세요!")
        else:
            # 드로잉이 없을 때의 가이드 안내
            st.info("좌측 캔버스 위에 보존할 곳(빨간선)과 지울 곳(초록선)을 슥슥 그리면 즉시 결과가 나옵니다!")
