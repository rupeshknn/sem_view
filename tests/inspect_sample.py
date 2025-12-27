import tifffile
import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

file_path = os.path.abspath("temp_scripts/sample_roi.tif")

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
else:
    with tifffile.TiffFile(file_path) as tif:
        page = tif.pages[0]
        print(f"Image Shape: {page.shape}")
        print(f"Image Dtype: {page.dtype}")
        
        # Check for ImageDescription (Tag 270)
        if 270 in page.tags:
            desc = page.tags[270].value
            print("\nImage Description found:")
            try:
                data = json.loads(desc)
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                print(desc)
        else:
            print("\nNo Image Description (Tag 270) found.")
