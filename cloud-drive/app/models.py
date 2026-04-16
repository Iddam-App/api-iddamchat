import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey, Index, TypeDecorator
from sqlalchemy.orm import relationship
from app.database import Base
from app.config import DATABASE_URL


# Use native PostgreSQL UUID when available, fall back to String for SQLite
if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID
    UUIDType = PG_UUID(as_uuid=True)
else:
    class UUIDString(TypeDecorator):
        impl = String(36)
        cache_ok = True

        def process_bind_param(self, value, dialect):
            if value is not None:
                return str(value)
            return value

        def process_result_value(self, value, dialect):
            if value is not None:
                return uuid.UUID(value) if not isinstance(value, uuid.UUID) else value
            return value

    UUIDType = UUIDString()


class User(Base):
    __tablename__ = "users"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    files = relationship("File", back_populates="owner", cascade="all, delete-orphan")
    folders = relationship("Folder", back_populates="owner", cascade="all, delete-orphan")


class Folder(Base):
    __tablename__ = "folders"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    parent_id = Column(UUIDType, ForeignKey("folders.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="folders")
    children = relationship("Folder", backref="parent", remote_side=[id], cascade="all, delete-orphan",
                            single_parent=True)
    files = relationship("File", back_populates="folder", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_folders_user_parent", "user_id", "parent_id"),
    )


class File(Base):
    __tablename__ = "files"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    original_name = Column(String(500), nullable=False)
    r2_key = Column(String(1000), nullable=False, unique=True)
    size = Column(BigInteger, nullable=False)
    mime_type = Column(String(255), nullable=True)
    folder_id = Column(UUIDType, ForeignKey("folders.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="files")
    folder = relationship("Folder", back_populates="files")

    __table_args__ = (
        Index("ix_files_user_folder", "user_id", "folder_id"),
    )
