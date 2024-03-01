from pydantic import BaseModel


class WorkbenchUser(BaseModel):
    email: str
    full_name: str
    default_namespace: str
