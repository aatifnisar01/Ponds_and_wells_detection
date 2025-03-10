# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 13:57:04 2025

@author: Aatif
"""

import os
import math
import time
import requests

# Helper function to convert latitude and longitude to tile numbers
def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

# Function to download map tiles
def download_map_tiles(base_url, image_dir, zoom_level, scale, topLeft, topRight, bottomLeft, bottomRight):
    # Ensure output folder exists
    os.makedirs(image_dir, exist_ok=True)

    # Convert lat/lon to tile numbers and get bounding box
    topleft = deg2num(topLeft[1], topLeft[0], zoom_level)
    topright = deg2num(topRight[1], topRight[0], zoom_level)
    bottomleft = deg2num(bottomLeft[1], bottomLeft[0], zoom_level)
    bottomright = deg2num(bottomRight[1], bottomRight[0], zoom_level)
    
    xmin = min(topleft[0], topright[0], bottomleft[0], bottomright[0])
    xmax = max(topleft[0], topright[0], bottomleft[0], bottomright[0])
    ymin = min(topleft[1], topright[1], bottomleft[1], bottomright[1])
    ymax = max(topleft[1], topright[1], bottomleft[1], bottomright[1])

    # Get start time
    start_time = time.time()

    # Iterate over each tile within the specified range
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            # Construct the URL for the current tile
            tile_url = f"{base_url}&x={x}&y={y}&z={zoom_level}&scale={scale}"
            print(tile_url)
            try:
                # Send HTTP GET request to fetch the tile
                response = requests.get(tile_url)

                # Check if request was successful (status code 200)
                if response.status_code == 200:
                    # Save the tile image to a file in the output folder
                    filename = f"tile_{zoom_level}_{x}_{y}.png"
                    filepath = os.path.join(image_dir, filename)
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    print(f"Downloaded: {filename}")
                else:
                    print(f"Failed to download tile ({x}, {y}), HTTP status code: {response.status_code}")

            except Exception as e:
                print(f"Error downloading tile ({x}, {y}): {e}")

    # Get end time
    end_time = time.time()

    # Print the total execution time
    print(f"Total time taken: {end_time - start_time} seconds")
