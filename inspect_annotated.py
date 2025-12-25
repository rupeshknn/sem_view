import tifffile
import numpy as np

def inspect_annotated(file_path):
    with tifffile.TiffFile(file_path) as tif:
        print(f"Number of pages: {len(tif.pages)}")
        for i, page in enumerate(tif.pages):
            data = page.asarray()
            print(f"Page {i}: Shape={data.shape}, Dtype={data.dtype}, Min={data.min()}, Max={data.max()}")
            if i == 1:
                # Check if page 1 has any content
                non_zero = np.count_nonzero(data)
                print(f"Page 1 Non-zero pixels: {non_zero}")

if __name__ == "__main__":
    inspect_annotated("annotaated_sample.tif")
