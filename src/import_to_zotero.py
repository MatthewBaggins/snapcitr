import os
import typing as typ

from dotenv import load_dotenv
from pyzotero import zotero

from src.bibtex import BibTeXEntry

# Map BibTeX entry types to Zotero item types (all 14 types)
ENTRY_TYPE_MAP: dict[str, str] = {
    "article": "journalArticle",
    "book": "book",
    "booklet": "document",
    "conference": "conferencePaper",
    "inbook": "bookSection",
    "incollection": "bookSection",
    "inproceedings": "conferencePaper",
    "manual": "report",
    "mastersthesis": "thesis",
    "misc": "document",
    "phdthesis": "thesis",
    "proceedings": "book",
    "techreport": "report",
    "unpublished": "manuscript",
}


def import_to_zotero(bibtex: BibTeXEntry) -> None:
    load_dotenv()
    z = zotero.Zotero(
        library_id=os.environ["ZOTERO_USER_ID"],
        library_type="user",
        api_key=os.environ["ZOTERO_API_KEY"],
    )

    item_type = ENTRY_TYPE_MAP.get(bibtex.entry_type.lower(), "journalArticle")

    # Parse creators (authors and editors)
    creators = []

    def parse_person(name: str, creator_type: str) -> dict[str, str]:
        name = name.strip()
        if "," in name:
            # Last, First format
            assert name.count(",") == 1, f"{name = !r} ({name.count(',')}>1 commas)"
            last_name, first_name = name.split(",", 1)
            return {
                "creatorType": creator_type,
                "lastName": last_name,
                "firstName": first_name,
            }
        else:
            # First Last format - split on last space
            parts = name.rsplit(" ", 1)
            if len(parts) == 2:
                return {
                    "creatorType": creator_type,
                    "firstName": parts[0].strip(),
                    "lastName": parts[1].strip(),
                }
            else:
                return {
                    "creatorType": creator_type,
                    "lastName": name,
                }

    if bibtex.author:
        for author in bibtex.author.split(" and "):
            creators.append(parse_person(author, "author"))

    if bibtex.editor:
        for editor in bibtex.editor.split(" and "):
            creators.append(parse_person(editor, "editor"))

    # Build item
    item: dict[str, typ.Any] = {
        "itemType": item_type,
        "creators": creators,
    }

    if bibtex.title:
        item["title"] = bibtex.title
    if bibtex.year:
        item["date"] = str(bibtex.year)
        if bibtex.month:
            item["date"] = f"{bibtex.month} {bibtex.year}"

    # Publication context fields
    if bibtex.journal:
        item["publicationTitle"] = bibtex.journal
    if bibtex.booktitle:
        if item_type == "conferencePaper":
            item["proceedingsTitle"] = bibtex.booktitle
        else:
            item["publicationTitle"] = bibtex.booktitle
    if bibtex.publisher:
        item["publisher"] = bibtex.publisher
    if bibtex.school:
        item["university"] = bibtex.school
    if bibtex.institution:
        item["institution"] = bibtex.institution

    # Location/numbering
    if bibtex.volume:
        item["volume"] = bibtex.volume
    if bibtex.number:
        if item_type == "report":
            item["reportNumber"] = bibtex.number
        else:
            item["issue"] = bibtex.number
    if bibtex.pages:
        item["pages"] = bibtex.pages
    if bibtex.series:
        item["series"] = bibtex.series
    if bibtex.edition:
        item["edition"] = bibtex.edition
    if bibtex.address:
        item["place"] = bibtex.address

    # Identifiers
    if bibtex.doi:
        item["DOI"] = bibtex.doi
    if bibtex.url:
        item["url"] = bibtex.url
    if bibtex.isbn:
        item["ISBN"] = bibtex.isbn
    if bibtex.issn:
        item["ISSN"] = bibtex.issn

    # Thesis/report type
    if bibtex.type_field:
        if item_type == "thesis":
            item["thesisType"] = bibtex.type_field
        elif item_type == "report":
            item["reportType"] = bibtex.type_field
    elif item_type == "thesis":
        # Default thesis types based on entry_type
        if bibtex.entry_type.lower() == "phdthesis":
            item["thesisType"] = "PhD thesis"
        elif bibtex.entry_type.lower() == "mastersthesis":
            item["thesisType"] = "Master's thesis"

    # Other fields → extra
    extra_parts = []
    if bibtex.chapter:
        extra_parts.append(f"Chapter Number: {bibtex.chapter}")
    if bibtex.note:
        extra_parts.append(bibtex.note)
    if bibtex.howpublished:
        extra_parts.append(f"Published via: {bibtex.howpublished}")
    if bibtex.organization:
        extra_parts.append(f"Organization: {bibtex.organization}")
    if extra_parts:
        item["extra"] = "\n".join(extra_parts)

    # Abstract
    if bibtex.abstract:
        item["abstractNote"] = bibtex.abstract

    # Keywords → tags
    if bibtex.keywords:
        item["tags"] = [{"tag": kw.strip()} for kw in bibtex.keywords.split(",")]

    result = z.create_items([item])

    # Check result
    print(f"Result: {result}")
    if result.get("successful"):
        print(f"Successfully added {len(result['successful'])} item(s)!")
    if result.get("failed"):
        print(f"Failed: {result.get('failed')}")
    if result.get("unchanged"):
        print(f"Unchanged: {result.get('unchanged')}")
