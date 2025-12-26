import tifffile
import json

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

def get_metadata_context(file_path):
    """
    Extracts context metadata (Tool, Voltage, Mag, etc.) from a TIFF file.
    Returns a dictionary of key-value pairs.
    """
    context = {}
    try:
        with tifffile.TiffFile(file_path) as tif:
            page = tif.pages[0]
            if 34118 in page.tags:
                data = page.tags[34118].value
                if isinstance(data, dict):
                    # Helper to safely get value from tuple/list or direct value
                    def get_val(key):
                        if key in data:
                            val = data[key]
                            if isinstance(val, (list, tuple)) and len(val) > 1:
                                return val[1] # Usually ('Label', value, unit) or ('Label', value)
                            return val
                        return None

                    # Tool Name
                    context['Tool'] = get_val('sv_serial_number') or get_val('sv_instrument_id') or "Unknown"
                    
                    # Voltage (EHT)
                    eht = get_val('ap_actualkv') or get_val('ap_eht') or get_val('ap_voltage') or get_val('ap_highvoltage')
                    if eht:
                        context['Beam Voltage'] = f"{eht} kV"
                    
                    # Aperture
                    aperture = get_val('ap_aperture_size') or get_val('dp_opt_aperture')
                    if aperture:
                        context['Aperture'] = f"{aperture}"
                        
                    # Working Distance
                    wd = get_val('ap_wd') or get_val('ap_working_distance')
                    if wd:
                        # WD is usually in meters or mm, need to check unit if possible, assuming mm or m
                        # Based on sample, it might be a float. Let's just store it as is for now.
                        context['WD'] = f"{wd}"
                        
                    # Mag
                    mag = get_val('ap_mag') or get_val('ap_magnification')
                    if mag:
                        # Fix "K X x" issue. If mag is a string and has "X", don't append "x"
                        if isinstance(mag, str) and ('X' in mag or 'x' in mag):
                            context['Mag'] = mag
                        else:
                            context['Mag'] = f"{mag} x"

                    # Date/Time
                    date_val = get_val('ap_date')
                    time_val = get_val('ap_time')
                    if date_val:
                        if time_val:
                            context['Date'] = f"{date_val} {time_val}"
                        else:
                            context['Date'] = date_val
                        
                    # Author
                    author = get_val('sv_user_name') or get_val('sv_operator')
                    if author:
                        context['Author'] = author

            # Check for ImageDescription (Tag 270) for measurements
            if 270 in page.tags:
                desc = page.tags[270].value
                if desc:
                    try:
                        # Try to parse as JSON
                        data = json.loads(desc)
                        if isinstance(data, dict):
                            if 'measurements' in data:
                                context['Measurements'] = data['measurements']
                            if 'annotations' in data:
                                context['Annotations'] = data['annotations']
                                
                            # Backfill colors for measurements if missing (for backward compatibility)
                            if 'Measurements' in context and 'Annotations' in context:
                                measurements = context['Measurements']
                                annotations = context['Annotations']
                                if len(measurements) == len(annotations):
                                    for i, m in enumerate(measurements):
                                        if 'color' not in m:
                                            m['color'] = annotations[i].get('color', '#000000')
                    except json.JSONDecodeError:
                        # Not JSON, maybe just text description
                        pass

    except Exception as e:
        print(f"Error parsing context: {e}")
    
    return context
