# 결과 출력 및 다운로드
        with col2:
            if original_name in st.session_state.processed_images:
                st.write("✨ 결과 이미지 (배경 및 그림자 투명화 완료)")
                out_img = st.session_state.processed_images[original_name]
                
                # 💡 [추가] Streamlit 화면에서 투명도를 눈으로 확인하기 위한 격자무늬 합성
                # 원본 이미지 크기의 격자(Checkered) 배경 생성
                bg_checker = Image.new("RGBA", out_img.size, (255, 255, 255, 255))
                ch_w, ch_h = out_img.size
                grid_size = 16  # 격자 크기
                
                # 가상의 투명 배경 패턴 그리기 (연한 회색과 흰색 교차)
                import PIL.ImageDraw as ImageDraw
                draw = ImageDraw.Draw(bg_checker)
                for i in range(0, ch_w, grid_size):
                    for j in range(0, ch_h, grid_size):
                        if (i // grid_size + j // grid_size) % 2 == 0:
                            draw.rectangle([i, j, i + grid_size, j + grid_size], fill=(240, 240, 240, 255))
                
                # 격자 배경 위에 작업한 투명 이미지를 얹어서 화면 표시용 이미지 생성
                preview_img = Image.alpha_composite(bg_checker, out_img)
                
                # 화면에는 격자가 합성된 이미지를 보여주어 투명 여부 확인
                st.image(preview_img, caption="💡 격자 부분 = 투명하게 지워진 영역", use_container_width=True)
                
                # 📥 다운로드 버튼 (격자가 없는 진짜 투명한 이미지를 다운로드)
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
