from functools import lru_cache
import os
import typing as typ

from dotenv import load_dotenv
from openai import OpenAI
from PIL.Image import Image
from pydantic import BaseModel
import pytesseract
from pyzotero import zotero


def extract_text(img: Image) -> str:
    return pytesseract.image_to_string(img)


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    load_dotenv()
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


class BibTeXEntry(BaseModel):
    entry_type: str  # article, book, inproceedings, etc.
    cite_key: str
    author: str
    title: str
    year: int
    # Optional fields
    journal: str | None = None
    booktitle: str | None = None
    publisher: str | None = None
    volume: str | None = None
    number: str | None = None
    pages: str | None = None
    doi: str | None = None
    url: str | None = None

    def format(self, *, with_cite_key: bool = True) -> str:
        """Format this BibTeX entry into a proper BibTeX string."""
        lines = [
            f"@{self.entry_type}{{{self.cite_key+"," if with_cite_key else ""}",
            f"  author = {{{self.author}}},",
            f"  title = {{{self.title}}},",
            f"  year = {{{self.year}}},",
        ]

        # Optional fields
        if self.journal:
            lines.append(f"  journal = {{{self.journal}}},")
        if self.booktitle:
            lines.append(f"  booktitle = {{{self.booktitle}}},")
        if self.publisher:
            lines.append(f"  publisher = {{{self.publisher}}},")
        if self.volume:
            lines.append(f"  volume = {{{self.volume}}},")
        if self.number:
            lines.append(f"  number = {{{self.number}}},")
        if self.pages:
            lines.append(f"  pages = {{{self.pages}}},")
        if self.doi:
            lines.append(f"  doi = {{{self.doi}}},")
        if self.url:
            lines.append(f"  url = {{{self.url}}},")

        lines.append("}")
        return "\n".join(lines)


CitationFormat = typ.Literal["BibTeX"]


def find_citation(
    citation_text: str, *, format: CitationFormat = "BibTeX"
) -> BibTeXEntry:
    # for later improvements/generalizations
    assert format == "BibTeX", f"{format = !r}"
    client = get_openai_client()
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "Extract bibliographic information as BibTeX.",
            },
            {"role": "user", "content": f"Paper: {citation_text}"},
        ],
        response_format=BibTeXEntry,
    )
    bibtex = response.choices[0].message.parsed
    assert bibtex is not None
    return bibtex


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
