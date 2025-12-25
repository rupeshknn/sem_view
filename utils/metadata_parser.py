import tifffile

def get_pixel_scale(file_path):
    """
    Extracts pixel scale from a TIFF file.
    Returns scale in meters per pixel.
    """
    try:
        with tifffile.TiffFile(file_path) as tif:
            page = tif.pages[0]
            
            # Check for Zeiss metadata (Tag 34118)
            if 34118 in page.tags:
                data = page.tags[34118].value
                if isinstance(data, dict):
                    # Look for ap_image_pixel_size
                    if 'ap_image_pixel_size' in data:
                        # Value is typically a tuple like ('Pixel Size', 3.166, 'nm')
                        # Or sometimes just a float if we are lucky, but based on analysis it's a tuple
                        val = data['ap_image_pixel_size']
                        if isinstance(val, tuple) and len(val) >= 3:
                            value = float(val[1])
                            unit = val[2]
                            
                            if unit == 'nm':
                                return value * 1e-9
                            elif unit == 'um' or unit == 'µm':
                                return value * 1e-6
                            elif unit == 'mm':
                                return value * 1e-3
                            elif unit == 'm':
                                return value
                            
                    # Fallback to dp_pixel_size if available
                    if 'dp_pixel_size' in data:
                         val = data['dp_pixel_size']
                         # Assuming similar structure
                         if isinstance(val, tuple) and len(val) >= 3:
                            value = float(val[1])
                            unit = val[2]
                            if unit == 'nm': return value * 1e-9
                            elif unit == 'um' or unit == 'µm': return value * 1e-6
                            
            # Check standard XResolution (Tag 282)
            # This is often in pixels per unit, not size per pixel
            # And unit is defined in ResolutionUnit (Tag 296)
            # But SEMs often don't set this correctly or use it for print size (DPI)
            # So we prioritize proprietary tags.
            
    except Exception as e:
        print(f"Error parsing metadata: {e}")
        
    return None
