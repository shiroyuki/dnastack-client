from datetime import datetime

from pydantic import BaseModel

from typing import List, Optional, Any

from dnastack.client.workbench.models import BaseListOptions, PaginatedResource


class SampleListOptions(BaseListOptions):
    pass


class SampleFile(BaseModel):
    path: str


class Sample(BaseModel):
    id: str
    created_at: Optional[datetime]
    last_updated_at: Optional[datetime]
    files: Optional[List[SampleFile]]
    father_id: Optional[str]
    mother_id: Optional[str]


class SampleListResponse(PaginatedResource):
    samples: List[Sample]

    def items(self) -> List[Any]:
        return self.samples
