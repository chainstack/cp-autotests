"""Pydantic schemas for Node API responses."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str


class NodeListItem(BaseModel):
    """Node item in list response."""
    id: str
    name: str
    protocol: str
    network: str
    created_at: datetime
    updated_at: datetime
    status: str


class NodeListResponse(BaseModel):
    """Response for GET /v1/ui/nodes."""
    results: List[NodeListItem]
    total: int


class NodeMetadataField(BaseModel):
    """Individual metadata field."""
    name: str
    type: str
    value: str


class NodeMetadata(BaseModel):
    """Metadata section containing fields."""
    name: str
    fields: List[NodeMetadataField]


class NodeRevision(BaseModel):
    """Node revision with metadata."""
    id: str
    metadata: List[NodeMetadata]


class Node(BaseModel):
    """Full node response for GET /v1/ui/nodes/{id}."""
    id: str
    name: str
    protocol: str
    network: str
    created_at: datetime
    updated_at: datetime
    status: str
    revision: NodeRevision


class CreateNodeRequest(BaseModel):
    """Request body for POST /v1/ui/nodes."""
    preset_instance_id: str
    preset_override_values: Optional[Dict[str, Any]] = None


class CreateNodeResponse(BaseModel):
    """Response for POST /v1/ui/nodes."""
    deployment_id: str
    initial_revision_id: str
    state: str


class ScheduleDeleteNodeResponse(BaseModel):
    """Response for POST /v1/ui/nodes/{id}/schedule-delete."""
    deployment_id: str
    state: str
