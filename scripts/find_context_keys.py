import tifffile

def find_context_keys(file_path):
    with open("context_keys.txt", "w") as f:
        with tifffile.TiffFile(file_path) as tif:
            page = tif.pages[0]
            if 34118 in page.tags:
                data = page.tags[34118].value
                if isinstance(data, dict):
                    f.write("--- Searching Keys ---\n")
                    keywords = ['volt', 'kv', 'aperture', 'working', 'dist', 'wd', 'author', 'operator', 'user', 'tool', 'serial', 'name', 'mag']
                    for k, v in data.items():
                        k_lower = k.lower()
                        if any(kw in k_lower for kw in keywords):
                            f.write(f"{k}: {v}\n")

if __name__ == "__main__":
    find_context_keys("sample.tif")
