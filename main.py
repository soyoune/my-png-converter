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
            value = streamlit_image_coordinates(image, key=f"click_{original_name}")
            
        # 클릭이 발생했을 때 배경 및 그림자 제거 로직 작동
        if value is not None:
            # 💡 [정정] streamlit_image_coordinates의 x, y 좌표를 numpy 배열 인덱스(y, x)에 맞게 확실하게 매칭
            x, y = int(value["x"]), int(value["y"])
            
            try:
                # 클릭한 위치의 정확한 RGB 값 추출
                clicked_color = img_array[y, x]
                c_r, c_g, c_b = int(clicked_color[0]), int(clicked_color[1]), int(clicked_color[2])
            except IndexError:
                st.warning("이미지 내부를 다시 정확히 클릭해 주세요.")
                st.stop()
            
            # 색상 제거 오차 범위 (흰색 배경 및 그림자를 잡기 위해 범위를 60으로 확장)
            tolerance = 60
            
            # 이미지의 각 픽셀과 클릭한 색상 간의 거리(오차) 계산
            # R, G, B 채널 각각의 차이를 구합니다.
            diff_r = np.abs(img_array[:, :, 0].astype(int) - c_r)
            diff_g = np.abs(img_array[:, :, 1].astype(int) - c_g)
            diff_b = np.abs(img_array[:, :, 2].astype(int) - c_b)
            
            # 모든 채널의 오차가 tolerance(60)보다 작은 영역을 '배경'으로 지정
            mask = (diff_r < tolerance) & (diff_g < tolerance) & (diff_b < tolerance)
            
            # 💡 핵심: 찾은 배경 영역의 알파 채널(투명도)을 '0(완전 투명)'으로 변경
            new_img_array = img_array.copy()
            new_img_array[mask, 3] = 0
            
            # 최종 투명 이미지 생성 및 세션 저장
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
                
                # 격자 배경 위에 '배경이 투명해진 이미지'를 합성
                preview_img = Image.alpha_composite(bg_checker, out_img)
                
                # 격자가 투명하게 비치는 미리보기 이미지를 화면에 표시
                st.image(preview_img, caption="💡 격자 부분 = 투명하게 지워진 영역", width="stretch")
                
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
