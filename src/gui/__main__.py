"""
GrabVid GUI entry point.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def main():
    from src.gui.app import GrabVidGUI
    app = GrabVidGUI()
    app.run()


if __name__ == "__main__":
    main()
