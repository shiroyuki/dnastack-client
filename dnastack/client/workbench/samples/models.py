from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import re

from pydantic import BaseModel, Field

from dnastack.client.workbench.models import BaseListOptions, PaginatedResource
from dnastack.client.service_registry.models import Service
from dnastack.common.json_argument_parser import JSONType


class SamplesListOptions(BaseListOptions):
    pass


class Sample(BaseModel):
    id: str
    repository_id: str
    instrument_id: str
    created_at: Optional[datetime]
    files: List[SampleFile]


class SampleFile(BaseModel):
    path: str