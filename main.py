import streamlit as st
from rembg import remove, new_session  # new_session 추가
from PIL import Image
import io
import os

st.title("✂️ 화질 손실 없는 배경 제거기")
st.write("이미지를 업로드하면 AI가 배경을 투명하게 만들어 드립니다.")

uploaded_files = st.file_uploader(
    "이미지를 선택하세요...", 
    type=["jpg", "jpeg", "png", "webp"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.write(f"총 {len(uploaded_files)}개의 파일이 업로드되었습니다.")
    
    # 💡 [개선] 더 정교하고 세밀한 객체 인식을 위한 세션 생성
    # 일반 u2net보다 디테일한 객체 분리에 강한 모델을 사용합니다.
    session = new_session("isnet-general-use") 
    
    for uploaded_file in uploaded_files:
        original_name = uploaded_file.name
        file_name, _ = os.path.splitext(original_name)
        new_filename = f"new_{file_name}.png"
        
        st.markdown(f"---")
        st.subheader(f"파일 처리 중: {original_name}")
        
        image = Image.open(uploaded_file)
        
        with st.spinner(f"{original_name} 배경 제거 중..."):
            # 💡 [개ment] 배경 제거 옵션 디테일 조정
            output_image = remove(
                image,
                session=session,
                alpha_matting=True,          # 가장자리 및 독립 오브젝트 세밀화 활성화
                alpha_matting_foreground_threshold=240, # 전경(살릴 부분) 기준 세부 조절
                alpha_matting_background_threshold=10,  # 배경(지울 부분) 기준 세부 조절
                alpha_matting_ero_size=10    # 세밀도 범위
            )
        
        # 이미지 다운로드 및 표시 로직 (기존과 동일)
        buf = io.BytesIO()
        output_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption="원본 이미지", use_container_width=True)
        with col2:
            st.image(output_image, caption="배경 제거 결과", use_container_width=True)
        
        st.download_button(
            label=f"📥 {new_filename} 다운로드",
            data=byte_im,
            file_name=new_filename,
            mime="image/png",
            key=new_filename
        )
