from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class FolderCreate(BaseModel):
    name: str
    parent_id: Optional[UUID] = None


class FolderResponse(BaseModel):
    id: UUID
    name: str
    parent_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class FileResponse(BaseModel):
    id: UUID
    original_name: str
    size: int
    mime_type: Optional[str]
    folder_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class FolderContents(BaseModel):
    current_folder: Optional[FolderResponse]
    breadcrumb: list[FolderResponse]
    folders: list[FolderResponse]
    files: list[FileResponse]
    storage_used: int
    storage_limit: int
