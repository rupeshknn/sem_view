import sys
import os
import numpy as np
import tifffile
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sem_view.utils.analysis import find_overlap_area


def test_sample_roi():
    file_path = os.path.abspath("temp_scripts/sample_roi.tif")
    if not os.path.exists(file_path):
        print(f"Sample file not found: {file_path}")
        return

    print(f"Loading {file_path}...")
    with tifffile.TiffFile(file_path) as tif:
        image_data = tif.pages[0].asarray()

        # Extract polygon from metadata
        page = tif.pages[0]
        user_poly = []
        if 270 in page.tags:
            desc = page.tags[270].value
            try:
                data = json.loads(desc)
                if "annotations" in data:
                    for ann in data["annotations"]:
                        if ann["type"] == "area":
                            user_poly = ann["points"]
                            break
            except Exception as e:
                print(f"Error parsing metadata: {e}")

    if not user_poly:
        print("No polygon found in metadata.")
        return

    print(f"User Polygon Points: {len(user_poly)}")

    print("Running find_overlap_area...")
    result = find_overlap_area(image_data, user_poly)

    if not result:
        print("FAIL: No overlap detected.")
        return

    print(f"Success! Detected polygon with {len(result)} points.")

    # Calculate area of result to compare with rough polygon
    # (Simple Shoelace formula)
    def polygon_area(points):
        area = 0.0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        return abs(area) / 2.0

    user_area = polygon_area(user_poly)
    result_area = polygon_area(result)

    print(f"User Area: {user_area:.2f} px²")
    print(f"Result Area: {result_area:.2f} px²")

    # Result area should be smaller than user area (subset) but significant
    if 0 < result_area < user_area:
        print("PASS: Result area is a valid subset of user area.")
    else:
        print("WARN: Result area seems odd.")

    # Save result
    output_path = os.path.abspath("temp_scripts/sample_roi_result.tif")
    print(f"Saving result to {output_path}...")

    description = {
        "description": "Auto Area Analysis Result",
        "measurements": [
            {
                "type": "Area",
                "value": f"{result_area:.2f}",
                "unit": "px²",
                "label": f"{result_area:.0f} px²",
                "color": "#00FF00",
            }
        ],
        "is_burnt_in": False,
        "annotations": [
            # Original User Polygon (Yellow)
            {"type": "area", "points": user_poly, "color": "#FFFF00"},
            # Result Polygon (Green)
            {"type": "area", "points": result, "color": "#00FF00"},
        ],
    }

    with tifffile.TiffWriter(output_path) as tif:
        tif.write(image_data, photometric="rgb", description=json.dumps(description))
    print("Done.")


if __name__ == "__main__":
    test_sample_roi()
