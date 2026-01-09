from __future__ import annotations

import typing as typ

from pydantic import BaseModel, model_validator


# All 14 standard BibTeX entry types
BibTeXEntryType = typ.Literal[
    "article",
    "book",
    "booklet",
    "conference",
    "inbook",
    "incollection",
    "inproceedings",
    "manual",
    "mastersthesis",
    "misc",
    "phdthesis",
    "proceedings",
    "techreport",
    "unpublished",
]

# Required fields per entry type
# Note: Some types require author OR editor - handled in validator
REQUIRED_FIELDS: dict[str, list[str]] = {
    "article": ["author", "title", "journal", "year"],
    "book": ["title", "publisher", "year"],  # author OR editor - special case
    "booklet": ["title"],
    "conference": ["author", "title", "booktitle", "year"],
    "inbook": ["title", "publisher", "year"],  # author OR editor, chapter OR pages
    "incollection": ["author", "title", "booktitle", "publisher", "year"],
    "inproceedings": ["author", "title", "booktitle", "year"],
    "manual": ["title"],
    "mastersthesis": ["author", "title", "school", "year"],
    "misc": [],
    "phdthesis": ["author", "title", "school", "year"],
    "proceedings": ["title", "year"],
    "techreport": ["author", "title", "institution", "year"],
    "unpublished": ["author", "title", "note"],
}

# Types that require author OR editor (not both required)
AUTHOR_OR_EDITOR_TYPES = {"book", "inbook", "proceedings"}


class BibTeXEntry(BaseModel):
    entry_type: BibTeXEntryType
    cite_key: str

    # Common fields (optional by default - validation per entry_type)
    author: str | None = None
    editor: str | None = None
    title: str | None = None
    year: int | None = None

    # Publication context
    journal: str | None = None
    booktitle: str | None = None
    publisher: str | None = None
    school: str | None = None  # For theses
    institution: str | None = None  # For techreport
    organization: str | None = None

    # Location/numbering
    volume: str | None = None
    number: str | None = None
    pages: str | None = None
    chapter: str | None = None
    series: str | None = None
    edition: str | None = None

    # Identifiers
    doi: str | None = None
    url: str | None = None
    isbn: str | None = None
    issn: str | None = None

    # Other
    address: str | None = None
    month: str | None = None
    note: str | None = None
    howpublished: str | None = None
    type: str | None = None
    abstract: str | None = None
    keywords: str | None = None

    @model_validator(mode="after")
    def validate_required_fields(self) -> BibTeXEntry:
        entry_type = self.entry_type.lower()
        required = REQUIRED_FIELDS.get(entry_type, [])
        missing = []

        for field in required:
            if getattr(self, field, None) is None:
                missing.append(field)

        # Special case: author OR editor for certain types
        if entry_type in AUTHOR_OR_EDITOR_TYPES:
            if "author" in missing and self.editor is not None:
                missing.remove("author")
            elif self.author is None and self.editor is None:
                missing.append("author or editor")

        if missing:
            raise ValueError(f"'{entry_type}' requires: {missing}")
        return self

    def format(self, *, with_cite_key: bool = True) -> str:
        """Format this BibTeX entry into a proper BibTeX string."""
        lines = [
            f"@{self.entry_type}{{{self.cite_key + ',' if with_cite_key else ''}",
        ]

        schema = BibTeXEntry.model_json_schema()
        for p in schema["properties"]:
            if p not in schema["required"] and getattr(self, p) is not None:
                lines.append(f"  {p} = {{{getattr(self, p)}}},")

        lines.append("}")
        return "\n".join(lines)
