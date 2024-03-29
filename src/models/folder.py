import sqlalchemy as sa
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import relationship
from src.models.meta import Base

from src.models.primitives.base import (
    SAUUID,
)
from src.models.primitives.folder import (
    FolderTitle,
    SAFolderTitle,
    FolderColor,
    SAFolderColor,
)

from uuid import uuid4, UUID

if TYPE_CHECKING:
    from src.models.note import Note
    from src.models.tag import Tag
    from src.models.user import User


class Folder(Base):
    __tablename__ = "folder"

    id: UUID = sa.Column(SAUUID, primary_key=True, default=lambda: uuid4())

    title: FolderTitle = sa.Column(SAFolderTitle, nullable=False)
    color: FolderColor = sa.Column(SAFolderColor, nullable=True)

    parent_id: UUID = sa.Column(SAUUID, sa.ForeignKey("folder.id"), nullable=True, index=True)
    parent: 'Folder' = relationship("Folder", foreign_keys=[parent_id], remote_side=[id], uselist=False)

    user_id: UUID = sa.Column(SAUUID, sa.ForeignKey("user.id"), nullable=False, index=True)
    user: 'User' = relationship("User", foreign_keys=[user_id])

    children_folders: List['Folder'] = relationship('Folder', back_populates="parent")

    notes: List['Note'] = relationship(
        'Note', back_populates="folder",
        primaryjoin="and_(Folder.id==Note.folder_id, Note.deleted.is_(None))",
    )

    tags: List['Tag'] = relationship(
        "Tag", secondary="folder_tag",
        primaryjoin="and_(Folder.id==FolderTag.folder_id)",
        secondaryjoin="and_(Tag.id==FolderTag.tag_id, Tag.deleted.is_(None))",
    )

    created = sa.Column(sa.DateTime, default=sa.func.now())
    updated = sa.Column(sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    deleted = sa.Column(sa.DateTime, nullable=True)


class FolderTag(Base):
    __tablename__ = "folder_tag"

    id: UUID = sa.Column(SAUUID, primary_key=True, default=lambda: uuid4())

    folder_id: UUID = sa.Column(SAUUID, sa.ForeignKey("folder.id"), nullable=False, index=True)
    folder = relationship("Folder", foreign_keys=[folder_id], overlaps="tags")

    tag_id: UUID = sa.Column(SAUUID, sa.ForeignKey("tag.id"), nullable=False, index=True)
    tag = relationship("Tag", foreign_keys=[tag_id], overlaps="tags")
