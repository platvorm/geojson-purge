#!/usr/bin/env python3

import os
import json
import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union
import shapely
import questionary
from tqdm import tqdm
import humanize

# List layers in the GeoJSON data
def list_layers(geojson_data):
    layer_counts = {}
    for feature in tqdm(geojson_data.get('features', []), desc="Listing Layer values"):
        layer = feature.get('properties', {}).get('Layer')
        if layer:
            if layer in layer_counts:
                layer_counts[layer] += 1
            else:
                layer_counts[layer] = 1
    # Filter layers to include only those with 2 or more features
    layers = [layer for layer, count in layer_counts.items() if count >= 2]
    return layers

# Select layers to merge
def select_layers(layers):
    if not layers:
        print("No layers with 2 or more features found.")
        return []
    
    choices = [layer for layer in layers]
    
    selected_layers = questionary.checkbox(
        "Select layers to merge",
        choices=choices
    ).ask()
    
    return selected_layers

# Remove Z-coordinate from geometries
def remove_z_coordinate(geometry):
    if geometry.has_z:
        return shapely.ops.transform(lambda x, y, z=None: (x, y), geometry)
    return geometry

# Truncate coordinates to a specified number of decimal places
def truncate_coordinates(geometry, decimal_places):
    def truncate_coords(coords):
        return tuple(round(coord, decimal_places) for coord in coords if coord is not None)
    
    return shapely.ops.transform(lambda *args: truncate_coords(args), geometry)

# List properties in the GeoJSON data
def list_properties(geojson_data):
    properties = {}
    for feature in geojson_data.get('features', []):
        for prop, value in feature.get('properties', {}).items():
            if prop not in properties:
                properties[prop] = value
    return properties

# Select properties to delete
def select_properties(properties):
    choices = [
        f"{prop} (Example: {value})" for prop, value in properties.items()
    ]
    
    selected_properties = questionary.checkbox(
        "Select properties to delete",
        choices=choices
    ).ask()
    
    selected_properties = [
        item.split(' (Example: ')[0] for item in selected_properties
    ]
    
    return selected_properties

# Delete properties from GeoJSON data
def delete_properties(geojson_data, properties_to_delete):
    for feature in geojson_data.get('features', []):
        for prop in properties_to_delete:
            feature['properties'].pop(prop, None)
    return geojson_data

# Save GeoJSON data to a file
def save_geojson(geojson_data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=2)
    print(f"GeoJSON saved to {file_path}")

# Main function
def main():
    print("Usage: This script processes a GeoJSON file by optionally removing the z-coordinate, trimming coordinates to a specified number of decimal places, simplifying the geometries, and removing specified properties.")
    print("You will be prompted to enter the path to the input GeoJSON file and select the operations to perform.")
    print("The processed GeoJSON file will be saved with '-processed' appended to the original filename.")

    # Ask for the input file
    while True:
        input_file = questionary.text("Enter the path to the input GeoJSON file:").ask().strip()
        if os.path.isfile(input_file):
            break
        else:
            print(f"File not found: {input_file}. Please enter a valid file path.")

    # Generate the output filename
    output_file = os.path.splitext(input_file)[0] + "-processed.geojson"

    # Define the operations
    operations = [
        "Merge layers",
        "Delete properties",
        "Remove Z-coordinate",
        "Truncate coordinates"
    ]

    # Let the user select the operations
    selected_operations = questionary.checkbox(
        "Select operations to perform",
        choices=operations
    ).ask()

    # Load the GeoJSON data
    gdf = gpd.read_file(input_file)
    size_before = os.path.getsize(input_file)
    
    # Convert Timestamp values to strings
    gdf[gdf.columns.difference(['geometry'])] = gdf[gdf.columns.difference(['geometry'])].apply(
        lambda col: col.map(lambda x: x.isoformat() if isinstance(x, pd.Timestamp) else x)
    )

    # Possibly dissolve by Layer if "Merge layers" is selected
    if "Merge layers" in selected_operations:
        # If you need the layer names
        layers = list_layers(json.loads(gdf.to_json()))
        selected_layers = select_layers(layers)

        if selected_layers:
            # Filter by selected layers
            gdf_selected = gdf[gdf['Layer'].isin(selected_layers)]
            gdf_unselected = gdf[~gdf['Layer'].isin(selected_layers)]

            # Merge geometries
            gdf_merged = gdf_selected.dissolve(by="Layer").reset_index()

            # Combine merged and unmerged layers
            gdf = gpd.GeoDataFrame(pd.concat([gdf_merged, gdf_unselected], ignore_index=True))

    # Delete selected properties
    if "Delete properties" in selected_operations:
        # List and choose
        properties = list_properties(json.loads(gdf.to_json()))
        if properties:
            properties_to_delete = select_properties(properties)
            if properties_to_delete:
                # <-- Fix: drop columns from gdf, not from raw geojson_data
                gdf = gdf.drop(columns=properties_to_delete, errors='ignore')

    # Remove Z-coordinates
    if "Remove Z-coordinate" in selected_operations:
        gdf['geometry'] = gdf['geometry'].apply(remove_z_coordinate)

    # Truncate coordinates
    if "Truncate coordinates" in selected_operations:
        decimal_places = questionary.text("Enter number of decimal places:", default="7").ask()
        decimal_places = int(decimal_places)
        gdf['geometry'] = gdf['geometry'].apply(lambda geom: truncate_coordinates(geom, decimal_places))

    # Finally, save once
    if selected_operations:
        output_file = os.path.splitext(input_file)[0] + "-processed.geojson"
        gdf.to_file(output_file, driver="GeoJSON")
        size_after = os.path.getsize(output_file)
        difference = ((size_before - size_after) / size_before) * 100
        print(f"Processed file saved to {output_file}")
        print(f"Size before: {humanize.naturalsize(size_before)}")
        print(f"Size after:  {humanize.naturalsize(size_after)}")
        print(f"Reduction:   {difference:.2f}%")

if __name__ == "__main__":
    main()