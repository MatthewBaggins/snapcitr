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
    type_field: str | None = None  # 'type' in BibTeX (e.g., "PhD dissertation")
    abstract: str | None = None
    keywords: str | None = None

    @model_validator(mode="after")
    def validate_required_fields(self) -> "BibTeXEntry":
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

        # Add non-None fields
        if self.author:
            lines.append(f"  author = {{{self.author}}},")
        if self.editor:
            lines.append(f"  editor = {{{self.editor}}},")
        if self.title:
            lines.append(f"  title = {{{self.title}}},")
        if self.year:
            lines.append(f"  year = {{{self.year}}},")
        if self.journal:
            lines.append(f"  journal = {{{self.journal}}},")
        if self.booktitle:
            lines.append(f"  booktitle = {{{self.booktitle}}},")
        if self.publisher:
            lines.append(f"  publisher = {{{self.publisher}}},")
        if self.school:
            lines.append(f"  school = {{{self.school}}},")
        if self.institution:
            lines.append(f"  institution = {{{self.institution}}},")
        if self.organization:
            lines.append(f"  organization = {{{self.organization}}},")
        if self.volume:
            lines.append(f"  volume = {{{self.volume}}},")
        if self.number:
            lines.append(f"  number = {{{self.number}}},")
        if self.pages:
            lines.append(f"  pages = {{{self.pages}}},")
        if self.chapter:
            lines.append(f"  chapter = {{{self.chapter}}},")
        if self.series:
            lines.append(f"  series = {{{self.series}}},")
        if self.edition:
            lines.append(f"  edition = {{{self.edition}}},")
        if self.doi:
            lines.append(f"  doi = {{{self.doi}}},")
        if self.url:
            lines.append(f"  url = {{{self.url}}},")
        if self.isbn:
            lines.append(f"  isbn = {{{self.isbn}}},")
        if self.issn:
            lines.append(f"  issn = {{{self.issn}}},")
        if self.address:
            lines.append(f"  address = {{{self.address}}},")
        if self.month:
            lines.append(f"  month = {{{self.month}}},")
        if self.note:
            lines.append(f"  note = {{{self.note}}},")
        if self.howpublished:
            lines.append(f"  howpublished = {{{self.howpublished}}},")
        if self.type_field:
            lines.append(f"  type = {{{self.type_field}}},")
        if self.abstract:
            lines.append(f"  abstract = {{{self.abstract}}},")
        if self.keywords:
            lines.append(f"  keywords = {{{self.keywords}}},")

        lines.append("}")
        return "\n".join(lines)
