# SEM Viewer

A Python application for viewing and analyzing Scanning Electron Microscope (SEM) images.

## Features
- **View SEM Images**: Supports TIFF format with metadata parsing.
- **Measurements**:
    - **Distance**: Measure lengths using line tools.
    - **Area**: Calculate areas using polygon tools.
    - **Real-world Units**: Automatically detects pixel scale from metadata to display results in nm, µm, or mm.
- **Standalone**: Runs as a single executable on Windows.

## Controls
- **Left Click**: Measure (Line) or Add Vertex (Polygon).
- **Right Click**: Pan the image.
- **Wheel**: Zoom in/out.

## Example Output
![Annotated Sample](Screen.png)
