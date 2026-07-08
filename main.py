import streamlit as st
from rembg import remove
from PIL import Image
import io

st.title("✂️ 화질 손실 없는 배경 제거기")
st.write("이미지를 업로드하면 AI가 배경을 투명하게 만들어 드립니다.")

# 파일 업로드 버튼
uploaded_file = st.file_uploader("이미지를 선택하세요...", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    # 이미지 열기
    input_image = Image.open(uploaded_file)
    
    # 웹 화면에 원본 표시
    st.image(input_image, caption="원본 이미지", use_container_width=True)
    
    with st.spinner("배경을 제거하는 중... 잠시만 기다려 주세요."):
        # 배경 제거 처리
        output_image = remove(input_image)
        
        # 다운로드를 위한 바이트 변환
        buf = io.BytesIO()
        output_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
    
    # 웹 화면에 결과 표시 및 다운로드 버튼 생성
    st.image(output_image, caption="배경 제거 완료", use_container_width=True)
    st.download_button(
        label="투명 PNG 다운로드",
        data=byte_im,
        file_name="transparent_output.png",
        mime="image/png"
    )
