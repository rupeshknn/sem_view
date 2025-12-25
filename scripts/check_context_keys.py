import tifffile

def check_context_keys(file_path):
    with tifffile.TiffFile(file_path) as tif:
        page = tif.pages[0]
        if 34118 in page.tags:
            data = page.tags[34118].value
            
            keys_to_check = [
                'ap_mag', 'ap_magnification', 
                'ap_wd', 'ap_working_distance',
                'ap_eht', 'ap_voltage', 'ap_highvoltage',
                'sv_user_name', 'sv_operator',
                'sv_serial_number', 'sv_instrument_id',
                'ap_aperture_size', 'ap_aperture'
            ]
            
            print("--- Checking Specific Keys ---")
            for k in keys_to_check:
                if k in data:
                    print(f"{k}: {data[k]}")
                else:
                    # Try partial match
                    for dk in data.keys():
                        if k in dk:
                            print(f"Partial match for {k}: {dk} = {data[dk]}")
                            break

if __name__ == "__main__":
    check_context_keys("sample.tif")
