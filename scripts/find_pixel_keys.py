import tifffile

def find_pixel_keys(file_path):
    with tifffile.TiffFile(file_path) as tif:
        page = tif.pages[0]
        if 34118 in page.tags:
            data = page.tags[34118].value
            for k in data.keys():
                if "pixel" in k.lower():
                    print(f"Key: {k}, Value: {data[k]}")

if __name__ == "__main__":
    find_pixel_keys("sample.tif")
