from enum import Enum
from typing import Optional, List, Any, Literal, Union

from pydantic import BaseModel

from dnastack.client.workbench.models import BaseListOptions
from dnastack.client.workbench.models import PaginatedResource


class Provider(str, Enum):
    aws = "AWS"
    gcp = "GCP"
    azure = "AZURE"


class AwsStorageAccountCredentials(BaseModel):
    access_key_id: Optional[str]
    secret_access_key: Optional[str]
    region: Optional[str]
    type: str = 'AWS_ACCESS_KEY'



class StorageAccount(BaseModel):
    id: Optional[str]
    namespace: Optional[str]
    name: Optional[str]
    provider: Optional[Provider]
    created_at: Optional[str]
    last_updated_at: Optional[str]
    credentials: Optional[Union[AwsStorageAccountCredentials]]

class StorageListOptions(BaseListOptions):
    provider: Optional[Provider]
    sort: Optional[str]


class StorageListResponse(PaginatedResource):
    accounts: List[StorageAccount]

    def items(self) -> List[Any]:
        return self.accounts


class Platform(BaseModel):
    id: Optional[str]
    namespace: Optional[str]
    storage_account_id: Optional[str]
    name: Optional[str]
    path: Optional[str]
    type: Optional[str]
    created_at: Optional[str]
    last_updated_at: Optional[str]


class PlatformListOptions(BaseListOptions):
    storage_account_id: Optional[str]
    sort: Optional[str]


class PlatformListResponse(PaginatedResource):
    platforms: List[Platform]

    def items(self) -> List[Any]:
        return self.platforms
