import streamlit as st
from rembg import remove, new_session
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
    
    # 일반 모델보다 객체 분할 및 디테일에 강한 u2net 기반의 세션 생성
    session = new_session("u2net") 
    
    for uploaded_file in uploaded_files:
        original_name = uploaded_file.name
        file_name, _ = os.path.splitext(original_name)
        new_filename = f"new_{file_name}.png"
        
        st.markdown(f"---")
        st.subheader(f"파일 처리 중: {original_name}")
        
        image = Image.open(uploaded_file)
        
        with st.spinner(f"{original_name} 배경 제거 중..."):
            # 💡 하트처럼 색이 선명한 독립된 객체를 살리기 위한 세부 옵션 적용
            output_image = remove(
                image,
                session=session,
                alpha_matting=True,
                alpha_matting_foreground_threshold=270, # 숫자를 높여 선명한 유색 영역을 전경으로 강하게 보호
                alpha_matting_background_threshold=20,  # 완전히 투명해질 완전 배경(흰색 등)의 범위 지정
                alpha_matting_ero_size=2                # 외곽선 주위를 더 촘촘하게 계산하여 하트가 잘리는 현상 방지
            )
        
        # 이미지 다운로드 및 표시 로직
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
