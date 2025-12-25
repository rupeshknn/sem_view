import tifffile
import math

def find_key(file_path, target_val=3.165519e-009):
    with tifffile.TiffFile(file_path) as tif:
        page = tif.pages[0]
        if 34118 in page.tags:
            data = page.tags[34118].value
            if isinstance(data, dict):
                for k, v in data.items():
                    try:
                        if isinstance(v, (int, float)):
                            if math.isclose(v, target_val, rel_tol=1e-5):
                                print(f"Found match: {k} = {v}")
                        elif isinstance(v, str):
                            if str(target_val) in v:
                                print(f"Found match in string: {k} = {v}")
                    except:
                        pass

if __name__ == "__main__":
    find_key("sample.tif")
