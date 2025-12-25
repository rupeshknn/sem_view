import tifffile

def inspect_value(file_path):
    with tifffile.TiffFile(file_path) as tif:
        page = tif.pages[0]
        data = page.tags[34118].value
        val = data.get('ap_image_pixel_size')
        if val:
            print(f"Type: {type(val)}")
            print(f"Value: {val}")

if __name__ == "__main__":
    inspect_value("sample.tif")
