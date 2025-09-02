import cv2
import numpy as np
import os
from glob import glob
import cv2
import numpy as np
import os
from glob import glob

in_dir = "/home/krri/바탕화면/background_LS315_0828/crackLS315_datasets/gt"
out_mask_dir = "/home/krri/바탕화면/background_LS315_0828/crackLS315_datasets/dilation_gt"

os.makedirs(out_mask_dir, exist_ok=True)

# dilation 커널 (4방향)
kernel = np.array([[0,1,0],
                   [1,1,1],
                   [0,1,0]], dtype=np.uint8)

for fpath in glob(os.path.join(in_dir, "*.bmp")):
    fname = os.path.basename(fpath)
    
    mask = cv2.imread(fpath, cv2.IMREAD_GRAYSCALE)
    _, bin_mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

    # === dilation (붙을 수 있는 부분 붙여줌) ===
    dilated = cv2.dilate(bin_mask, kernel, iterations=1)

    # === 윤곽 + 계층 구조 찾기 ===
    contours, hierarchy = cv2.findContours(dilated, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    vis = cv2.cvtColor(dilated, cv2.COLOR_GRAY2BGR)

    cv2.imwrite(os.path.join(out_mask_dir, fname), dilated)

print("모든 이미지 처리 완료 (dilation")
