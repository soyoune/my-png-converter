# 클릭이 발생했을 때 배경 제거 로직 작동 (그림자 보호형 FloodFill)
        if value is not None:
            x, y = int(value["x"]), int(value["y"])
            
            # OpenCV FloodFill 알고리즘 적용을 위해 RGB 채널과 알파 채널 분리
            rgb = img_array[:, :, :3]
            alpha = img_array[:, :, 3]
            
            # FloodFill을 위한 마스크 생성 (이미지보다 사방으로 2픽셀 더 커야 함)
            h, w = rgb.shape[:2]
            mask = np.zeros((h + 2, w + 2), np.uint8)
            
            # 💡 [핵심] 그림자를 보호하기 위해 loDiff, upDiff 값을 조절
            # 기존 10에서 5로 낮추어, 클릭한 흰색과 색상차가 나는 그림자(연한 회색)를 
            # 배경 범위에서 제외하여 보호합니다.
            flooded = rgb.copy()
            cv2.floodFill(flooded, mask, (x, y), (0, 0, 0), loDiff=(5, 5, 5), upDiff=(5, 5, 5))
            
            # floodFill이 채워진 영역(마스크에서 1이 된 부분)을 투명하게 만듦
            # 배경 제거된 마스크는 0번 행렬 기준 1부터 h+1까지 추출
            actual_mask = mask[1:h+1, 1:w+1]
            
            # 찾은 배경 부분의 알파(투명도) 값을 '0(완전 투명)'으로 변경
            new_alpha = alpha.copy()
            new_alpha[actual_mask == 1] = 0
            
            # 최종 투명 이미지 합성 및 세션 저장
            output_array = np.dstack((rgb, new_alpha))
            output_image = Image.fromarray(output_array)
            st.session_state.processed_images[original_name] = output_image
