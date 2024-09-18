from enum import Enum
from typing import Optional, List, Any, Literal, Union

from pydantic import BaseModel

class Provider(str, Enum):
    aws = "aws"
    gcp = "gcp"
    azure = "azure"


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

