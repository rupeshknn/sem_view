"""
Image analysis utilities for SEM Viewer.
"""

import numpy as np
from skimage.draw import polygon
from skimage.filters import threshold_otsu, threshold_local
from skimage.measure import find_contours
from skimage.morphology import closing, disk, opening
from skimage.util import img_as_ubyte


def find_overlap_area(image_data, polygon_points=None, seed_point=None, mask=None):
    """
    Finds the overlap area within a user-defined polygon or mask.

    Args:
        image_data (np.ndarray): The image data (grayscale).
        polygon_points (list of tuple, optional): List of (x, y) points defining the rough ROI.
        seed_point (tuple, optional): (x, y) point to help guide segmentation (unused for now).
        mask (np.ndarray, optional): Boolean mask defining the ROI. Overrides polygon_points.

    Returns:
        list of tuple: List of (x, y) points defining the detected overlap polygon.
    """
    if image_data is None:
        return []

    if mask is None and (polygon_points is None or len(polygon_points) < 3):
        return []

    # Handle RGB
    if image_data.ndim == 3 and image_data.shape[2] in (3, 4):
        # Simple RGB to Grayscale: 0.299 R + 0.587 G + 0.114 B
        # Or just use mean for simplicity in this context
        image_gray = np.mean(image_data[:, :, :3], axis=2).astype(image_data.dtype)
    else:
        image_gray = image_data

    height, width = image_gray.shape[:2]

    # Create a mask from the user polygon if not provided
    if mask is None:
        # skimage.draw.polygon uses (row, col) -> (y, x)
        poly_y = [p[1] for p in polygon_points]
        poly_x = [p[0] for p in polygon_points]

        rr, cc = polygon(poly_y, poly_x, shape=(height, width))
        mask = np.zeros((height, width), dtype=bool)
        mask[rr, cc] = True

    # Extract ROI
    roi = image_gray.copy()
    # We only care about the area inside the mask.
    # Let's set outside to 0 (or mean) to avoid affecting threshold too much,
    # but Otsu on masked array is better.

    roi_values = roi[mask]

    if len(roi_values) == 0:
        return []

    # Otsu thresholding on the ROI pixels
    try:
        thresh = threshold_otsu(roi_values)
    except Exception:
        # Fallback if ROI is uniform
        thresh = roi_values.mean()

    # Create binary mask of the overlap (assuming overlap is brighter)
    # If overlap is darker, we might need to invert or check mean intensities.
    # Usually metal on substrate is brighter in SEM.
    binary_mask = (roi > thresh) & mask

    # Clean up the mask
    # Closing to fill small holes, Opening to remove noise
    binary_mask = closing(binary_mask, disk(3))
    binary_mask = opening(binary_mask, disk(2))

    # Find contours
    contours = find_contours(binary_mask, 0.5)

    if not contours:
        return []

    # Find the largest contour by length (approximation for area)
    largest_contour = max(contours, key=len)

    # Convert back to (x, y) list
    # contours are (row, col) -> (y, x)
    result_polygon = [(pt[1], pt[0]) for pt in largest_contour]

    # Simplify polygon slightly to reduce point count if needed?
    # For now, return "large n polygon" as requested.

    return result_polygon
