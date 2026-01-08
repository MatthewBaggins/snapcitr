from pydantic import BaseModel


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
