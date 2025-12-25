import tifffile
import json

def dump_json(file_path):
    with tifffile.TiffFile(file_path) as tif:
        page = tif.pages[0]
        if 34118 in page.tags:
            data = page.tags[34118].value
            # Convert to simple dict
            simple_data = {}
            for k, v in data.items():
                # Handle tuples/lists
                if isinstance(v, (tuple, list)):
                    simple_data[k] = [str(x) for x in v]
                else:
                    simple_data[k] = str(v)
            
            with open("metadata_dump.json", "w") as f:
                json.dump(simple_data, f, indent=2)

if __name__ == "__main__":
    dump_json("sample.tif")
