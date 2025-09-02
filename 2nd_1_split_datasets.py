import os
import shutil
import random
from glob import glob
import re

# --- 경로 설정 ---
gt_dir = "/home/krri/바탕화면/background_LS315_0828/crackLS315_datasets/dilation_gt"
img_dir = "/home/krri/바탕화면/background_LS315_0828/crackLS315_datasets/images"
out_root = "/home/krri/바탕화면/background_LS315_0828/crackLS315_datasets/split"

splits = ["train", "val", "test"]

# --- 출력 폴더 구조 생성 ---
for split in splits:
    os.makedirs(os.path.join(out_root, "gt", split), exist_ok=True)
    os.makedirs(os.path.join(out_root, "images", split), exist_ok=True)

# --- 파일 목록 불러오기 (gt 기준) ---
gt_files = sorted(glob(os.path.join(gt_dir, "*.bmp")))
print(f"총 GT 파일 개수: {len(gt_files)}")

# --- train/val/test 비율 나누기 ---
random.seed(42)  # 재현성 보장
random.shuffle(gt_files)

n_total = len(gt_files)
n_train = int(n_total * 0.6)
n_val   = int(n_total * 0.2)
n_test  = n_total - n_train - n_val

train_files = gt_files[:n_train]
val_files   = gt_files[n_train:n_train+n_val]
test_files  = gt_files[n_train+n_val:]

split_map = {
    "train": train_files,
    "val": val_files,
    "test": test_files
}

# --- 복사 ---
for split, files in split_map.items():
    for gt_path in files:
        fname = os.path.basename(gt_path)
        img_path = os.path.join(img_dir, fname.replace(".bmp", ".jpg"))  # 확장자 맞게 조정 필요

        # GT 복사
        shutil.copy(gt_path, os.path.join(out_root, "gt", split, fname))
        
        # Image 복사
        if os.path.exists(img_path):
            shutil.copy(img_path, os.path.join(out_root, "images", split, os.path.basename(img_path)))
        else:
            print(f"[경고] {img_path} 없음")