# Minecraft Papercraft Mask Generator 🎭

This tool generates a printable A4 PDF mask from a Minecraft skin, including the outer layer (hat/mask).
You can use either a Minecraft username or a local PNG file.
The app previews the final PDF of papercraft.

![App Window](assets/app_window.png)

![Final Result 1](assets/final_result_1.png)
![Final Result 2](assets/final_result_2.png)

## Features

- Input a Minecraft **username** or select a local `.png` skin
- **Live PDF preview** inside the app (up to 4 pages)
- Fully editable settings (paper size, face width, edge thickness, etc.)
- Output file saved as **`papercraft-mask.pdf`**

## Usage

1. Run `skin2mask.py` (See [Build](#build) section below)
2. Enter a Minecraft username or select a local skin
3. Adjust the settings if needed (especially orange ones)
4. Click **Generate Mask PDF**
5. The result is shown on the right and saved as `papercraft-mask.pdf`

## Configuration

| Field                | Description                                                              |
|----------------------|--------------------------------------------------------------------------|
| `face_width_mm`      | Width of the front face area in millimeters                              |
| `face_height_mm`     | Height of the front face area in millimeters                             |
| `edge_thickness_mm`  | Height of the mask sides (like the walls of a box lid)                   |
| `dpi`                | Print resolution in dots per inch                                        |
| `a4_width_mm`        | Paper width in millimeters (default A4 = 210 mm)                         |
| `a4_height_mm`       | Paper height in millimeters (default A4 = 297 mm)                        |
| `overlap_mm`         | Horizontal overlap between printed pages to help with gluing/alignment   |
| `marker_size`        | Size (in pixels) of black square alignment markers                       |
| `outer_scale_factor` | How much bigger the outer hat layer should be compared to the base layer |

## Notes

- The skin must be a **64x64** format Minecraft skin.
- You can print the generated PDF on A4 paper, cut it out, and glue it to a box or mask base.
- Use cotton pads to secure the outer layer of the mask.

## <a name="build"></a> Build

Virtual Python environment
```shell
python -m venv .venv
```
Activate on Windows:
```shell
.venv/Scripts/activate.ps1
```
Activate on Linux / macOS:
```shell
source .venv/bin/activate
```
Install dependencies:
```shell
python -m pip install -r requirements.txt
```
Run the app:
```shell
python skin2mask.py
```