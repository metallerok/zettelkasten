import sqlalchemy as sa
from typing import TYPE_CHECKING, List
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.models.meta import Base

from src.models.primitives.note import (
    NoteTitle,
    SANoteTitle,
    NoteColor,
    SANoteColor,
)

from uuid import uuid4

if TYPE_CHECKING:
    from src.models.folder import Folder
    from src.models.tag import Tag
    from src.models.user import User


class Note(Base):
    __tablename__ = "note"

    id = sa.Column(UUID, primary_key=True, default=lambda: str(uuid4()))

    title: NoteTitle = sa.Column(SANoteTitle, nullable=False)
    color: NoteColor = sa.Column(SANoteColor, nullable=True)

    text = sa.Column(sa.String, nullable=True)

    folder_id = sa.Column(UUID, sa.ForeignKey("folder.id"), nullable=True, index=True)
    folder: 'Folder' = relationship("Folder", foreign_keys=[folder_id], back_populates="notes")

    user_id = sa.Column(UUID, sa.ForeignKey("user.id"), nullable=False, index=True)
    user: 'User' = relationship("User", foreign_keys=[user_id])

    notes_relations: List['NoteToNoteRelation'] = relationship(
        "NoteToNoteRelation",
        foreign_keys="[NoteToNoteRelation.parent_note_id]",
        cascade="all, delete-orphan"
    )

    tags: List['Tag'] = relationship(
        "Tag", secondary="note_tag",
        primaryjoin="and_(Note.id==NoteTag.note_id)",
        secondaryjoin="and_(Tag.id==NoteTag.tag_id, Tag.deleted.is_(None))",
    )

    created = sa.Column(sa.DateTime, default=sa.func.now())
    updated = sa.Column(sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    deleted = sa.Column(sa.DateTime, nullable=True)


class NoteToNoteRelation(Base):
    __tablename__ = "note_to_note_relation"

    id = sa.Column(UUID, primary_key=True, default=lambda: str(uuid4()))

    parent_note_id = sa.Column(UUID, sa.ForeignKey("note.id"), nullable=False, index=True)
    parent_note = relationship(
        "Note", foreign_keys=[parent_note_id], back_populates="notes_relations"
    )

    child_note_id = sa.Column(UUID, sa.ForeignKey("note.id"), nullable=False, index=True)
    child_note = relationship("Note", foreign_keys=[child_note_id])

    description = sa.Column(sa.String, nullable=True)


class NoteTag(Base):
    __tablename__ = "note_tag"

    id = sa.Column(UUID, primary_key=True, default=lambda: str(uuid4()))

    note_id = sa.Column(UUID, sa.ForeignKey("note.id"), nullable=False, index=True)
    note = relationship("Note", foreign_keys=[note_id], overlaps="tags")

    tag_id = sa.Column(UUID, sa.ForeignKey("tag.id"), nullable=False, index=True)
    tag = relationship("Tag", foreign_keys=[tag_id], overlaps="tags")
