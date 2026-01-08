# main.py
# Entry point for the snapshot application
from pathlib import Path

from src.rectangle_selector import RectangleSelector
from src.processing import extract_text, find_citation
from src.import_to_zotero import import_to_zotero
from src.utils import get_logger

if __name__ == "__main__":
    log_file = Path(__file__).parent / "logs"
    logger = get_logger(log_file)
    logger.info("=" * 60)
    logger.info("Snapshot application started")
    logger.info("Log file: %s", log_file)

    citation_count = 0

    while True:
        logger.info("Ready for next citation")

        try:
            selector = RectangleSelector()
            selector.start_selection()

            # Check if user cancelled (pressed Escape)
            if not selector.selected:
                logger.info(
                    "User exited. Total citations processed: %d", citation_count
                )
                break

            logger.info("Selection made")
            img = selector.capture_image(strict=True)
            text = extract_text(img)
            logger.info("Extracted text (%d chars): %s...", len(text), text[:100])

            citation = find_citation(text)
            logger.info("Citation found: %s - %s", citation.entry_type, citation.title)
            citation_formatted = citation.format(with_cite_key=False)
            logger.info("Formatted citation:\n%s", citation_formatted)

            import_to_zotero(citation)
            citation_count += 1
            logger.info("Citation #%d added to Zotero successfully", citation_count)

        except Exception as e:
            logger.error("Error processing citation: %s", e, exc_info=True)

    logger.info("Snapshot application closed")
    logger.info("=" * 60)
