from functools import lru_cache
import os
import typing as typ

from openai import OpenAI
from PIL.Image import Image
from pydantic import BaseModel
import pytesseract


def extract_text(img: Image) -> str:
    text = pytesseract.image_to_string(img)
    return text


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
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


CitationFormat = typ.Literal["BibTeX"]


def find_citation(
    citation_text: str, *, format: CitationFormat = "BibTeX"
) -> BibTeXEntry:
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
