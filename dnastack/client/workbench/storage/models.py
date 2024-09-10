from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field

class CloudProvider(Enum):
    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"


class AwsAccessCredentials(BaseModel):
    type: str = Field(default="AWS_ACCESS_KEY", const=True)
    access_key_id: str
    secret_access_key: str


class Repository(BaseModel):
    namespace: Optional[str]
    id: Optional[str]
    name: Optional[str]
    bucket: str
    path: Optional[str]
    region: str
    provider: str
    etag: Optional[str]
    credentials: Optional[Union[AwsAccessCredentials]]
