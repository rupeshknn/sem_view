import tifffile
import pprint


def inspect_metadata(file_path):
    try:
        with open("meta_dump.txt", "w", encoding="utf-8") as f:
            with tifffile.TiffFile(file_path) as tif:
                page = tif.pages[0]
                f.write(f"--- Tags for {file_path} ---\n")

                if 34118 in page.tags:
                    f.write("\n--- Zeiss Metadata (34118) ---\n")
                    data = page.tags[34118].value
                    if isinstance(data, dict):
                        for k, v in sorted(data.items()):
                            f.write(f"Key: {k}\n")
                            f.write(f"  Value: {v}\n")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    inspect_metadata("docs/sample.tif")
