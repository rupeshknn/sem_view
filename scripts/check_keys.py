import tifffile

def check_keys(file_path):
    with tifffile.TiffFile(file_path) as tif:
        page = tif.pages[0]
        if 34118 in page.tags:
            data = page.tags[34118].value
            if isinstance(data, dict):
                print("Keys in 34118:")
                for k in data.keys():
                    print(k)
                
                # Try to find pixel size
                if 'Pixel Size' in data:
                    print(f"\nPixel Size: {data['Pixel Size']}")
                if 'Image Pixel Size' in data:
                    print(f"\nImage Pixel Size: {data['Image Pixel Size']}")
                if 'Ap_Image_Pixel_Size' in data:
                     print(f"\nAp_Image_Pixel_Size: {data['Ap_Image_Pixel_Size']}")
            else:
                print(f"Tag 34118 is {type(data)}")

if __name__ == "__main__":
    check_keys("sample.tif")
