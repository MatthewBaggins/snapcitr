from PIL.Image import Image
import pytesseract

from src.bibtex import BibTeXEntry
from src.utils import get_openai_client


def extract_text(img: Image) -> str:
    return pytesseract.image_to_string(img)


def find_citation(citation_text: str) -> BibTeXEntry:
    # for later improvements/generalizations
    client = get_openai_client()
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": """Extract bibliographic information as BibTeX.
                
Extract ALL available fields from the citation, including:
- entry_type: one of article, book, booklet, conference, inbook, incollection, inproceedings, manual, mastersthesis, misc, phdthesis, proceedings, techreport, unpublished
- cite_key: generate a sensible citation key (e.g., authorYear or authorTitleYear)
- author, editor, title, year
- journal, booktitle, publisher, school, institution, organization
- volume, number, pages, chapter, series, edition
- doi, url, isbn, issn
- address, month, note, howpublished, type_field (for thesis/report type)
- abstract, keywords

Only include fields that are present or can be inferred from the citation text.""",
            },
            {"role": "user", "content": f"Paper: {citation_text}"},
        ],
        response_format=BibTeXEntry,
    )
    bibtex = response.choices[0].message.parsed
    assert bibtex is not None
    return bibtex
