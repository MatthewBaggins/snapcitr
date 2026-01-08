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


def import_to_zotero() -> None:
    load_dotenv()
    z = zotero.Zotero(
        library_id=os.environ["ZOTERO_USER_ID"],
        library_type="user",
        api_key=os.environ["ZOTERO_API_KEY"],
    )

    # Test item with correct creator format
    result = z.create_items(
        [
            {
                "itemType": "journalArticle",
                "title": "XYZ XYZ XYZ",
                "creators": [
                    {
                        "creatorType": "author",
                        "firstName": "John",
                        "lastName": "Doe",
                    }
                ],
                "date": "1998",
            }
        ]
    )

    # Check result
    print(f"Result: {result}")
    if result.get("successful"):
        print(f"Successfully added {len(result['successful'])} item(s)!")
    if result.get("failed"):
        print(f"Failed: {result.get('failed')}")
    if result.get("unchanged"):
        print(f"Unchanged: {result.get('unchanged')}")
