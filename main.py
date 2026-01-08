# main.py
# Entry point for the snapshot application
from src.rectangle_selector import RectangleSelector
from src.processing import extract_text, find_citation, import_to_zotero


if __name__ == "__main__":
    print("Snapshot application initialized.")
    print("Click and drag to select the area you want to capture...")

    selector = RectangleSelector()
    selector.start_selection()
    img = selector.capture_image(strict=True)
    selector.save(img)
    text = extract_text(img)
    print(f"{text = !r}")
    citation = find_citation(text)
    citation_formated = citation.format(with_cite_key=False)
    print(citation_formated)
    import_to_zotero(citation)
