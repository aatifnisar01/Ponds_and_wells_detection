# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 13:31:23 2025

@author: Aatif
"""

import os
import requests
import time
import math

# URL for Google map tiles (satellite imagery)
base_url = "https://mt1.google.com/vt/lyrs=s"
zoom_level = 17  # Set the zoom level

# Specify the folder where you want to save the downloaded tiles
output_folder = "C:/Users/Aatif/Downloads/Plantation_Detection_2.0/Negative Samples"



# Function to download a specific map tile based on x and y coordinates
def download_map_tile(base_url, output_folder, zoom_level, x_tile, y_tile):
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Get start time
    start_time = time.time()

    # Construct the URL for the current tile
    tile_url = f"{base_url}&x={x_tile}&y={y_tile}&z={zoom_level}"
    print(tile_url)

    try:
        # Send HTTP GET request to fetch the tile
        response = requests.get(tile_url)

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            # Save the tile image to a file in the output folder
            filename = f"tile_{zoom_level}_{x_tile}_{y_tile}.png"
            filepath = os.path.join(output_folder, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download tile ({x_tile}, {y_tile}), HTTP status code: {response.status_code}")

    except Exception as e:
        print(f"Error downloading tile ({x_tile}, {y_tile}): {e}")

    # Get end time
    end_time = time.time()

    # Print the total execution time
    print(f"Total time taken: {end_time - start_time} seconds")



def lat_lon_to_tile(lat, lon, zoom):
    lat = max(min(lat, 85.05112878), -85.05112878)

    # Calculate x tile
    x_tile = int((lon + 180.0) / 360.0 * 2 ** zoom)

    # Calculate y tile
    lat_rad = math.radians(lat)
    y_tile = int((1.0 - (math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi)) / 2.0 * 2 ** zoom)

    return x_tile, y_tile


latitude, longitude = 24.4883792,72.7644233

x_tile, y_tile = lat_lon_to_tile(latitude, longitude, zoom_level)
print(f"Latitude: {latitude}, Longitude: {longitude}, Zoom: {zoom_level} -> X Tile: {x_tile}, Y Tile: {y_tile}")



x_tile = x_tile  
y_tile = y_tile 



# Download the specific tile
download_map_tile(base_url, output_folder, zoom_level, x_tile, y_tile)