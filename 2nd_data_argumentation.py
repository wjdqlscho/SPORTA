import cv2
import os
import numpy as np
from albumentations import HorizontalFlip
from pathlib import Path

# === 경로 설정 (train만 증강) ===
img_dir = "/home/krri/바탕화면/background_LS315_0828/crackLS315_datasets/split/images/train"
mask_dir = "/home/krri/바탕화면/background_LS315_0828/crackLS315_datasets/split/gt/train"

out_img_dir = "/home/krri/바탕화면/background_LS315_0828/aug/images"
out_mask_dir = "/home/krri/바탕화면/background_LS315_0828/aug/gt"
os.makedirs(out_img_dir, exist_ok=True)
os.makedirs(out_mask_dir, exist_ok=True)

# === 변환 정의 ===
flip = HorizontalFlip(p=1.0)
angles = [19, 23, 90]
gammas = [("g03030", 0.3030), ("g06060", 0.6060)]

def gamma_correction(img, gamma):
    invGamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** invGamma * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(img, table)

def rotate_mask_cubic(mask, angle, scale=1.0):
    h, w = mask.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rot = cv2.warpAffine(mask, M, (w, h), flags=cv2.INTER_CUBIC, borderValue=0)
    _, bin_mask = cv2.threshold(rot, 30, 255, cv2.THRESH_BINARY)
    return bin_mask

def center_crop_pad(image, mask, crop_size, out_size=512):
    h, w = image.shape[:2]
    cx, cy = w // 2, h // 2
    half = crop_size // 2

    x1, y1 = max(0, cx - half), max(0, cy - half)
    x2, y2 = min(w, cx + half), min(h, cy + half)

    cropped_img = image[y1:y2, x1:x2]
    cropped_mask = mask[y1:y2, x1:x2]

    h_c, w_c = cropped_img.shape[:2]
    pad_top = (out_size - h_c) // 2
    pad_bottom = out_size - h_c - pad_top
    pad_left = (out_size - w_c) // 2
    pad_right = out_size - w_c - pad_left

    padded_img = cv2.copyMakeBorder(cropped_img, pad_top, pad_bottom, pad_left, pad_right,
                                    cv2.BORDER_CONSTANT, value=0)
    padded_mask = cv2.copyMakeBorder(cropped_mask, pad_top, pad_bottom, pad_left, pad_right,
                                     cv2.BORDER_CONSTANT, value=0)
    return padded_img, padded_mask

# === 메인 루프 (train 데이터셋만 증강) ===
crop_sizes = [300, 400, 500]
total_saved = 0

for fname in os.listdir(img_dir):
    if not fname.lower().endswith((".jpg", ".png", ".bmp")):
        continue

    img_path = os.path.join(img_dir, fname)
    mask_path = os.path.join(mask_dir, Path(fname).stem + ".bmp")

    img = cv2.imread(img_path)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

    if img is None or mask is None:
        print(f"[WARN] 이미지나 마스크를 못 읽음: {fname}")
        continue

    base_name = Path(fname).stem

    # === (0) 원본 그대로 저장 ===
    cv2.imwrite(os.path.join(out_img_dir, f"{base_name}_orig.png"), img)
    cv2.imwrite(os.path.join(out_mask_dir, f"{base_name}_orig.png"), mask)
    total_saved += 1

    # === (A) 원본 증강 ===
    variants = [("orig", img, mask)]
    flipped = flip(image=img, mask=mask)
    variants.append(("flip", flipped["image"], flipped["mask"]))

    for flip_tag, f_img, f_mask in variants:
        for angle in angles:
            h, w = f_img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            r_img = cv2.warpAffine(f_img, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=0)
            r_mask = rotate_mask_cubic(f_mask, angle)

            for g_tag, g_val in gammas:
                g_img = gamma_correction(r_img, g_val)
                g_mask = r_mask.copy()

                out_name = f"{base_name}_full_{flip_tag}_r{angle}_{g_tag}.png"
                cv2.imwrite(os.path.join(out_img_dir, out_name), g_img)
                cv2.imwrite(os.path.join(out_mask_dir, out_name), g_mask)
                total_saved += 1

    # === (B) 클리핑 증강 ===
    for ci, c_size in enumerate(crop_sizes):
        c_img, c_mask = center_crop_pad(img, mask, crop_size=c_size, out_size=512)

        variants = [("orig", c_img, c_mask)]
        flipped = flip(image=c_img, mask=c_mask)
        variants.append(("flip", flipped["image"], flipped["mask"]))

        for flip_tag, f_img, f_mask in variants:
            for angle in angles:
                h, w = f_img.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                r_img = cv2.warpAffine(f_img, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=0)
                r_mask = rotate_mask_cubic(f_mask, angle)

                for g_tag, g_val in gammas:
                    g_img = gamma_correction(r_img, g_val)
                    g_mask = r_mask.copy()

                    out_name = f"{base_name}_crop{ci}_{flip_tag}_r{angle}_{g_tag}.png"
                    cv2.imwrite(os.path.join(out_img_dir, out_name), g_img)
                    cv2.imwrite(os.path.join(out_mask_dir, out_name), g_mask)
                    total_saved += 1

print(f"\n[RESULT] 총 저장된 이미지 수: {total_saved}")