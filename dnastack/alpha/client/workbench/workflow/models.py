from typing import Optional, List, Dict

from pydantic import BaseModel

from dnastack.client.workbench.workflow.models import WorkflowVersion


class ResolvedWorkflow(BaseModel):
    id: str
    internalId: str
    source: str
    name: str
    description: Optional[str]
    lastUpdatedAt: Optional[str]
    versionId: Optional[str]
    version: Optional[WorkflowVersion]
    authors: Optional[List[str]]
    etag: Optional[str]


class WorkflowDefaultsSelector(BaseModel):
    engine: Optional[str]
    provider: Optional[str]
    region: Optional[str]

class WorkflowDefaults(BaseModel):
    id: Optional[str]
    name: Optional[str]
    workflow_id: Optional[str]
    workflow_version_id: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    selector: Optional[WorkflowDefaultsSelector]
    values: Optional[Dict]
