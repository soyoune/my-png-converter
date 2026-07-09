# 클릭이 발생했을 때 배경 제거 로직 작동 (캐릭터 보호형 FloodFill)
        if value is not None:
            x, y = int(value["x"]), int(value["y"])
            
            # OpenCV FloodFill 알고리즘 적용을 위해 RGB 채널과 알파 채널 분리
            rgb = img_array[:, :, :3]
            alpha = img_array[:, :, 3]
            
            # FloodFill을 위한 마스크 생성 (이미지보다 사방으로 2픽셀 더 커야 함)
            h, w = rgb.shape[:2]
            mask = np.zeros((h + 2, w + 2), np.uint8)
            
            # 💡 핵심 로직: FloodFill 알고리즘 적용
            # 사용자가 클릭한 지점(x, y)과 색상이 유사하면서 '연속적으로 연결된 영역'만 추적하여 mask에 1을 채웁니다.
            # 캐릭터 내부의 흰색은 외곽선에 가로막혀 연결되지 않으므로 mask에 포함되지 않습니다.
            
            # BGR 색상 순서로 클릭된 색상 가져오기 (OpenCV standard)
            c_r, c_g, c_b = int(rgb[y, x, 0]), int(rgb[y, x, 1]), int(rgb[y, x, 2])
            
            # 오차 범위 설정 (loDiff, upDiff = 10) - 필요시 수치를 높여 더 넓은 범위의 흰색을 잡을 수 있습니다.
            flooded = rgb.copy()
            cv2.floodFill(flooded, mask, (x, y), (0, 0, 0), loDiff=(10, 10, 10), upDiff=(10, 10, 10))
            
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
