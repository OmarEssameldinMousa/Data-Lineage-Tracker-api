from pydantic import ConfigDict, BaseModel
import uuid
from datetime import datetime

class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    created_at: datetime

class DatasetCreate(BaseModel):
    name: str

class DatasetDepthResponse(BaseModel):
    dataset: DatasetResponse
    depth: int

class LineageGraphResponse(BaseModel):
    upstream: list[DatasetResponse]
    downstream: list[DatasetResponse]