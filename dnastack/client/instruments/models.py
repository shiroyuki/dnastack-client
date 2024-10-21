from typing import List, Optional, Any

from pydantic import BaseModel

from dnastack.alpha.client.workbench.storage.models import PlatformType
from dnastack.client.workbench.models import BaseListOptions, PaginatedResource


class InstrumentListOptions(BaseListOptions):
    platform_type: Optional[PlatformType]

class Instrument(BaseModel):
    id: str
    platform_type: PlatformType


class InstrumentListResponse(PaginatedResource):
    instruments: List[Instrument]

    def items(self) -> List[Any]:
        return self.instruments
