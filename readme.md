# GeoJSON Purge 🌍🧹

GeoJSON Purge is to clean GeoJSON files. Developed for the internal use of studio [Platvorm](https://platvorm.ee/).

## Overview

GeoJSON Purge is a command-line Python tool that:

* Merges feature geometries by layer: Polygons into MultiPolygons, LineStrings into MultiLineString, and Points into MultiPoints.
* Removes selected properties
* Removes Z-coordinates
* Truncates coordinate precision

It guides you via prompts to select which operations to perform. The script then outputs a cleaned, optimized GeoJSON file.

## Installation

1. Clone or download the repository from GitHub.
2. In a terminal (or command prompt), navigate to the project directory:

	```bash
	cd path/to/geojson-purge
	```

3. (Optional) Create and activate a virtual environment:

	```bash
	python -m venv venv
	source venv/bin/activate  # On macOS/Linux
	venv\Scripts\activate     # On Windows
	```

4. Install dependencies from requirements.txt:

	```bash
	pip install -r requirements.txt
	```

## Usage

1. Run the script from the command line:

	```bash
	python geojson-purge.py
	```

2. You will be prompted for the path to your GeoJSON file. Type or paste the full path to your .geojson file (e.g., my_data.geojson).

3. You will see a checkbox list of operations:

	* Merge layers
	* Delete properties
	* Remove Z-coordinate
	* Truncate coordinates

	Use the arrow keys to select/deselect the operations you want to perform; press Enter to confirm.

4. Merging layers (if selected)
	If you choose to merge layers, the tool will list distinct layers found in Layer property, then ask which ones to merge/dissolve together.

5. Deleting properties (if selected)

	* The script will list all available properties and their example values.
	* Check the ones you want to remove, then press Enter.

6. Removing Z-coordinate (if selected)

	* If selected, the script automatically strips out any Z (third dimension) from all geometries.

7. Truncating coordinates (if selected)

	* The script will ask for a number of decimal places to keep (default is 7).
	* All coordinates are rounded to that precision.

8. Output

	* Once all operations are completed, the tool saves your cleaned dataset to a new file called `originalfilename-processed.geojson` in the same directory as the original.

## Troubleshooting & Tips

* No layers to merge? If your file has no "Layer" property, the merge step is skipped.
* No properties listed? Make sure your GeoJSON data is valid and actually contains feature properties.
* For very large GeoJSON files, processing time can be longer, especially for layer dissolves.

---
Inspired by [geojson-shave](https://github.com/ben-nour/geojson-shave)