from utils.metadata_parser import get_pixel_scale

def test_parser():
    scale = get_pixel_scale("sample.tif")
    print(f"Scale: {scale}")
    if scale:
        print(f"Scale in nm/px: {scale * 1e9}")

if __name__ == "__main__":
    test_parser()
