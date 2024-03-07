from abc import ABC
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from pydantic import Field, BaseModel


class BaseItemInfo(BaseModel, ABC):
    """ Base Simplified Library Item

        Based on https://github.com/DNAstack/indexing-service/blob/main/src/main/java/com/dnastack/indexingservice/library/LibraryItem.java.
    """
    id: str
    name: str
    type: str
    size: int
    size_unit: str
    item_updated_time: datetime


class TableInfo(BaseItemInfo):
    """ Simplified Library Item """
    json_schema: Dict[str, Any]


class BlobInfo(BaseItemInfo):
    """ Simplified Library Item """
    checksums: List[Dict[str, str]] = Field(default_factory=list)


class ItemType(str, Enum):
    BLOB = 'blob'
    TABLE = 'table'
