# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 14:16:26 2025

@author: Aatif
"""

import os
import math
import cv2
import numpy as np
from entropy_calculator import get_entropy  # Importing from entropy module

def process_image(image_path, conf_thresholds, model, class_names):
    """
    Process an image using a given model, extract polygons, classes, confidence scores, and entropy for 'Wet' class.

    Parameters:
    - image_path: Path to the image file.
    - conf_thresholds: Dictionary mapping class names to confidence thresholds.
    - model: The trained model for prediction.
    - class_names: List of class names corresponding to model output classes.

    Returns:
    - Tuple: (image_path, number of polygons, list of polygons, list of predicted classes, confidence scores, entropy values)
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Unable to load image {image_path}")
        return None, None, None, None, None

    results = model.predict(img)

    polygons = []
    pred_classes = []
    conf_scores = []
    entropies = []

    if results[0].masks is not None:
        for i, (polygon, cls, conf) in enumerate(zip(results[0].masks.xy, results[0].boxes.cls.cpu().numpy(), results[0].boxes.conf.cpu().numpy())):
            class_name = class_names[int(cls)]
            if conf >= conf_thresholds[class_name]:
                polygons.append(polygon)
                pred_classes.append(class_name)
                conf_scores.append(conf)

                if class_name == 'Wet':  # Only compute entropy for 'Wet' class
                    predicted_mask = results[0].masks.data.cpu().numpy()[i].astype(np.uint8)  # Convert to uint8
                    entropy_value = get_entropy(img, predicted_mask)  # Calculate entropy for the masked region
                    entropies.append(entropy_value)
                    print(f"Entropy for {class_name}: {entropy_value:.2f}")
                else:
                    entropies.append(None)  # Skip entropy calculation for other classes

    return image_path, len(polygons), polygons, pred_classes, conf_scores, entropies


def extract_xtile_ytile(image_path):
    """
    Extract tile coordinates (xtile, ytile) from the image filename.

    Parameters:
    - image_path: Path to the image file.

    Returns:
    - Tuple: (xtile, ytile)
    """
    try:
        basename = os.path.basename(image_path)
        parts = basename.split('_')
        if len(parts) >= 4:
            xtile = int(parts[2])
            ytile = int(parts[3].split('.')[0].split()[0])
            return xtile, ytile
        else:
            raise ValueError("Filename does not contain valid tile coordinates")
    except Exception as e:
        raise ValueError(f"Filename {image_path} does not contain valid tile coordinates: {e}")


def tile_corners_to_latlon(xtile, ytile, zoom):
    """
    Convert tile coordinates to latitude and longitude of tile corners.

    Parameters:
    - xtile, ytile: Tile coordinates.
    - zoom: Zoom level.

    Returns:
    - Tuple: (top_left, top_right, bottom_left, bottom_right) in (lat, lon) format.
    """
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad_nw = math.atan(math.sinh(math.pi * (1 - 2 * (ytile / n))))
    lat_deg_nw = math.degrees(lat_rad_nw)

    lat_rad_se = math.atan(math.sinh(math.pi * (1 - 2 * ((ytile + 1) / n))))
    lat_deg_se = math.degrees(lat_rad_se)

    # Limit latitude to avoid errors at extreme values
    lat_deg_nw = max(min(lat_deg_nw, 85.0511), -85.0511)
    lat_deg_se = max(min(lat_deg_se, 85.0511), -85.0511)

    top_left = (lat_deg_nw, lon_deg)
    top_right = (lat_deg_nw, lon_deg + (360.0 / n))
    bottom_right = (lat_deg_se, lon_deg + (360.0 / n))
    bottom_left = (lat_deg_se, lon_deg)

    return top_left, top_right, bottom_left, bottom_right


def calculate_tile_center(top_left, top_right, bottom_left, bottom_right):
    """
    Calculate the center latitude and longitude of a tile.

    Parameters:
    - top_left, top_right, bottom_left, bottom_right: Tile corner coordinates in (lat, lon) format.

    Returns:
    - Tuple: (center_lat, center_lon)
    """
    center_lat = (top_left[0] + bottom_left[0]) / 2
    center_lon = (top_left[1] + top_right[1]) / 2
    return (center_lat, center_lon)
