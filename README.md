# Ponds_and_wells_detection

This project detects wells and ponds (dry and wet) within a specified geographic region using satellite imagery tiles and a YOLO-based object detection model. It processes images, extracts polygons of detected ponds, filters based on entropy (for wet ponds), converts pixel coordinates to geospatial coordinates, and generates a combined shapefile of all detected ponds.

## Table of Contents
- Overview
- Dependencies
- Folder Structure
- Workflow
- Usage Instructions
- Output
- Notes

## Overview
- Input: GeoJSON file of the target region (Masalia_mws.geojson)
- Process:
    Download satellite image tiles for the region using tile coordinates.
    Detect ponds (Dry/Wet) using a pre-trained YOLO model.
    Compute entropy to filter out noisy wet pond detections.
    Store polygon masks and geospatial data into a CSV file.
    Convert polygons to GeoJSON and combine overlapping geometries.
    Export the final combined geometry as a shapefile and ZIP it.


## Dependencies
Ensure the following Python packages are installed:
        pip install numpy pandas geopandas opencv-python pillow requests matplotlib shapely ultralytics scikit-image

- YOLOv11 model via Ultralytics
- Shapely, GeoPandas for geospatial operations
- OpenCV, scikit-image for image processing
- requests for downloading map tiles

## Folder Structure
- Data/Zoom17/Masalia/           # Image tiles (downloaded here)
- Shapefiles/Masalia_mws.geojson # Input GeoJSON boundary
- CSV_Output/Masalia_Ponds.csv   # Output CSV with pond data
- Shapefile_Output/              # Output shapefile ZIPs
- Ponds_best.pt                  # Pre-trained YOLO model


## Workflow
1. Download Map Tiles
- Converts bounding box of GeoJSON to tile numbers.
- Downloads tiles from Google Maps (satellite imagery) at zoom level 17.

2. YOLO Inference
- Runs object detection using Ponds_best.pt.
- Filters detections using confidence thresholds.
- For wet ponds, calculates entropy to ensure detection validity.

3. Polygon Conversion
- Extracts polygon mask coordinates.
- Converts pixel coordinates to latitude/longitude using tile geo-boundaries.

4. CSV Generation
- Stores polygon data, class labels, entropy, tile locations into a CSV.

5. GeoJSON and Shapefile Creation
- Converts polygons to GeoJSON features.
- Merges overlapping geometries using buffer-union-buffer method.
- Exports as shapefile and compresses it into a ZIP file.

## Usage Instructions
1. Set Paths and Parameters
- Modify the following in the script as needed:
    model_path, csv_file, image_dir, zoom_level, scale, entropy_threshold

2. Run the Script
- Execute the full script in your Python environment.

3. Output Files
- Processed CSV at: CSV_Output/Masalia_Ponds.csv
- Final shapefile ZIP at: Shapefile_Output/Masalia_Ponds_COMBINED_GEOMETRY.zip

## Output
- CSV File: Contains wells and pond classification (Dry/Wet), polygon coordinates, entropy values, tile locations.
- Shapefile (Zipped): Combined geometries of all detected ponds and wells in EPSG:4326.

## Notes
- Entropy is only computed for wet ponds to filter out noisy detections.
- Tile scale of 1 results in 256x256 pixel images.
- Merging buffer distance can be adjusted (0.0005) for sensitivity.

## Overall Workflow
![ponds drawio (1)](https://github.com/user-attachments/assets/d1ef93b5-d9c1-4398-bdd8-daaffdb72c09)

