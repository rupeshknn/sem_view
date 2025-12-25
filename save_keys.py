import tifffile

def save_keys(file_path):
    with open("keys.txt", "w") as f:
        with tifffile.TiffFile(file_path) as tif:
            page = tif.pages[0]
            if 34118 in page.tags:
                data = page.tags[34118].value
                if isinstance(data, dict):
                    for k, v in data.items():
                        f.write(f"{k}: {v}\n")

if __name__ == "__main__":
    save_keys("sample.tif")
