from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QApplication,
)

from stitcher import load_images_from_folder, stitch_grid
from capture_window import capture_unreal_window_screenshot


class StitcherApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Blueprint Screenshot Capture & Stitcher")

        # How many tiles we’ve captured so far (for this folder + session)
        self.captured_count = 0

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        instructions = QLabel(
            "Workflow:\n"
            "1. Open Unreal and the Blueprint graph, set a nice zoom level.\n"
            "2. Arrange windows so Unreal is visible (this app can sit over it).\n"
            "3. Choose the screenshot folder and Unreal window title keyword.\n"
            "4. Set Columns/Rows (how many tiles you'll capture in a grid).\n"
            "5. For each tile: position the graph in Unreal, then click 'Capture next tile'.\n"
            "   The app will minimize, capture the Unreal window, then reappear.\n"
            "6. When all tiles are captured, click 'Stitch' to build the big image."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        form = QFormLayout()
        layout.addLayout(form)

        # --- Unreal window keyword ---
        self.window_keyword_edit = QLineEdit("Unreal Editor")
        form.addRow("Unreal window title keyword:", self.window_keyword_edit)

        # --- Folder selection (used for both capture & stitch) ---
        folder_layout = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.folder_browse_btn = QPushButton("Browse...")
        self.folder_browse_btn.clicked.connect(self._choose_folder)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(self.folder_browse_btn)
        form.addRow("Screenshots folder:", folder_layout)

        # --- Columns / rows ---
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 50)
        self.cols_spin.setValue(3)
        form.addRow("Columns:", self.cols_spin)

        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 50)
        self.rows_spin.setValue(3)
        form.addRow("Rows:", self.rows_spin)

        # --- Overlap (optional) ---
        self.overlap_x_spin = QSpinBox()
        self.overlap_x_spin.setRange(0, 2000)
        self.overlap_x_spin.setValue(0)
        form.addRow("Overlap X (pixels):", self.overlap_x_spin)

        self.overlap_y_spin = QSpinBox()
        self.overlap_y_spin.setRange(0, 2000)
        self.overlap_y_spin.setValue(0)
        form.addRow("Overlap Y (pixels):", self.overlap_y_spin)

        # --- Output file ---
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit("blueprint_stitched.png")
        self.output_browse_btn = QPushButton("Browse...")
        self.output_browse_btn.clicked.connect(self._choose_output_file)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(self.output_browse_btn)
        form.addRow("Output file:", output_layout)

        # --- Capture & Stitch Buttons ---
        capture_row = QHBoxLayout()
        layout.addLayout(capture_row)

        self.capture_btn = QPushButton("Capture next tile")
        self.capture_btn.clicked.connect(self._on_capture_clicked)
        capture_row.addWidget(self.capture_btn)

        self.reset_count_btn = QPushButton("Reset counter")
        self.reset_count_btn.clicked.connect(self._on_reset_counter_clicked)
        capture_row.addWidget(self.reset_count_btn)

        # Status label
        self.status_label = QLabel("Ready.")
        self.status_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.status_label)

        # Stitch / Close row
        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        self.stitch_btn = QPushButton("Stitch")
        self.stitch_btn.clicked.connect(self._on_stitch_clicked)
        btn_layout.addWidget(self.stitch_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)

    # ---------- helpers ----------

    def _choose_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select folder for screenshots",
            "",
        )
        if folder:
            self.folder_edit.setText(folder)

    def _choose_output_file(self):
        current = self.output_edit.text().strip() or "blueprint_stitched.png"
        suggested_dir = str(Path(current).resolve().parent)

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Choose output image file",
            suggested_dir,
            "PNG Images (*.png);;All Files (*)",
        )
        if filename:
            self.output_edit.setText(filename)

    # ---------- capture logic ----------

    def _on_capture_clicked(self):
        folder_text = self.folder_edit.text().strip()
        if not folder_text:
            QMessageBox.warning(self, "Missing folder", "Please select a screenshots folder.")
            return

        folder_path = Path(folder_text).resolve()
        folder_path.mkdir(parents=True, exist_ok=True)

        cols = self.cols_spin.value()
        rows = self.rows_spin.value()
        total_tiles = cols * rows

        if self.captured_count >= total_tiles:
            QMessageBox.information(
                self,
                "All tiles captured",
                f"You already captured {self.captured_count} tiles (cols*rows = {total_tiles}).\n"
                f"Reset the counter if you want to start over.",
            )
            return

        tile_index = self.captured_count + 1
        filename = f"tile_{tile_index:02d}.png"
        save_path = folder_path / filename

        window_keyword = self.window_keyword_edit.text().strip() or "Unreal Editor"

        # Tell the user what’s happening
        self.status_label.setText(
            f"Capturing tile {tile_index}/{total_tiles}... "
            "This window will minimize; make sure Unreal is behind it."
        )
        QApplication.processEvents()

        # Minimize our own window so it doesn't block Unreal
        self.showMinimized()
        QApplication.processEvents()

        try:
            capture_unreal_window_screenshot(
                window_keyword=window_keyword,
                save_path=save_path,
                delay=1.5,  # adjust if needed
            )
        except Exception as e:
            # Restore our window and show error
            self.showNormal()
            QApplication.processEvents()
            QMessageBox.critical(
                self,
                "Capture error",
                f"Could not capture Unreal window:\n{e}",
            )
            self.status_label.setText("Capture error.")
            return

        # Restore window
        self.showNormal()
        QApplication.processEvents()

        self.captured_count += 1
        self.status_label.setText(
            f"Captured {self.captured_count}/{total_tiles} tiles. "
            f"Saved: {save_path.name}"
        )

    def _on_reset_counter_clicked(self):
        self.captured_count = 0
        self.status_label.setText("Counter reset. Ready to capture.")

    # ---------- stitch logic ----------

    def _on_stitch_clicked(self):
        folder_text = self.folder_edit.text().strip()
        if not folder_text:
            QMessageBox.warning(self, "Missing folder", "Please select a screenshots folder.")
            return

        folder_path = Path(folder_text)
        if not folder_path.is_dir():
            QMessageBox.warning(self, "Invalid folder", "The selected folder does not exist.")
            return

        cols = self.cols_spin.value()
        rows = self.rows_spin.value()
        overlap_x = self.overlap_x_spin.value()
        overlap_y = self.overlap_y_spin.value()

        output_text = self.output_edit.text().strip()
        if not output_text:
            QMessageBox.warning(self, "Missing output", "Please specify an output filename.")
            return

        output_path = Path(output_text).resolve()

        try:
            self.status_label.setText("Loading images for stitching...")
            self.stitch_btn.setEnabled(False)

            images = load_images_from_folder(folder_path)
            self.status_label.setText(
                f"Loaded {len(images)} images. Stitching {cols} x {rows}..."
            )

            stitched = stitch_grid(
                images,
                cols=cols,
                rows=rows,
                overlap_x=overlap_x,
                overlap_y=overlap_y,
            )

            stitched.save(output_path)
            self.status_label.setText(f"Saved stitched image: {output_path}")

            QMessageBox.information(
                self,
                "Success",
                f"Stitched image saved to:\n{output_path}",
            )

        except Exception as e:
            self.status_label.setText("Stitch error.")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while stitching:\n{e}",
            )
        finally:
            self.stitch_btn.setEnabled(True)
