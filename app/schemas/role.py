from pydantic import BaseModel
from typing import Dict, Any

class RoleBase(BaseModel):
    name: str
    label: str
    permissions: Dict[str, Any]

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: str | None = None
    label: str | None = None
    permissions: Dict[str, Any] | None = None

class RoleOut(RoleBase):
    id: int

    class Config:
        from_attributes = True
