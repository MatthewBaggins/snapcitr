from dotenv import load_dotenv
import os
import typing as typ

from pyzotero import zotero

from src.bibtex import BibTeXEntry


def import_to_zotero(bibtex: BibTeXEntry) -> None:
    load_dotenv()
    z = zotero.Zotero(
        library_id=os.environ["ZOTERO_USER_ID"],
        library_type="user",
        api_key=os.environ["ZOTERO_API_KEY"],
    )

    # Map BibTeX entry types to Zotero item types
    entry_type_map = {
        "article": "journalArticle",
        "book": "book",
        "inproceedings": "conferencePaper",
        "incollection": "bookSection",
        "phdthesis": "thesis",
        "mastersthesis": "thesis",
        "techreport": "report",
        "misc": "document",
    }

    item_type = entry_type_map.get(bibtex.entry_type.lower(), "journalArticle")

    # Parse authors (simple split on "and")
    authors = []
    for author in bibtex.author.split(" and "):
        author = author.strip()
        if "," in author:
            # Last, First format
            parts = author.split(",", 1)
            authors.append(
                {
                    "creatorType": "author",
                    "lastName": parts[0].strip(),
                    "firstName": parts[1].strip(),
                }
            )
        else:
            # First Last format - split on last space
            parts = author.rsplit(" ", 1)
            if len(parts) == 2:
                authors.append(
                    {
                        "creatorType": "author",
                        "firstName": parts[0].strip(),
                        "lastName": parts[1].strip(),
                    }
                )
            else:
                authors.append(
                    {
                        "creatorType": "author",
                        "lastName": author,
                    }
                )

    # Build item
    item: dict[str, typ.Any] = {
        "itemType": item_type,
        "title": bibtex.title,
        "creators": authors,
        "date": str(bibtex.year),
    }

    # Add optional fields with correct field names per item type
    if bibtex.journal:
        item["publicationTitle"] = bibtex.journal
    if bibtex.booktitle:
        # Use correct field name based on item type
        if item_type == "conferencePaper":
            item["proceedingsTitle"] = bibtex.booktitle
        else:
            item["publicationTitle"] = bibtex.booktitle
    if bibtex.publisher:
        item["publisher"] = bibtex.publisher
    if bibtex.volume:
        item["volume"] = bibtex.volume
    if bibtex.number:
        item["issue"] = bibtex.number
    if bibtex.pages:
        item["pages"] = bibtex.pages
    if bibtex.doi:
        item["DOI"] = bibtex.doi
    if bibtex.url:
        item["url"] = bibtex.url

    result = z.create_items([item])

    # Check result
    print(f"Result: {result}")
    if result.get("successful"):
        print(f"Successfully added {len(result['successful'])} item(s)!")
    if result.get("failed"):
        print(f"Failed: {result.get('failed')}")
    if result.get("unchanged"):
        print(f"Unchanged: {result.get('unchanged')}")
