import tifffile

def check_specific_key(file_path):
    with tifffile.TiffFile(file_path) as tif:
        page = tif.pages[0]
        data = page.tags[34118].value
        key = 'ap_image_pixel_size'
        if key in data:
            print(f"{key}: {data[key]}")
        else:
            print(f"{key} not found")
            
        key2 = 'dp_pixel_size'
        if key2 in data:
            print(f"{key2}: {data[key2]}")

if __name__ == "__main__":
    check_specific_key("sample.tif")
