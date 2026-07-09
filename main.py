import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io
import os
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
        
        st.markdown("---")
        st.subheader(f"작업 파일: {original_name}")
        
        # 이미지 로드
        image = Image.open(uploaded_file).convert("RGBA")
        img_array = np.array(image)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("👇 지울 배경/그림자 한 곳을 클릭하세요.")
            # 사용자가 이미지를 클릭하면 좌표 수집
            value = streamlit_image_coordinates(image, key=f"click_{original_name}")
            
        # 클릭이 발생했을 때 배경 및 그림자 제거 로직 작동
        if value is not None:
            x, y = value["x"], value["y"]
            
            # 클릭한 지점의 R, G, B, A 색상값 가져오기
            try:
                clicked_color = img_array[y, x] 
            except IndexError:
                st.warning("이미지 내부를 다시 정확히 클릭해 주세요.")
                st.stop()
                
            c_r, c_g, c_b, c_a = clicked_color
            
            # 색상 제거 오차 범위 설정 (밝기 기준)
            r_range = g_range = b_range = 50 
            
            # 클릭한 색상을 기준으로 하한/상한값 계산
            lower_bound = np.array([
                max(0, c_r - r_range),
                max(0, c_g - g_range),
                max(0, c_b - b_range),
                0
            ])
            upper_bound = np.array([
                min(255, c_r + r_range),
                min(255, c_g + g_range),
                min(255, c_b + b_range),
                255
            ])
            
            # 이미지 전체에서 범위 내에 해당하는 모든 영역 찾기
            mask = ((img_array >= lower_bound) & (img_array <= upper_bound)).all(axis=-1)
            
            # 찾은 영역의 알파(투명도) 값을 0으로 변경
            new_img_array = img_array.copy()
            new_img_array[mask, 3] = 0
            
            # 최종 투명 이미지 합성 및 세션 저장
            output_image = Image.fromarray(new_img_array)
            st.session_state.processed_images[original_name] = output_image

        # 결과 출력 및 다운로드 영역
        with col2:
            if original_name in st.session_state.processed_images:
                st.write("✨ 결과 이미지 (배경 및 그림자 투명화 완료)")
                out_img = st.session_state.processed_images[original_name]
                
                # 투명도 확인을 위한 격자무늬(Checkered) 배경 생성
                bg_checker = Image.new("RGBA", out_img.size, (255, 255, 255, 255))
                ch_w, ch_h = out_img.size
                grid_size = 16
                
                draw = ImageDraw.Draw(bg_checker)
                for i in range(0, ch_w, grid_size):
                    for j in range(0, ch_h, grid_size):
                        if (i // grid_size + j // grid_size) % 2 == 0:
                            draw.rectangle([i, j, i + grid_size, j + grid_size], fill=(240, 240, 240, 255))
                
                # 격자 배경 위에 작업한 투명 이미지 합성
                preview_img = Image.alpha_composite(bg_checker, out_img)
                
                # 화면 표시 (격자 포함)
                st.image(preview_img, caption="💡 격자 부분 = 투명하게 지워진 영역", width=None)
                
                # 다운로드 파일 준비 (격자 없는 진짜 투명 이미지)
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
