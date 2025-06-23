# gui_mask_maker.py

import os
import json
import requests
import fitz  # PyMuPDF
from PyQt6 import QtWidgets, QtGui, QtCore
from mask_generator import generate_mask_pdf

CONFIG_PATH = "config.json"
DEFAULT_CONFIG = {
    "dpi": 300,
    "a4_width_mm": 210,
    "a4_height_mm": 297,
    "overlap_mm": 15,
    "marker_size": 15,
    "face_width_mm": 185,
    "face_height_mm": 215,
    "edge_thickness_mm": 35,
    "outer_scale_factor": 1.125
}

RECOMMENDED_FIELDS = {"face_width_mm", "face_height_mm", "edge_thickness_mm"}

class MaskMakerApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minecraft Papercraft Mask Generator")
        self.config = self.load_config()
        self.pdf_path = "papercraft-mask.pdf"
        self.skin_path = "skin.png"
        self.init_ui()

    def load_config(self):
        if os.path.isfile(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=2)

    def init_ui(self):
        layout = QtWidgets.QHBoxLayout(self)

        # === Left: Input Panel ===
        input_panel = QtWidgets.QVBoxLayout()

        input_panel.addWidget(QtWidgets.QLabel(""))

        # Skin source
        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setPlaceholderText("Enter Minecraft Username")
        self.file_button = QtWidgets.QPushButton("Select Local Skin (.png)")
        self.file_button.clicked.connect(self.select_skin_file)

        # Create OR label with fixed vertical size policy
        or_label = QtWidgets.QLabel("OR")
        or_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,  # Horizontal policy
            QtWidgets.QSizePolicy.Policy.Fixed  # Vertical policy (fixed height)
        )
        or_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # Center-align text

        input_panel.addWidget(self.username_input)
        input_panel.addWidget(or_label)
        input_panel.addWidget(self.file_button)

        # Config inputs
        self.inputs = {}
        for key in DEFAULT_CONFIG:
            row = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(f"{key}:")
            if key in RECOMMENDED_FIELDS:
                label.setStyleSheet("color: orange;")
                label.setToolTip("Recommended to tweak for your paper box")
            input_box = QtWidgets.QLineEdit(str(self.config.get(key, "")))
            self.inputs[key] = input_box
            row.addWidget(label)
            row.addWidget(input_box)
            input_panel.addLayout(row)

        # Run Button
        self.run_button = QtWidgets.QPushButton("Generate Mask PDF")
        self.run_button.clicked.connect(self.generate_pdf)
        input_panel.addWidget(self.run_button)

        # === Right: PDF Preview ===
        self.preview_label = QtWidgets.QLabel()
        self.preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumWidth(420)

        layout.addLayout(input_panel, 2)
        layout.addWidget(self.preview_label, 3)

    def select_skin_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Skin PNG", "", "PNG Files (*.png)")
        if path:
            self.skin_path = path
            self.username_input.setText("")  # Clear username if file is selected

    def download_skin(self, username):
        url = f"https://minecraftskins.com/skin/{username}"
        session_url = f"https://sessionserver.mojang.com/session/minecraft/profile/{self.get_uuid(username)}"
        try:
            resp = requests.get(session_url, timeout=10)
            if resp.status_code != 200:
                raise Exception("Could not get profile")
            data = resp.json()
            for prop in data.get("properties", []):
                if prop["name"] == "textures":
                    import base64, zlib
                    decoded = base64.b64decode(prop["value"]).decode()
                    if "SKIN" not in decoded:
                        raise Exception("Skin not found")
                    import json as js
                    skin_url = js.loads(decoded)["textures"]["SKIN"]["url"]
                    image = requests.get(skin_url)
                    with open("skin.png", "wb") as f:
                        f.write(image.content)
                    self.skin_path = "skin.png"
                    return
            raise Exception("Skin not found in profile")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to download skin: {e}")

    def get_uuid(self, username):
        resp = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}", timeout=10)
        if resp.status_code != 200:
            raise Exception("Invalid username")
        return resp.json()["id"]

    def generate_pdf(self):
        # Read config from inputs
        try:
            for key in self.inputs:
                val = self.inputs[key].text()
                if "." in val:
                    self.config[key] = float(val)
                else:
                    self.config[key] = int(val)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter valid numeric values.")
            return

        # Save config
        self.save_config()

        # Handle skin input
        username = self.username_input.text().strip()
        if username:
            self.download_skin(username)
        elif not os.path.isfile(self.skin_path):
            QtWidgets.QMessageBox.warning(self, "Skin Missing", "Please select or provide a valid skin.")
            return

        try:
            generate_mask_pdf(self.skin_path, self.pdf_path, self.config)
            QtWidgets.QMessageBox.information(self, "Success", f"Saved to {self.pdf_path}")
            self.show_pdf_preview(self.pdf_path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Generation Error", str(e))

    def show_pdf_preview(self, pdf_path):
        try:
            doc = fitz.open(pdf_path)
            num_pages = min(4, len(doc))  # Show up to 4 pages

            # Create a list to hold all page pixmaps
            pixmaps = []
            for i in range(num_pages):
                page = doc.load_page(i)
                pix = page.get_pixmap(dpi=100)
                img = QtGui.QImage(pix.samples, pix.width, pix.height, pix.stride, QtGui.QImage.Format.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(img)
                pixmaps.append(pixmap.scaledToWidth(200))  # Scale down to fit in grid

            # Create a combined image for 2x2 grid
            if num_pages == 1:
                combined_pixmap = pixmaps[0]
            else:
                # Determine grid size
                grid_width = 2
                grid_height = 2 if num_pages > 2 else 1

                # Calculate total size
                width = max(pix.width() for pix in pixmaps) * grid_width
                height = max(pix.height() for pix in pixmaps) * grid_height

                # Create blank pixmap
                combined_pixmap = QtGui.QPixmap(width, height)
                combined_pixmap.fill(QtCore.Qt.GlobalColor.white)

                painter = QtGui.QPainter(combined_pixmap)

                # Arrange pixmaps in grid
                for i, pixmap in enumerate(pixmaps):
                    row = i // 2
                    col = i % 2
                    x = col * 200  # 200 is our scaled width
                    y = row * pixmap.height()
                    painter.drawPixmap(x, y, pixmap)

                painter.end()

            self.preview_label.setPixmap(combined_pixmap.scaledToWidth(400))

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Preview Error", f"Could not preview PDF: {e}")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MaskMakerApp()
    window.setWindowIcon(QtGui.QIcon("assets/icon.png"))
    window.resize(960, 640)
    window.show()
    sys.exit(app.exec())
