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
                "content": "Extract bibliographic information as BibTeX.",
            },
            {"role": "user", "content": f"Paper: {citation_text}"},
        ],
        response_format=BibTeXEntry,
    )
    bibtex = response.choices[0].message.parsed
    assert bibtex is not None
    return bibtex
