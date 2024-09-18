from datetime import datetime

from pydantic import BaseModel

from typing import List, Optional

from dnastack.client.workbench.models import BaseListOptions


class SampleListOptions(BaseListOptions):
    pass


class SampleFile(BaseModel):
    path: str


class Sample(BaseModel):
    id: str

    repository_id: str

    instrument_id: str

    created_at: Optional[datetime]

    files: List[SampleFile]


class SampleListResponse(BaseModel):
    samples: List[Sample]

    next_page_token: Optional[str] = None
