import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from ui import StitcherApp


def resource_path(relative: str) -> Path:
    """
    Get absolute path to resource, works for dev and PyInstaller bundle.
    """
    base_path = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    return Path(base_path) / relative


def main():
    app = QApplication(sys.argv)

    # Try to load the icon
    icon_path = resource_path("blueprint_icon.ico")
    if icon_path.exists():
        app_icon = QIcon(str(icon_path))
        app.setWindowIcon(app_icon)
    else:
        app_icon = None

    window = StitcherApp()
    if app_icon is not None:
        window.setWindowIcon(app_icon)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
