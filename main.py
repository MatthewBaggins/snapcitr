# main.py
# Entry point for the snapshot application

from src.rectangle_selector import RectangleSelector


if __name__ == "__main__":
    print("Snapshot application initialized.")
    print("Click and drag to select the area you want to capture...")

    selector = RectangleSelector()
    selector.start_selection()
    selector.capture_and_save()
