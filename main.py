import streamlit as st
# 배경 제거 라이브러리 (예시: rembg를 사용하는 경우)
# 만약 다른 라이브러리나 API를 쓰신다면 해당 처리 로직을 유지하시면 됩니다.
from rembg import remove 
from PIL import Image
import io

st.title("✂️ 화질 손실 없는 배경 제거기")
st.write("이미지를 업로드하면 AI가 배경을 투명하게 만들어 드립니다.")

# 1. accept_multiple_files=True 옵션을 추가하여 여러 파일 업로드 가능하게 변경
uploaded_files = st.file_uploader(
    "이미지를 선택하세요...", 
    type=["jpg", "jpeg", "png", "webp"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.write(f"총 {len(uploaded_files)}개의 파일이 업로드되었습니다.")
    
    # 2. 루프를 돌며 각 파일을 순차적으로 처리
    for uploaded_file in uploaded_files:
        # 원래 파일명 가져오기
        original_name = uploaded_file.name
        # 확장자를 제외한 파일명과 확장자 분리 (예: photo.jpg -> photo, .jpg)
        import os
        file_name, _ = os.path.splitext(original_name)
        
        # 3. 파일명 앞에 'new_' 접두사 붙이고 png로 확장자 고정
        new_filename = f"new_{file_name}.png"
        
        st.markdown(f"---")
        st.subheader(f"파일 처리 중: {original_name}")
        
        # 이미지 열기 및 배경 제거 로직
        image = Image.open(uploaded_file)
        
        # 이미지 처리 (여기서는 rembg 예시, 작성하신 AI 변환 로직을 넣으시면 됩니다)
        with st.spinner(f"{original_name} 배경 제거 중..."):
            output_image = remove(image)
        
        # 이미지를 바이트스트림으로 변환 (다운로드 버튼용)
        buf = io.BytesIO()
        output_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        # 결과 화면 표시
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption="원본 이미지", use_container_width=True)
        with col2:
            st.image(output_image, caption="배경 제거 결과", use_container_width=True)
        
        # 4. 개별 파일 다운로드 버튼 (새로운 파일명 적용)
        st.download_button(
            label=f"📥 {new_filename} 다운로드",
            data=byte_im,
            file_name=new_filename,
            mime="image/png",
            key=new_filename # 다중 버튼 생성 시 고유 key 필요
        )
