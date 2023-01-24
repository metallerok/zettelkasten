from marshmallow import Schema, fields
from src.schemas.primitives.notes import (
    NoteTitleField,
    NoteColorField,
)


class NoteByIdParamsSchema(Schema):
    note_id = fields.UUID(required=True)


class NotesRelationsDumpSchema(Schema):
    child_note_id = fields.UUID(dump_only=True)
    child_note = fields.Nested("NoteDumpSchema")

    description = fields.String(dump_only=True)


class NoteDumpSchema(Schema):
    id = fields.UUID(dump_only=True)

    title = NoteTitleField(dump_only=True)
    color = NoteColorField(dump_only=True)

    text = fields.String(dump_only=True)

    folder_id = fields.UUID(dump_only=True)
    folder = fields.Nested("FolderDumpSchema")

    notes_relations = fields.Nested("NotesRelationsDumpSchema", many=True)

    created = fields.DateTime(dump_only=True)
    updated = fields.DateTime(dump_only=True)


class NoteCreationInputSchema(Schema):
    title = NoteTitleField(required=True)
    color = NoteColorField(required=False, allow_none=True)

    text = fields.String(required=False, allow_none=True)

    folder_id = fields.UUID(required=False, allow_none=True, missing=None)


class NoteUpdateSchema(Schema):
    title = NoteTitleField(required=False)
    color = NoteColorField(required=False, allow_none=True)

    text = fields.String(required=False, allow_none=True)

    folder_id = fields.UUID(required=False, allow_none=True)


class NotesCollectionParamsSchema(Schema):
    title = fields.String(required=False, allow_none=True, missing=None)
    by_folder = fields.Boolean(required=False, allow_none=False, missing=False)
    folder_id = fields.UUID(required=False, allow_none=True, missing=None)


class NoteRelationCreationParamsSchema(Schema):
    parent_note_id = fields.UUID(required=True)
    child_note_id = fields.UUID(required=True)


class NoteRelationCreationBodySchema(Schema):
    description = fields.String()


class NoteRelationRemoveParamsSchema(Schema):
    parent_note_id = fields.UUID(required=True)
    child_note_id = fields.UUID(required=True)
