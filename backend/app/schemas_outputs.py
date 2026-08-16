from pydantic import BaseModel
class EvidenceRow(BaseModel):
    parameter: str
    value: object | None=None
    unit: str | None=None
    source_type: str
    doi: str | None=None
    pmid: str | None=None
    title: str | None=None
    url: str | None=None
    locator: str | None=None
    quote: str | None=None
