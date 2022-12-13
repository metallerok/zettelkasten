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


class Note(Base):
    __tablename__ = "note"

    id = sa.Column(UUID, primary_key=True, default=lambda: str(uuid4()))

    title: NoteTitle = sa.Column(SANoteTitle, nullable=False)
    color: NoteColor = sa.Column(SANoteColor, nullable=True)

    text = sa.Column(sa.String, nullable=True)

    folder_id = sa.Column(UUID, sa.ForeignKey("folder.id"), nullable=True, index=True)
    folder: 'Folder' = relationship("Folder", foreign_keys=[folder_id], back_populates="notes")

    notes_relations: List['NoteToNoteRelation'] = relationship(
        "NoteToNoteRelation",
        foreign_keys="[NoteToNoteRelation.parent_note_id]",
    )

    created = sa.Column(sa.DateTime, default=sa.func.now())
    updated = sa.Column(sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    deleted = sa.Column(sa.DateTime, nullable=True)


class NoteToNoteRelation(Base):
    __tablename__ = "note_to_note_relation"

    id = sa.Column(UUID, primary_key=True, default=lambda: str(uuid4()))

    parent_note_id = sa.Column(UUID, sa.ForeignKey("note.id"), nullable=False, index=True)
    parent_note = relationship("Note", foreign_keys=[parent_note_id], back_populates="notes_relations")

    child_note_id = sa.Column(UUID, sa.ForeignKey("note.id"), nullable=False, index=True)
    child_note = relationship("Note", foreign_keys=[child_note_id])

    # todo: add description here
