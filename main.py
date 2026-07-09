import streamlit as st
from PIL import Image
import numpy as np
import io
import os
# 이미지 클릭 좌표 수집 라이브러리 (이미 터미널에 설치하셨으므로 requirements.txt에만 추가)
from streamlit_image_coordinates import streamlit_image_coordinates

st.title("🎯 스마트 배경 및 그림자 제거기")
st.write("이미지에서 **지우고 싶은 배경이나 그림자 부분(예: 흰 바탕)**을 한 곳만 클릭하세요!")

uploaded_files = st.file_uploader(
    "이미지를 선택하세요...", 
    type=["jpg", "jpeg", "png", "webp"], 
    accept_multiple_files=True
)

if uploaded_files:
    # 세션 상태를 활용해 각 파일별로 작업 상태 저장
    if "processed_images" not in st.session_state:
        st.session_state.processed_images = {}

    for uploaded_file in uploaded_files:
        original_name = uploaded_file.name
        file_name, _ = os.path.splitext(original_name)
        new_filename = f"new_{file_name}.png"
        
        st.markdown(f"---")
        st.subheader(f"작업 파일: {original_name}")
        
        # 이미지 로드
        image = Image.open(uploaded_file).convert("RGBA")
        img_array = np.array(image)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("👇 지울 배경/그림자 한 곳을 클릭하세요.")
            # 💡 사용자가 이미지를 클릭하면 좌표 수집
            value = streamlit_image_coordinates(image, key=f"click_{original_name}")
            
        # 클릭이 발생했을 때 배경 및 그림자 제거 로직 작동
        if value is not None:
            x, y = value["x"], value["y"]
            
            # 클릭한 지점의 R, G, B, A 색상값 가져오기
            try:
                # 사용자가 이미지 캔버스 바깥이나 경계를 클릭했을 때를 대비한 예외 처리
                clicked_color = img_array[y, x] 
            except IndexError:
                st.warning("이미지 내부를 다시 정확히 클릭해 주세요.")
                st.stop()
                
            c_r, c_g, c_b, c_a = clicked_color
            
            # 색상 제거 오차 범위 설정 (밝기 기준)
            # 흰색 배경과 그림자를 함께 지우기 위해 범위를 대폭 넓혔습니다.
            # 💡 조절 팁: 그림자가 덜 지워지면 값을 높이고, 캐릭터 내부가 지워지면 값을 낮추세요.
            r_range = g_range = b_range = 50 
            
            # HSV 색공간 대신 RGB 채널별 범위를 지정하여 마스킹
            # 클릭한 색상을 기준으로 하한/상한값 계산 (0~255 범위 준수)
            lower_bound = np.array([
                max(0, c_r - r_range),
                max(0, c_g - g_range),
                max(0, c_b - b_range),
                0  # 알파 채널은 무관
            ])
            upper_bound = np.array([
                min(255, c_r + r_range),
                min(255, c_g + g_range),
                min(255, c_b + b_range),
                255
            ])
            
            # 💡 핵심 로직: 이미지 전체에서 클릭한 색상의 범위에 해당하는 모든 영역을 찾습니다.
            mask = ((img_array >= lower_bound) & (img_array <= upper_bound)).all(axis=-1)
            
            # 찾은 영역(배경+그림자)의 알파(투명도) 값을 0으로 변경
            new_img_array = img_array.copy()
            new_img_array[mask, 3] = 0
            
            # 최종 투명 이미지 합성
            output_image = Image.fromarray(new_img_array)
            st.session_state.processed_images[original_name] = output_image

        # 결과 출력 및 다운로드 (기존 코드와 동일)
        with col2:
            if original_name in st.session_state.processed_images:
                st.write("✨ 결과 이미지 (배경 및 그림자 투명화 완료)")
                out_img = st.session_state.processed_images[original_name]
                st.image(out_img, use_container_width=True)
                
                # 다운로드 버튼
                buf = io.BytesIO()
                out_img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label=f"📥 {new_filename} 다운로드",
                    data=byte_im,
                    file_name=new_filename,
                    mime="image/png",
                    key=f"dl_{original_name}"
                )
            else:
                st.info("왼쪽 이미지에서 배경을 클릭하면 결과가 여기에 표시됩니다.")
