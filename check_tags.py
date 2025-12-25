import tifffile

def check_tags(file_path):
    with tifffile.TiffFile(file_path) as tif:
        page = tif.pages[0]
        
        # Check ImageDescription
        if 270 in page.tags:
            print("Tag 270 (ImageDescription):")
            print(page.tags[270].value)
        else:
            print("Tag 270 not found.")

        # Check 34118
        if 34118 in page.tags:
            print("\nTag 34118:")
            val = page.tags[34118].value
            print(val)

if __name__ == "__main__":
    check_tags("sample.tif")
