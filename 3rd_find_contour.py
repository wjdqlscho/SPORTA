import cv2
import numpy as np
import os
from glob import glob
import shutil

# 원본 root
root_dir = "/home/krri/바탕화면/background_LS315_0828/crackLS315_datasets/split"

# 최종 datasets root
out_root = "/home/krri/바탕화면/background_LS315_0828/datasets"

for split in ["train", "val", "test"]:
    in_img_dir = os.path.join(root_dir, "images", split)
    in_gt_dir = os.path.join(root_dir, "gt", split)

    out_img_dir = os.path.join(out_root, "images", split)
    out_label_dir = os.path.join(out_root, "labels", split)
    out_gt_dir = os.path.join(out_root, "gt", split)

    os.makedirs(out_img_dir, exist_ok=True)
    os.makedirs(out_label_dir, exist_ok=True)
    os.makedirs(out_gt_dir, exist_ok=True)

    # 이미지 복사
    for fpath in glob(os.path.join(in_img_dir, "*.jpg")):
        shutil.copy(fpath, out_img_dir)

    # GT 변환 + 복사
    for fpath in glob(os.path.join(in_gt_dir, "*.bmp")):
        fname = os.path.basename(fpath)
        name_no_ext = os.path.splitext(fname)[0]

        mask = cv2.imread(fpath, cv2.IMREAD_GRAYSCALE)
        h, w = mask.shape
        _, bin_mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(bin_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # YOLO txt 저장
        label_lines = []
        for cnt in contours:
            if len(cnt) < 3:
                continue
            poly = []
            for (x, y) in cnt[:, 0]:
                poly.append(x / w)
                poly.append(y / h)
            line = "0 " + " ".join(f"{p:.6f}" for p in poly)
            label_lines.append(line)

        with open(os.path.join(out_label_dir, f"{name_no_ext}.txt"), "w") as f:
            f.write("\n".join(label_lines))

        # GT 복사
        shutil.copy(fpath, out_gt_dir)

    print(f"[OK] {split} 세트 변환 완료")

print("=== 최종 datasets 폴더 구성 완료 ===")
