import geopandas as gpd
import pandas as pd



def process_water_bodies(ponds_path, swb_path, output_ponds_path, output_swb_path, output_combined_path, threshold=0.5):
    # Load the GeoJSON files
    ponds = gpd.read_file(ponds_path)
    swb = gpd.read_file(swb_path)
    
    # Make sure they have the same CRS
    ponds = ponds.to_crs(swb.crs)
    
    # Create copies for modification
    ponds_to_keep = ponds.copy()
    swb_to_keep = swb.copy()
    
    # Spatial index for faster queries
    ponds_sindex = ponds.sindex
    swb_sindex = swb.sindex
    
    # Lists to store indices of features to remove
    ponds_to_remove = set()
    swb_to_remove = set()
    
    # Check ponds against SWBs
    for pond_idx, pond in ponds.iterrows():
        pond_area = pond.geometry.area
        possible_matches_index = list(swb_sindex.intersection(pond.geometry.bounds))
        
        for swb_idx in possible_matches_index:
            swb_feature = swb.iloc[swb_idx]
            intersection = pond.geometry.intersection(swb_feature.geometry)
            
            if not intersection.is_empty:
                aoi = intersection.area / min(pond.geometry.area, swb_feature.geometry.area)
                
                if aoi > threshold:
                    # Determine which one is larger
                    if pond.geometry.area >= swb_feature.geometry.area:
                        swb_to_remove.add(swb_idx)
                    else:
                        ponds_to_remove.add(pond_idx)
    
    # Remove the identified features
    ponds_to_keep = ponds_to_keep.drop(index=list(ponds_to_remove))
    swb_to_keep = swb_to_keep.drop(index=list(swb_to_remove))
    
    # Add source type column
    ponds_to_keep['waterbody_type'] = 'pond'
    swb_to_keep['waterbody_type'] = 'swb'
    
    # Combine the processed datasets
    combined = gpd.GeoDataFrame(pd.concat([ponds_to_keep, swb_to_keep], ignore_index=True), crs=ponds_to_keep.crs)
    
    # Save all files
    ponds_to_keep.to_file(output_ponds_path, driver='GeoJSON')
    swb_to_keep.to_file(output_swb_path, driver='GeoJSON')
    combined.to_file(output_combined_path, driver='GeoJSON')
    
    print(f"Processing complete. Removed {len(ponds_to_remove)} ponds and {len(swb_to_remove)} SWBs.")
    print(f"Combined file created with {len(combined)} water bodies.")

# Usage
ponds_path = 'C:/Users/Aatif/Downloads/Masalia_Ponds.geojson'
swb_path = 'C:/Users/Aatif/Downloads/Masalia_SWB.geojson'
output_ponds_path = 'C:/Users/Aatif/Downloads/Masalia_Ponds_processed.geojson'
output_swb_path = 'C:/Users/Aatif/Downloads/Masalia_SWB_processed.geojson'
output_combined_path = 'C:/Users/Aatif/Downloads/Masalia_WaterBodies_Combined.geojson'

process_water_bodies(ponds_path, swb_path, output_ponds_path, output_swb_path, output_combined_path)