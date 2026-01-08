# main.py
# Entry point for the snapshot application
from src.rectangle_selector import RectangleSelector
from src.processing import extract_text, find_citation
from src.import_to_zotero import import_to_zotero


if __name__ == "__main__":
    print("Snapshot application initialized.")
    print("Press Alt to hide/show overlay | Esc to finish")

    while True:
        print("\n--- Ready for next citation ---")

        selector = RectangleSelector()
        selector.start_selection()

        # Check if user cancelled (pressed Escape)
        if not selector.selected:
            print("Exiting...")
            break

        img = selector.capture_image(strict=True)
        text = extract_text(img)
        print(f"{text = !r}")
        citation = find_citation(text)
        print(citation.format(with_cite_key=False))
        import_to_zotero(citation)
