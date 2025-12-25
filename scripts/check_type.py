import tifffile

def check_type(file_path):
    with tifffile.TiffFile(file_path) as tif:
        page = tif.pages[0]
        if 34118 in page.tags:
            val = page.tags[34118].value
            print(f"Type: {type(val)}")
            print(f"Repr: {repr(val)[:200]}")

if __name__ == "__main__":
    check_type("sample.tif")
