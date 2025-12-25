import tifffile

def inspect_tiff(file_path):
    with open("tags.txt", "w") as f:
        with tifffile.TiffFile(file_path) as tif:
            page = tif.pages[0]
            f.write(f"Tags for {file_path}:\n")
            for tag in page.tags:
                try:
                    val = tag.value
                    # Truncate long values
                    if isinstance(val, (bytes, str)) and len(val) > 500:
                        val = val[:500] + "..."
                    f.write(f"{tag.name} ({tag.code}): {val}\n")
                except Exception as e:
                    f.write(f"{tag.name} ({tag.code}): Error reading value - {e}\n")

if __name__ == "__main__":
    inspect_tiff("sample.tif")
