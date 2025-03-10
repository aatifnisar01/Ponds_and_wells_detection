# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 14:17:08 2025

@author: Aatif
"""

def pixel_to_geo(x, y, lat_top_left, lon_top_left, lat_bottom_right, lon_bottom_right, img_width, img_height):
    """
    Convert pixel coordinates to geographic coordinates (latitude, longitude).

    Parameters:
    - x, y: Pixel coordinates in the image.
    - lat_top_left, lon_top_left: Latitude and longitude of the top-left corner of the image.
    - lat_bottom_right, lon_bottom_right: Latitude and longitude of the bottom-right corner.
    - img_width, img_height: Dimensions of the image.

    Returns:
    - Tuple: (longitude, latitude) corresponding to the pixel location.
    """
    lon_range = lon_bottom_right - lon_top_left
    lat_range = lat_top_left - lat_bottom_right  # Latitude decreases southward
    lon = lon_top_left + (x / img_width) * lon_range
    lat = lat_top_left - (y / img_height) * lat_range
    return lon, lat
