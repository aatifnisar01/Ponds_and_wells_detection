# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 13:02:04 2025

@author: Aatif
"""


import os
import random
import cv2
import numpy as np

# Paths
negative_folder = r"C:\Users\Aatif\Downloads\Plantation_Detection_2.0\Negative Samples"
annotated_images_folder = r"C:\Users\Aatif\Downloads\Plantation_Detection_2.0\Annotated_data\train\images"
annotated_labels_folder = r"C:\Users\Aatif\Downloads\Plantation_Detection_2.0\Annotated_data\train\labels"
output_images_folder = r"C:\Users\Aatif\Downloads\Plantation_Detection_2.0\cutmix_folder\images"
output_labels_folder = r"C:\Users\Aatif\Downloads\Plantation_Detection_2.0\cutmix_folder\labels"

os.makedirs(output_images_folder, exist_ok=True)
os.makedirs(output_labels_folder, exist_ok=True)

negative_images = [f for f in os.listdir(negative_folder) if f.endswith('.png') or f.endswith('.jpg')]
annotated_images = [f for f in os.listdir(annotated_images_folder) if f.endswith('.jpg') or f.endswith('.png')]

def parse_first_polygon(label_line):
    parts = label_line.strip().split()
    cls_id = int(parts[0])
    coords = list(map(float, parts[1:]))

    polygon = []
    for i in range(0, len(coords) - 1, 2):
        x, y = coords[i], coords[i + 1]
        if x == 1.0 and y == 1.0:
            break
        polygon.append((x, y))
    return cls_id, polygon

def polygon_to_mask(polygon, width, height):
    pts = np.array([[int(x * width), int(y * height)] for x, y in polygon], dtype=np.int32)
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(mask, [pts], 255)
    return mask, pts

def translate_polygon_pixel(polygon, orig_w, orig_h, dx, dy, new_w, new_h):
    translated = []
    for x, y in polygon:
        abs_x = x * orig_w + dx
        abs_y = y * orig_h + dy
        norm_x = abs_x / new_w
        norm_y = abs_y / new_h
        translated.append((norm_x, norm_y))
    return translated

def polygon_to_label_string(cls_id, polygon):
    return f"{cls_id} " + " ".join(f"{x:.6f} {y:.6f}" for x, y in polygon)

# Main loop: repeat each negative image twice
for neg_img_name in negative_images:
    for copy_index in [1, 2]:
        neg_img_path = os.path.join(negative_folder, neg_img_name)
        neg_img_orig = cv2.imread(neg_img_path)
        if neg_img_orig is None:
            continue

        img_h, img_w = neg_img_orig.shape[:2]
        all_labels = []
        neg_img = neg_img_orig.copy()

        random.shuffle(annotated_images)  # randomize

        for ann_img_name in annotated_images:
            ann_lbl_name = os.path.splitext(ann_img_name)[0] + '.txt'
            ann_img_path = os.path.join(annotated_images_folder, ann_img_name)
            ann_lbl_path = os.path.join(annotated_labels_folder, ann_lbl_name)

            ann_img = cv2.imread(ann_img_path)
            if ann_img is None:
                continue
            ann_h, ann_w = ann_img.shape[:2]

            try:
                with open(ann_lbl_path, 'r') as f:
                    lines = f.readlines()
            except:
                continue

            random.shuffle(lines)  # shuffle polygons

            for line in lines:
                try:
                    cls_id, polygon = parse_first_polygon(line)
                    if len(polygon) < 3:
                        continue

                    mask, polygon_pts = polygon_to_mask(polygon, ann_w, ann_h)
                    object_region = cv2.bitwise_and(ann_img, ann_img, mask=mask)

                    x, y, w, h = cv2.boundingRect(polygon_pts)
                    x_end = min(x + w, ann_w)
                    y_end = min(y + h, ann_h)
                    x = max(x, 0)
                    y = max(y, 0)
                    w = x_end - x
                    h = y_end - y

                    if w <= 1 or h <= 1 or w >= img_w or h >= img_h:
                        continue

                    crop = object_region[y:y+h, x:x+w]
                    mask_crop = mask[y:y+h, x:x+w]

                    paste_x = random.randint(0, img_w - w)
                    paste_y = random.randint(0, img_h - h)
                    roi = neg_img[paste_y:paste_y+h, paste_x:paste_x+w]

                    if len(mask_crop.shape) != 2:
                        mask_crop = cv2.cvtColor(mask_crop, cv2.COLOR_BGR2GRAY)
                    mask_crop = mask_crop.astype(np.uint8)
                    if mask_crop.shape[:2] != roi.shape[:2]:
                        continue

                    inverse_mask = cv2.bitwise_not(mask_crop)
                    bg = cv2.bitwise_and(roi, roi, mask=inverse_mask)
                    fg = cv2.bitwise_and(crop, crop, mask=mask_crop)
                    combined = cv2.add(bg, fg)
                    neg_img[paste_y:paste_y+h, paste_x:paste_x+w] = combined

                    dx = paste_x - x
                    dy = paste_y - y
                    translated_polygon = translate_polygon_pixel(polygon, ann_w, ann_h, dx, dy, img_w, img_h)
                    label_str = polygon_to_label_string(cls_id, translated_polygon)
                    all_labels.append(label_str)
                    break  # ✅ one polygon per image

                except Exception as e:
                    print(f"⚠️ Skipping polygon in {ann_lbl_name}: {e}")
                    continue

            if all_labels:
                break  # ✅ one annotation per image

        if all_labels:
            out_img_name = os.path.splitext(neg_img_name)[0] + f'_{copy_index}.jpg'
            out_img_path = os.path.join(output_images_folder, out_img_name)
            cv2.imwrite(out_img_path, neg_img)

            out_lbl_name = os.path.splitext(out_img_name)[0] + '.txt'
            out_lbl_path = os.path.join(output_labels_folder, out_lbl_name)
            with open(out_lbl_path, 'w') as f:
                for lbl in all_labels:
                    f.write(lbl + '\n')
        else:
            print(f"⚠️ Skipped: {neg_img_name}_{copy_index} (no valid object found)")

print("✅ All 200 CutMix images with single polygon annotations generated.") 







#################################################

import matplotlib.pyplot as plt

annotation_file_path = "C:/Users/Aatif/Downloads/Plantation_Detection_2.0/cutmix_folder/labels/tile_17_92126_56238_1.txt"
#annotation_file_path = os.path.join(pwd, annotation_file_path)
image_file_path = "C:/Users/Aatif/Downloads/Plantation_Detection_2.0/cutmix_folder/images/tile_17_92126_56238_1.jpg"
#image_file_path = os.path.join(pwd, image_file_path)

# Check if the files exist
if not os.path.exists(image_file_path):
    raise FileNotFoundError(f"Image file not found: {image_file_path}")
if not os.path.exists(annotation_file_path):
    raise FileNotFoundError(f"Annotation file not found: {annotation_file_path}")

# Read the image
image = cv2.imread(image_file_path)
if image is None:
    raise ValueError(f"Failed to read image from file: {image_file_path}")
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Get the image dimensions
image_height, image_width = image.shape[:2]

# Read the annotation file
with open(annotation_file_path, 'r') as f:
    annotations = f.readlines()

# Define a function to draw polygons on the image
def draw_polygons(image, annotations, img_width, img_height):
    for annotation in annotations:
        parts = annotation.strip().split()
        class_index = int(parts[0])
        points = list(map(float, parts[1:]))
        # Scale the normalized coordinates to the image dimensions
        scaled_points = [int(points[i] * img_width if i % 2 == 0 else points[i] * img_height) for i in range(len(points))]
        # Create a list of (x, y) tuples
        polygon = [(scaled_points[i], scaled_points[i+1]) for i in range(0, len(scaled_points), 2)]
        polygon = np.array(polygon, np.int32)
        polygon = polygon.reshape((-1, 1, 2))
        # Draw the polygon on the image
        cv2.polylines(image, [polygon], isClosed=True, color=(0, 255, 0), thickness=2)
    return image

# Draw the annotations on the image
image_with_annotations = draw_polygons(image, annotations, image_width, image_height)

# Display the image with annotations
plt.figure(figsize=(10, 10))
plt.imshow(image_with_annotations)
plt.axis('off')
plt.show()